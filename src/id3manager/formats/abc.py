import abc
import typing as t

import mutagen.id3 as id3


class MetadataFormatter(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Return a string name of this metadata formatter."""

    @abc.abstractmethod
    def read(self, fileobj: t.IO) -> t.List[id3.Frame]:
        """Deserialize ID3 frames from a stream of bytes."""

    @abc.abstractmethod
    def write(self, fileobj: t.IO, frames: t.List[id3.Frame]) -> None:
        """Serialize ID3 frames into a stream of bytes."""
