import dataclasses
import typing as t

import mutagen.id3 as id3

from .text import read_text_metadata, write_text_metadata
from .toml import read_toml_metadata, write_toml_metadata


@dataclasses.dataclass
class Format:
    reader: t.Callable[[t.IO], t.List[id3.Frame]]
    writer: t.Callable[[t.IO, t.List[id3.Frame]], None]


FORMATS: t.Dict[str, Format] = {
    "text": Format(reader=read_text_metadata, writer=write_text_metadata),
    "toml": Format(reader=read_toml_metadata, writer=write_toml_metadata),
}


def get_supported_formats() -> t.List[str]:
    """Return the list of supported metadata formats."""

    return list(FORMATS.keys())


def get_format(name: str) -> Format:
    try:
        fmt = FORMATS[name]
    except KeyError:
        raise ValueError(f"{name}: unsupported format")

    return fmt
