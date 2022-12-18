import subprocess
import textwrap


def test_metadata(get_mp3):
    test_mp3 = get_mp3("metadata.mp3")
    expected = textwrap.dedent(
        """\
        TIT2 = Обробка помилок
        TPE1 = Ігор, Роман
        TRCK = 14/14
        TALB = Шо по коду?
        TDRC = 2022-11-27
        TCON = Podcast
        TSSE = Lavf59.27.100

        00:00:00 Початок
        """
    )
    actual = subprocess.check_output(["id3manager", "get", test_mp3])

    assert expected == actual.decode("utf-8")


def test_no_metadata(get_mp3):
    test_mp3 = get_mp3("no-metadata.mp3")
    expected = ""
    actual = subprocess.check_output(["id3manager", "get", test_mp3])

    assert expected == actual.decode("utf-8")
