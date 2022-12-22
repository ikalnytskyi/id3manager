import subprocess
import textwrap

import pytest


@pytest.fixture(scope="function", autouse=True)
def editor_ed(monkeypatch):
    monkeypatch.setenv("EDITOR", "ed")


def test_metadata(get_mp3):
    test_mp3 = get_mp3("metadata.mp3")
    ed_input = textwrap.dedent(
        """\
        1
        s/Обробка/Створення
        5
        s/2022-11-27/2022-12-19
        w
        """
    )
    expected = textwrap.dedent(
        """\
        TIT2 = Створення помилок
        TPE1 = Ігор, Роман
        TRCK = 14/14
        TALB = Шо по коду?
        TDRC = 2022-12-19
        TCON = Podcast
        TSSE = Lavf59.27.100

        00:00:00 Початок
        """
    )
    subprocess.check_output(
        ["id3manager", "edit", test_mp3], input=ed_input.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_no_metadata(get_mp3):
    test_mp3 = get_mp3("no-metadata.mp3")
    ed_input = textwrap.dedent(
        """\
        i
        TDRC = 2022-10-14
        TRCK = 12/12
        TPE1 = Ігор, Роман
        TALB = Шо по коду?
        TIT2 = Обробка помилок
        TCON = Podcast

        00:00:00 Кінець
        .
        w
        """
    )
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
        ["id3manager", "edit", test_mp3], input=ed_input.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_toml_metadata(get_mp3):
    test_mp3 = get_mp3("metadata.mp3")
    ed_input = textwrap.dedent(
        """\
        /TIT2
        +
        s/Обробка/Створення
        /TDRC
        +
        s/2022-11-27/2022-12-19
        w
        """
    )
    expected = textwrap.dedent(
        """\
        [[TIT2]]
        text = "Створення помилок"

        [[TPE1]]
        text = "Ігор, Роман"

        [[TRCK]]
        text = "14/14"

        [[TALB]]
        text = "Шо по коду?"

        [[TDRC]]
        text = "2022-12-19"

        [[TCON]]
        text = "Podcast"

        [[TSSE]]
        text = "Lavf59.27.100"

        [[CHAP]]
        text = "Початок"
        timestamp = "00:00:00"
        """
    )
    subprocess.check_output(
        ["id3manager", "-f", "toml", "edit", test_mp3], input=ed_input.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "-f", "toml", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_toml_no_metadata(get_mp3):
    test_mp3 = get_mp3("no-metadata.mp3")
    ed_input = textwrap.dedent(
        """\
        i
        [[TDRC]]
        text = "2022-11-27"

        [[TRCK]]
        text = "14/14"

        [[TPE1]]
        text = "Ігор, Роман"

        [[TALB]]
        text = "Шо по коду?"

        [[TIT2]]
        text = "Обробка помилок"

        [[TCON]]
        text = "Podcast"

        [[CHAP]]
        text = "Кінець"
        timestamp = "00:00:00"
        .
        w
        """
    )
    expected = textwrap.dedent(
        """\
        [[TDRC]]
        text = "2022-11-27"

        [[TRCK]]
        text = "14/14"

        [[TPE1]]
        text = "Ігор, Роман"

        [[TALB]]
        text = "Шо по коду?"

        [[TIT2]]
        text = "Обробка помилок"

        [[TCON]]
        text = "Podcast"

        [[CHAP]]
        text = "Кінець"
        timestamp = "00:00:00"
        """
    )
    subprocess.check_output(
        ["id3manager", "-f", "toml", "edit", test_mp3], input=ed_input.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "-f", "toml", "get", test_mp3])
    assert expected == actual.decode("utf-8")
