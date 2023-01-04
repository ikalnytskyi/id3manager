import typing as t

import mutagen.id3 as id3

from . import utils
from .formats import get_metadata_formatter

__all__ = [
    "read_metadata",
    "write_metadata",
    "ID3SourceFrameOrder",
]


def read_metadata(fileobj: t.IO, format: str, audio_len: float) -> t.List[id3.Frame]:
    """Build an in-memory representation of ID3 frames from a serialized metadata."""

    frames = []
    chapters = []

    for frame in get_metadata_formatter(format).read(fileobj):
        if frame.FrameID not in {"CHAP", "CTOC"}:
            frames.append(frame)
        elif frame.FrameID == "CHAP":
            chapters.append(frame)
        else:
            # TODO: at the moment, we always regenerate CTOC from CHAPs, but
            # we would need to handle CTOC to support nested chapters
            continue

    frames.extend(chapters_from_parts(chapters, audio_len))
    return frames


def write_metadata(fileobj: t.IO, format: str, frames: t.List[id3.Frame]) -> None:
    """Serialize an in-memory representation of ID3 frames into a stream of bytes."""

    return get_metadata_formatter(format).write(fileobj, frames)


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


def chapters_from_parts(
    parts: t.List[id3.Frame], audio_len: float
) -> t.List[id3.Frame]:
    frames = []

    for idx, frame in enumerate(parts[:-1]):
        frames.append(
            id3.CHAP(
                element_id=f"chapter#{idx}",
                start_time=frame.start_time,
                end_time=parts[idx + 1].start_time,
                sub_frames=[id3.TIT2(text=frame.sub_frames["TIT2"].text)],
            )
        )

    frames.append(
        id3.CHAP(
            element_id=f"chapter#{len(parts) - 1}",
            start_time=parts[-1].start_time,
            end_time=utils.sec_to_ms(audio_len),
            sub_frames=[id3.TIT2(text=parts[-1].sub_frames["TIT2"].text)],
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
