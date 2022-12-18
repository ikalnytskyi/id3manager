import argparse
import mimetypes
import os
import re
import subprocess
import sys
import tempfile
import typing as t

import mutagen.id3 as id3
import mutagen.mp3 as mp3

EDITOR = os.environ.get("EDITOR", "vi")
ID3Frame = id3.Frame


class ID3SourceFrameOrder(id3.ID3):
    """The ID3 class that preserves frame order.

    Mutagen sorts frames according to its internal idea of what best practices
    are. In most cases it's okay and causes no issues but there are buggy
    software out there. For instance, Apple Podcasts is unable to render audio
    chapters if their frames are out-of-order (i.e. not sorted by start_time).

    Instead of coming up with *smart* sorting solution let's start with the
    most simple solution: the order of frames is preserved. Which means it'd be
    up to a user to add frames in proper order.

    See https://github.com/quodlibet/mutagen/issues/506
    """

    def _write(self, config):
        from mutagen.id3._tags import save_frame

        framedata = [save_frame(f, config=config) for f in self.values()]
        return bytearray().join(framedata)


def parse_metadata(fileobj, audio_len=None) -> t.List[ID3Frame]:
    """Parse textual representation of metadata."""

    metadata_txt = fileobj.read()
    frames_txt, chapters_txt = re.split(r"\n{2,}", metadata_txt, maxsplit=1)

    frames = []
    frames.extend(parse_metadata_frames(frames_txt))
    frames.extend(parse_metadata_chapters(chapters_txt, audio_len=audio_len))
    return frames


def parse_metadata_frames(frames_txt: str) -> t.List[ID3Frame]:
    """Parse textual representation of metadata frames."""

    parts = frames_txt.splitlines()
    parts = [line.split("=", maxsplit=1) for line in parts]
    parts = {k.strip(): v.strip() for k, v in parts}

    frames = []
    for frame, value in parts.items():
        frame_cls = id3.Frames[frame]
        if issubclass(frame_cls, id3.TextFrame):
            frame = frame_cls(text=[value])
        elif issubclass(frame_cls, id3.UrlFrame):
            frame = frame_cls(url=value)
        elif frame_cls is id3.APIC:
            picture_parts = value.split(maxsplit=1)
            picture_type, picture = picture_parts
            picture_type = int(picture_type.split(":")[1])

            if picture.startswith("http"):
                mime = "-->"
                picture = picture.encode("utf-8")
            elif picture.startswith("file:"):
                mime = mimetypes.guess_type(picture)[0]
                picture = open(picture.lstrip("file:"), "rb").read()

            # APIC = type:3 @cover-front.png
            frame = frame_cls(
                encoding=id3.Encoding.UTF16,
                mime=mime,
                desc="cover",
                type=id3.PictureType(picture_type),
                data=picture,
            )
        else:
            raise ValueError(f"{frame}: unsupported frame")
        frames.append(frame)
    return frames


def parse_metadata_chapters(chapters_txt, audio_len) -> t.List[ID3Frame]:
    """Parse textual representation of metadata chapters."""

    parts = chapters_txt.splitlines()
    parts = [line.split(maxsplit=1) for line in parts]
    parts = [(parse_timestamp_to_ms(ts), text) for ts, text in parts]

    frames = []

    for idx, (timestamp, text) in enumerate(parts[:-1]):
        frames.append(
            id3.CHAP(
                element_id=f"chapter#{idx}",
                start_time=sec_to_ms(timestamp),
                end_time=sec_to_ms(parts[idx + 1][0]),
                sub_frames=[id3.TIT2(text=[text])],
            )
        )
    frames.append(
        id3.CHAP(
            element_id=f"chapter#{len(parts) - 1}",
            start_time=sec_to_ms(parts[-1][0]),
            end_time=sec_to_ms(audio_len),
            sub_frames=[id3.TIT2(text=[parts[-1][1]])],
        )
    )
    frames.append(
        id3.CTOC(
            element_id="toc",
            flags=id3.CTOCFlags.TOP_LEVEL | id3.CTOCFlags.ORDERED,
            child_element_ids=[frame.element_id for frame in frames],
            sub_frames=[id3.TIT2(text=["Розділи"])],
        )
    )
    return frames


