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
