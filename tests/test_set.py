import subprocess
import textwrap


def test_metadata(get_mp3):
    expected = textwrap.dedent(
        """\
        TDRC = 2022-10-14
        TRCK = 12/12
        TPE1 = Ігор, Роман
        TALB = Шо по коду?
        TIT2 = Обробка помилок
        TCON = Podcast

        00:00:00 Кінець
        """
    )

    test_mp3 = get_mp3("metadata.mp3")
    subprocess.check_output(
        ["id3manager", "set", test_mp3], input=expected.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_no_metadata(get_mp3):
    test_mp3 = get_mp3("no-metadata.mp3")
    expected = textwrap.dedent(
        """\
        TDRC = 2022-10-14
        TRCK = 12/12
        TPE1 = Ігор, Роман
        TALB = Шо по коду?
        TIT2 = Обробка помилок
        TCON = Podcast

        00:00:00 Кінець
        """
    )
    subprocess.check_output(
        ["id3manager", "set", test_mp3], input=expected.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "get", test_mp3])
    assert expected == actual.decode("utf-8")