def parse_timestamp_to_ms(timestamp: str, sep: str = ":") -> float:
    parts = [float(part) for part in timestamp.split(sep)]
    parts = [0] * (3 - len(parts)) + parts
    hrs, min, sec = parts
    return hrs * 60 * 60 + min * 60 + sec


def ms_to_human_time(ms: int) -> str:
    hrs = int(ms / (60 * 60 * 1000))
    ms -= hrs * 60 * 60 * 1000

    min = int(ms / (60 * 1000))
    ms -= min * 60 * 1000

    sec = int(ms / 1000)
    ms -= sec * 1000

    hhmmss = f"{hrs:02}:{min:02}:{sec:02}"
    if ms:
        hhmmss = f"{hhmmss}.{ms:03}"
    return hhmmss


def sec_to_ms(sec: float):
    return int(sec * 1000)


def get_subcommand_entrypoint(args, file=sys.stdout):
    audio_mp3 = mp3.MP3(args.audio, ID3=ID3SourceFrameOrder)
    if audio_mp3.tags is None:
        return

    frames = [
        frame
        for frame in audio_mp3.tags.values()
        if frame.FrameID not in {"CHAP", "CTOC"}
    ]
    chapters = [frame for frame in audio_mp3.tags.values() if frame.FrameID in {"CHAP"}]

    for frame in frames:
        if isinstance(frame, id3.TextFrame):
            value = frame.text[0]
        elif isinstance(frame, id3.UrlFrame):
            value = frame.url
        else:
            raise ValueError(f"{frame.FrameID}: unsupported frame")
        print(frame.FrameID, "=", value, file=file)

    if not chapters:
        return
    print(file=file)

    for chapter in chapters:
        text = chapter.sub_frames["TIT2"].text[0]
        print(ms_to_human_time(chapter.start_time), text, file=file)


def set_subcommand_entrypoint(args, file=sys.stdin):
    audio_mp3 = mp3.MP3(args.audio, ID3=ID3SourceFrameOrder)
    frames = parse_metadata(file or args.metadata, audio_len=audio_mp3.info.length)

    if audio_mp3.tags is None:
        audio_mp3.add_tags(ID3=ID3SourceFrameOrder)
    audio_mp3.tags.delete(args.audio)

    for frame in frames:
        audio_mp3.tags.add(frame)
    audio_mp3.save(args.audio)


def edit_subcommand_entrypoint(args):
    with tempfile.NamedTemporaryFile(mode="w+t") as fp:
        get_subcommand_entrypoint(args, file=fp)
        fp.flush()

        process = subprocess.Popen([EDITOR, fp.name])
        process.wait()

        fp.seek(0)
        set_subcommand_entrypoint(args, file=fp)


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="The ID3 metadata manager that you have been missing.",
    )
    subparsers = parser.add_subparsers(required=True, title="subcommands")

    parser_get = subparsers.add_parser("get", help="get ID3 metadata")
    parser_get.add_argument(
        "audio",
        metavar="audio.mp3",
        type=argparse.FileType("rb"),
        help="the aduio file to get metadata from",
    )
    parser_get.set_defaults(subcommand=get_subcommand_entrypoint)

    parser_set = subparsers.add_parser("set", help="set ID3 metadata")
    parser_set.add_argument(
        "audio",
        metavar="audio.mp3",
        type=argparse.FileType("rb+"),
        help="the audio file to set metadata in",
    )
    parser_set.set_defaults(subcommand=set_subcommand_entrypoint)

    parser_edit = subparsers.add_parser("edit", help="interactively edit ID3 metadata")
    parser_edit.add_argument(
        "audio",
        metavar="audio.mp3",
        type=argparse.FileType("rb+"),
        help="the audio file to edit metadata in",
    )
    parser_edit.set_defaults(subcommand=edit_subcommand_entrypoint)

    args = parser.parse_args(argv)
    return args.subcommand(args)


if __name__ == "__main__":
    # TODO:
    #  * URL frames must be "bytes"
    #    * punyencoding or percent encoding?
    #  * Add support for PairedTextFrame
    #  * Add support for BinaryFrame
    #  * Add support for ETCO
    #  * Add support for MLLT
    #  * Add support for SYTC
    #  * Add support for USLT, SYLT
    main()
