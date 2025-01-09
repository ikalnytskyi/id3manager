import base64
import mimetypes
import typing as t
import urllib.parse as urlparse

import mutagen.id3 as id3


def parse_timestamp_to_ms(timestamp: str, sep: str = ":") -> int:
    parts = [float(part) for part in timestamp.split(sep)]
    parts = [0] * (3 - len(parts)) + parts
    hrs, min, sec = parts
    return int((hrs * 60 * 60 + min * 60 + sec) * 1000)


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


def get_apic_picture_type(value: t.Union[str, int, None] = None) -> id3.PictureType:
    # id3.PictureType is not an enum from the standard library :(
    FIRST = 0x00
    LAST = 0x14

    if isinstance(value, str) and hasattr(id3.PictureType, value):
        # Mutagen enum variants.
        return getattr(id3.PictureType, value)
    elif isinstance(value, int) and (value >= FIRST and value <= LAST):
        # Picture type codes from https://id3.org/id3v2.3.0#Attached_picture.
        return id3.PictureType(value)
    elif value is None:
        # The most suitable default value.
        return id3.PictureType.COVER_FRONT
    else:
        supported_values = [
            str(id3.PictureType(i)).split(".")[-1] for i in range(FIRST, LAST)
        ]
        raise ValueError(
            f"Invalid APIC type value: `{value}`. "
            f"Supported values are: `{supported_values}`"
        )


def create_apic_frame(
    data: t.Optional[str] = None,
    url: t.Optional[urlparse.ParseResult] = None,
    mime_type: t.Optional[str] = None,
    picture_type: t.Optional[id3.PictureType] = None,
) -> id3.APIC:
    if not picture_type:
        picture_type = id3.PictureType.COVER_FRONT
    if not mime_type:
        mime_type = ""

    if data and not url:
        try:
            raw_data = base64.b64decode(data)
        except Exception:
            raise ValueError(f"Invalid base64 value: `{data}`")

        return id3.APIC(data=raw_data, type=picture_type, mime=mime_type)
    elif url and not data:
        if url.scheme == "file":
            # URL specifying the location of an image file on the local host. The data
            # is loaded to be stored in the APIC frame. The MIME type is deducted from
            # the file extension.
            #
            # E.g. "file:///path/to/image.jpeg"
            if not mime_type:
                mime_type, _ = mimetypes.guess_type(url.path)

            return id3.APIC(
                data=open(url.path, "rb").read(),
                type=picture_type,
                mime=mime_type,
            )
        elif url.scheme == "http" or url.scheme == "https":
            # URL specifying the remote location. The URL is *not* resolved and is stored
            # as is in the APIC frame. The special MIME type "-->" is used per specification
            # (https://id3.org/id3v2.3.0).
            #
            # E.g. "https://www.site.com/my/image.png".
            return id3.APIC(
                data=urlparse.urlunparse(url).encode(),
                type=picture_type,
                mime="-->",
            )
        else:
            raise ValueError(f"Invalid APIC URL value: `{url}`")
    else:
        raise ValueError("Exactly one of `data` or `url` must be specified")
