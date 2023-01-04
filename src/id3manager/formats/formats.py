import typing as t

from .abc import MetadataFormatter
from .text import TextMetadataFormatter
from .toml import TomlMetadataFormatter

FORMATTERS = {
    formatter.name: formatter
    for formatter in [TextMetadataFormatter(), TomlMetadataFormatter()]
}


def get_metadata_formatter(name: str) -> MetadataFormatter:
    """Return an implementation of a given metadata format."""

    try:
        return FORMATTERS[name]
    except KeyError:
        raise ValueError(f"{name}: unsupported format")


def get_supported_formats() -> t.List[str]:
    """Return the list of supported metadata formats."""

    return list(FORMATTERS.keys())
