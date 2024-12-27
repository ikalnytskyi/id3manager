import base64
import re
import typing as t
import urllib.parse as urlparse

import mutagen.id3 as id3

from .. import utils
from .abc import MetadataFormatter


class TextMetadataFormatter(MetadataFormatter):
    @property
    def name(self):
        return "text"

    def read(self, fileobj: t.IO) -> t.List[id3.Frame]:
        metadata_txt = fileobj.read()
        frames_txt, chapters_txt = re.split(r"\n{2,}", metadata_txt, maxsplit=1)

        frames = []
        frames.extend(parse_text_frames(frames_txt))
        frames.extend(parse_text_chapters(chapters_txt))
        return frames

    def write(self, fileobj: t.IO, frames: t.List[id3.Frame]) -> None:
        frames_wo_chapters = [
            frame for frame in frames if frame.FrameID not in {"CHAP", "CTOC"}
        ]
        chapters = [frame for frame in frames if frame.FrameID in {"CHAP"}]

        for frame in frames_wo_chapters:
            if isinstance(frame, id3.TextFrame):
                value = frame.text[0]
            elif isinstance(frame, id3.UrlFrame):
                value = frame.url
            elif isinstance(frame, id3.APIC):
                value = unparse_apic(frame)
            else:
                raise ValueError(f"{frame.FrameID}: unsupported frame")
            print(frame.FrameID, "=", value, file=fileobj)

        if not chapters:
            return
        print(file=fileobj)

        for chapter in chapters:
            text = chapter.sub_frames["TIT2"].text[0]
            print(utils.ms_to_human_time(chapter.start_time), text, file=fileobj)


def parse_text_frames(frames_txt: str) -> t.List[id3.Frame]:
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
        elif issubclass(frame_cls, id3.APIC):
            frame = parse_apic(value)
        else:
            raise ValueError(f"{frame}: unsupported frame")
        frames.append(frame)
    return frames


def parse_text_chapters(chapters_txt) -> t.List[id3.Frame]:
    """Parse textual representation of metadata chapters."""

    parts = chapters_txt.splitlines()
    parts = [line.split(maxsplit=1) for line in parts]
    parts = [(utils.parse_timestamp_to_ms(ts), text) for ts, text in parts]

    return [
        id3.CHAP(start_time=start_time, sub_frames=[id3.TIT2(text=text)])
        for (start_time, text) in parts
    ]


def _parse_picture_type(value: str) -> t.Tuple[str, id3.PictureType]:
    # Expected format: "URL[ picture_type]".

    url, *params = value.split(" ", maxsplit=1)
    type_name_or_value = params[0] if params else None

    return url, utils.get_apic_picture_type(type_name_or_value)


def _parse_data_url(path: str) -> t.Tuple[str, t.Optional[str]]:
    # Expected format: "[mime-type][;base64],<data>".

    try:
        metadata, data = path.split(",", maxsplit=1)
    except ValueError:
        raise ValueError(f"Invalid data URL value: `data:{path}`")

    try:
        mime_type, encoding = metadata.split(";", maxsplit=1)
    except ValueError:
        mime_type = metadata or None
        encoding = None

    if encoding and encoding != "base64":
        raise ValueError(f"Unsupported encoding: `{encoding}`")

    return data, mime_type


def parse_apic(value: str) -> id3.APIC:
    url, picture_type = _parse_picture_type(value)

    result = urlparse.urlparse(url)
    if result.scheme == "data":
        # Data URL (https://developer.mozilla.org/en-US/docs/Web/URI/Schemes/data).
        # Image data is embedded in the URL as a base64 value and stored alongside
        # the MIME type.
        #
        # E.g. "data:image/png;base64,SGVsbG8sIFdvcmxkIQ==" or "data:,SGVsbG8sIFdvcmxkIQ==".
        data, mime_type = _parse_data_url(result.path)
        return utils.create_apic_frame(
            data=data, mime_type=mime_type, picture_type=picture_type
        )
    else:
        return utils.create_apic_frame(url=result, picture_type=picture_type)


def unparse_apic(frame: id3.APIC) -> str:
    if frame.mime == "-->":
        # Remote URL. Represented by its location.
        value = frame.data.decode()
    else:
        # Embedded data. Represented as a "data" URL.
        data = base64.b64encode(frame.data).decode()
        value = f"data:{frame.mime};base64,{data}"

    if frame.type:
        value += " "
        value += str(frame.type).split(".")[-1]

    return value
