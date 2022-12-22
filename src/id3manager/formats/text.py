import re
import typing as t

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
