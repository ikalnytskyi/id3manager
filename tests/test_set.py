import base64
import subprocess
import textwrap


def test_text_metadata(get_mp3):
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


def test_text_metadata_multiple_chapters(get_mp3):
    expected = textwrap.dedent(
        """\
        TDRC = 2022-10-14
        TRCK = 12/12
        TPE1 = Ігор, Роман
        TALB = Шо по коду?
        TIT2 = Обробка помилок
        TCON = Podcast

        00:00:00 Початок
        00:00:01 Кінець
        """
    )

    test_mp3 = get_mp3("metadata.mp3")
    subprocess.check_output(
        ["id3manager", "set", test_mp3], input=expected.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_text_metadata_multiple_chapters_ms(get_mp3):
    expected = textwrap.dedent(
        """\
        TDRC = 2022-10-14
        TRCK = 12/12
        TPE1 = Ігор, Роман
        TALB = Шо по коду?
        TIT2 = Обробка помилок
        TCON = Podcast

        00:00:00 Початок
        00:00:01.123 Кінець
        """
    )

    test_mp3 = get_mp3("metadata.mp3")
    subprocess.check_output(
        ["id3manager", "set", test_mp3], input=expected.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_text_metadata_apic_url(get_mp3):
    expected = textwrap.dedent(
        """\
        TDRC = 2022-10-14
        TRCK = 12/12
        TPE1 = Ігор, Роман
        TALB = Шо по коду?
        TIT2 = Обробка помилок
        TCON = Podcast
        APIC = https://foo.bar/some.png COVER_FRONT

        00:00:00 Кінець
        """
    )

    test_mp3 = get_mp3("metadata.mp3")
    subprocess.check_output(
        ["id3manager", "set", test_mp3], input=expected.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_text_metadata_apic_url_default_picture_type(get_mp3):
    input = textwrap.dedent(
        """\
        TDRC = 2022-10-14
        TRCK = 12/12
        TPE1 = Ігор, Роман
        TALB = Шо по коду?
        TIT2 = Обробка помилок
        TCON = Podcast
        APIC = https://foo.bar/some.png

        00:00:00 Кінець
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
        APIC = https://foo.bar/some.png COVER_FRONT

        00:00:00 Кінець
        """
    )

    test_mp3 = get_mp3("metadata.mp3")
    subprocess.check_output(
        ["id3manager", "set", test_mp3], input=input.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_text_metadata_apic_file(get_mp3, testdata):
    image_path = testdata / "logo.png"
    image_data = image_path.read_bytes()

    input = textwrap.dedent(
        f"""\
        TDRC = 2022-10-14
        TRCK = 12/12
        TPE1 = Ігор, Роман
        TALB = Шо по коду?
        TIT2 = Обробка помилок
        TCON = Podcast
        APIC = file://{image_path}

        00:00:00 Кінець
        """
    )
    expected = textwrap.dedent(
        f"""\
        TDRC = 2022-10-14
        TRCK = 12/12
        TPE1 = Ігор, Роман
        TALB = Шо по коду?
        TIT2 = Обробка помилок
        TCON = Podcast
        APIC = data:image/png;base64,{base64.b64encode(image_data).decode()} COVER_FRONT

        00:00:00 Кінець
        """
    )

    test_mp3 = get_mp3("metadata.mp3")
    subprocess.check_output(
        ["id3manager", "set", test_mp3], input=input.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_text_metadata_apic_data(get_mp3):
    expected = textwrap.dedent(
        """\
        TDRC = 2022-10-14
        TRCK = 12/12
        TPE1 = Ігор, Роман
        TALB = Шо по коду?
        TIT2 = Обробка помилок
        TCON = Podcast
        APIC = data:image/jpeg;base64,ZHNhZmFzZmFkcw== COVER_FRONT

        00:00:00 Кінець
        """
    )

    test_mp3 = get_mp3("metadata.mp3")
    subprocess.check_output(
        ["id3manager", "set", test_mp3], input=expected.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_text_metadata_apic_data_default_picture_type(get_mp3):
    input = textwrap.dedent(
        """\
        TDRC = 2022-10-14
        TRCK = 12/12
        TPE1 = Ігор, Роман
        TALB = Шо по коду?
        TIT2 = Обробка помилок
        TCON = Podcast
        APIC = data:image/jpeg;base64,ZHNhZmFzZmFkcw==

        00:00:00 Кінець
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
        APIC = data:image/jpeg;base64,ZHNhZmFzZmFkcw== COVER_FRONT

        00:00:00 Кінець
        """
    )

    test_mp3 = get_mp3("metadata.mp3")
    subprocess.check_output(
        ["id3manager", "set", test_mp3], input=input.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_text_metadata_apic_data_no_mime_type(get_mp3):
    expected = textwrap.dedent(
        """\
        TDRC = 2022-10-14
        TRCK = 12/12
        TPE1 = Ігор, Роман
        TALB = Шо по коду?
        TIT2 = Обробка помилок
        TCON = Podcast
        APIC = data:;base64,ZHNhZmFzZmFkcw== COVER_FRONT

        00:00:00 Кінець
        """
    )

    test_mp3 = get_mp3("metadata.mp3")
    subprocess.check_output(
        ["id3manager", "set", test_mp3], input=expected.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_text_metadata_apic_data_no_encoding(get_mp3):
    input = textwrap.dedent(
        """\
        TDRC = 2022-10-14
        TRCK = 12/12
        TPE1 = Ігор, Роман
        TALB = Шо по коду?
        TIT2 = Обробка помилок
        TCON = Podcast
        APIC = data:image/jpeg,ZHNhZmFzZmFkcw==

        00:00:00 Кінець
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
        APIC = data:image/jpeg;base64,ZHNhZmFzZmFkcw== COVER_FRONT

        00:00:00 Кінець
        """
    )

    test_mp3 = get_mp3("metadata.mp3")
    subprocess.check_output(
        ["id3manager", "set", test_mp3], input=input.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_text_metadata_apic_data_invalid_encoding(get_mp3):
    input = textwrap.dedent(
        """\
        TDRC = 2022-10-14
        TRCK = 12/12
        TPE1 = Ігор, Роман
        TALB = Шо по коду?
        TIT2 = Обробка помилок
        TCON = Podcast
        APIC = data:image/jpeg;base128,ZHNhZmFzZmFkcw==

        00:00:00 Кінець
        """
    )

    test_mp3 = get_mp3("metadata.mp3")
    result = subprocess.run(
        ["id3manager", "set", test_mp3],
        input=input.encode("utf-8"),
        capture_output=True,
    )
    assert result.returncode == 1
    assert "Unsupported encoding: `base128`" in result.stderr.decode("utf-8")


def test_text_metadata_apic_data_invalid_picture_type(get_mp3):
    input = textwrap.dedent(
        """\
        TDRC = 2022-10-14
        TRCK = 12/12
        TPE1 = Ігор, Роман
        TALB = Шо по коду?
        TIT2 = Обробка помилок
        TCON = Podcast
        APIC = data:image/jpeg;base64,ZHNhZmFzZmFkcw== NON_EXISTING_TYPE

        00:00:00 Кінець
        """
    )

    test_mp3 = get_mp3("metadata.mp3")
    result = subprocess.run(
        ["id3manager", "set", test_mp3],
        input=input.encode("utf-8"),
        capture_output=True,
    )
    assert result.returncode == 1
    assert "Invalid APIC type value: `NON_EXISTING_TYPE`" in result.stderr.decode(
        "utf-8"
    )


def test_text_no_metadata(get_mp3):
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


def test_toml_metadata(get_mp3):
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

    test_mp3 = get_mp3("metadata.mp3")
    subprocess.check_output(
        ["id3manager", "-f", "toml", "set", test_mp3], input=expected.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "-f", "toml", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_toml_metadata_apic_url(get_mp3):
    input = textwrap.dedent(
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

        [[APIC]]
        url = "https://foo.bar/some.png"
        picture_type = "COVER_FRONT"

        [[CHAP]]
        text = "Кінець"
        timestamp = "00:00:00"
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

        [[APIC]]
        url = "https://foo.bar/some.png"
        mime_type = "-->"
        picture_type = "COVER_FRONT"

        [[CHAP]]
        text = "Кінець"
        timestamp = "00:00:00"
        """
    )

    test_mp3 = get_mp3("metadata.mp3")
    subprocess.check_output(
        ["id3manager", "-f", "toml", "set", test_mp3], input=input.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "-f", "toml", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_toml_metadata_apic_url_default_picture_type(get_mp3):
    input = textwrap.dedent(
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

        [[APIC]]
        url = "https://foo.bar/some.png"

        [[CHAP]]
        text = "Кінець"
        timestamp = "00:00:00"
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

        [[APIC]]
        url = "https://foo.bar/some.png"
        mime_type = "-->"
        picture_type = "COVER_FRONT"

        [[CHAP]]
        text = "Кінець"
        timestamp = "00:00:00"
        """
    )

    test_mp3 = get_mp3("metadata.mp3")
    subprocess.check_output(
        ["id3manager", "-f", "toml", "set", test_mp3], input=input.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "-f", "toml", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_toml_metadata_apic_file(get_mp3, testdata):
    image_path = testdata / "logo.png"
    image_data = image_path.read_bytes()

    input = textwrap.dedent(
        f"""\
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

        [[APIC]]
        url = "file://{image_path}"

        [[CHAP]]
        text = "Кінець"
        timestamp = "00:00:00"
        """
    )
    expected = textwrap.dedent(
        f"""\
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

        [[APIC]]
        data = "{base64.b64encode(image_data).decode()}"
        mime_type = "image/png"
        picture_type = "COVER_FRONT"

        [[CHAP]]
        text = "Кінець"
        timestamp = "00:00:00"
        """
    )

    test_mp3 = get_mp3("metadata.mp3")
    subprocess.check_output(
        ["id3manager", "-f", "toml", "set", test_mp3], input=input.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "-f", "toml", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_toml_metadata_apic_data(get_mp3):
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

        [[APIC]]
        data = "ZHNhZmFzZmFkcw=="
        mime_type = "image/jpeg"
        picture_type = "COVER_FRONT"

        [[CHAP]]
        text = "Кінець"
        timestamp = "00:00:00"
        """
    )
    test_mp3 = get_mp3("metadata.mp3")
    subprocess.check_output(
        ["id3manager", "-f", "toml", "set", test_mp3], input=expected.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "-f", "toml", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_toml_metadata_apic_data_no_mime_type(get_mp3):
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

        [[APIC]]
        data = "ZHNhZmFzZmFkcw=="
        picture_type = "COVER_FRONT"

        [[CHAP]]
        text = "Кінець"
        timestamp = "00:00:00"
        """
    )
    test_mp3 = get_mp3("metadata.mp3")
    subprocess.check_output(
        ["id3manager", "-f", "toml", "set", test_mp3], input=expected.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "-f", "toml", "get", test_mp3])
    assert expected == actual.decode("utf-8")


def test_toml_metadata_apic_data_invalid_value(get_mp3):
    input = textwrap.dedent(
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

        [[APIC]]
        mime_type = "image/jpeg"
        data = "ZHNhZmFzZmFkcw"

        [[CHAP]]
        text = "Кінець"
        timestamp = "00:00:00"
        """
    )
    test_mp3 = get_mp3("metadata.mp3")
    result = subprocess.run(
        ["id3manager", "-f", "toml", "set", test_mp3],
        input=input.encode("utf-8"),
        capture_output=True,
    )
    assert result.returncode == 1
    assert "Invalid base64 value: `ZHNhZmFzZmFkcw`" in result.stderr.decode("utf-8")


def test_toml_metadata_apic_data_invalid_picture_type(get_mp3):
    input = textwrap.dedent(
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

        [[APIC]]
        mime_type = "image/jpeg"
        data = "ZHNhZmFzZmFkcw=="
        picture_type = "NON_EXISTING_TYPE"

        [[CHAP]]
        text = "Кінець"
        timestamp = "00:00:00"
        """
    )
    test_mp3 = get_mp3("metadata.mp3")
    result = subprocess.run(
        ["id3manager", "-f", "toml", "set", test_mp3],
        input=input.encode("utf-8"),
        capture_output=True,
    )
    assert result.returncode == 1
    assert "Invalid APIC type value: `NON_EXISTING_TYPE`" in result.stderr.decode(
        "utf-8"
    )


def test_toml_no_metadata(get_mp3):
    test_mp3 = get_mp3("no-metadata.mp3")
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
        ["id3manager", "-f", "toml", "set", test_mp3], input=expected.encode("utf-8")
    )

    actual = subprocess.check_output(["id3manager", "-f", "toml", "get", test_mp3])
    assert expected == actual.decode("utf-8")
