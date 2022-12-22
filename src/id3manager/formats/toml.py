import collections
import typing as t

import mutagen.id3 as id3
import tomlkit

from .. import utils
from .abc import MetadataFormatter


class TomlMetadataFormatter(MetadataFormatter):
    @property
    def name(self):
        return "toml"

    def read(self, fileobj: t.IO) -> t.List[id3.Frame]:
        metadata = tomlkit.load(fileobj)

        parsed_frames = []

        for frame_name, frames in metadata.items():
            for frame in frames:
                frame_cls = id3.Frames[frame_name]

                if issubclass(frame_cls, id3.TextFrame):
                    frame = frame_cls(text=[frame["text"]])
                elif issubclass(frame_cls, id3.UrlFrame):
                    frame = frame_cls(url=frame["url"])
                elif issubclass(frame_cls, id3.CHAP):
                    timestamp = utils.parse_timestamp_to_ms(frame["timestamp"])
                    chapter_title = frame["text"]

                    frame = frame_cls(
                        start_time=timestamp,
                        sub_frames=[id3.TIT2(text=chapter_title)],
                    )
                else:
                    raise ValueError(f"{frame}: unsupported frame")

                parsed_frames.append(frame)

        return parsed_frames

    def write(self, fileobj: t.IO, frames: t.List[id3.Frame]) -> None:
        output = collections.defaultdict(list)

        for frame in frames:
            if isinstance(frame, id3.TextFrame):
                output[frame.FrameID].append({"text": str(frame.text[0])})
            elif isinstance(frame, id3.UrlFrame):
                output[frame.FrameID].append({"url": frame.url})
            elif isinstance(frame, id3.CHAP):
                output[frame.FrameID].append(
                    {
                        "text": frame.sub_frames["TIT2"].text[0],
                        "timestamp": utils.ms_to_human_time(frame.start_time),
                    }
                )
            elif isinstance(frame, id3.CTOC):
                # TODO: implement this when we add support for nested chapters
                pass
            else:
                raise ValueError(f"{frame.FrameID}: unsupported frame")

        tomlkit.dump(output, fileobj)
