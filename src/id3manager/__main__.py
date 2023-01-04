import argparse
import os
import subprocess
import sys
import tempfile

import mutagen.mp3 as mp3

from . import formats, metadata

EDITOR = os.environ.get("EDITOR", "vi")


def get_subcommand_entrypoint(args, file=sys.stdout):
    audio_mp3 = mp3.MP3(args.audio, ID3=metadata.ID3SourceFrameOrder)
    if audio_mp3.tags is None:
        return
    frames = audio_mp3.tags.values()

    metadata.write_metadata(file, args.format, frames)


def set_subcommand_entrypoint(args, file=sys.stdin):
    audio_mp3 = mp3.MP3(args.audio, ID3=metadata.ID3SourceFrameOrder)

    frames = metadata.read_metadata(file, args.format, audio_len=audio_mp3.info.length)

    if audio_mp3.tags is None:
        audio_mp3.add_tags(ID3=metadata.ID3SourceFrameOrder)
    audio_mp3.tags.delete(args.audio)

    for frame in frames:
        audio_mp3.tags.add(frame)
    audio_mp3.save(args.audio)


def edit_subcommand_entrypoint(args):
    with tempfile.NamedTemporaryFile(mode="w+t") as fp:
        get_subcommand_entrypoint(args, file=fp)
        fp.flush()

        process = subprocess.Popen([EDITOR, fp.name])
        process.wait()

        fp.seek(0)
        set_subcommand_entrypoint(args, file=fp)


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="The ID3 metadata manager that you have been missing.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=formats.get_supported_formats(),
        default="text",
        help="format to use for metadata",
    )
    subparsers = parser.add_subparsers(required=True, title="subcommands")

    parser_get = subparsers.add_parser("get", help="get ID3 metadata")
    parser_get.add_argument(
        "audio",
        metavar="audio.mp3",
        type=argparse.FileType("rb"),
        help="the aduio file to get metadata from",
    )
    parser_get.set_defaults(subcommand=get_subcommand_entrypoint)

    parser_set = subparsers.add_parser("set", help="set ID3 metadata")
    parser_set.add_argument(
        "audio",
        metavar="audio.mp3",
        type=argparse.FileType("rb+"),
        help="the audio file to set metadata in",
    )
    parser_set.set_defaults(subcommand=set_subcommand_entrypoint)

    parser_edit = subparsers.add_parser("edit", help="interactively edit ID3 metadata")
    parser_edit.add_argument(
        "audio",
        metavar="audio.mp3",
        type=argparse.FileType("rb+"),
        help="the audio file to edit metadata in",
    )
    parser_edit.set_defaults(subcommand=edit_subcommand_entrypoint)

    args = parser.parse_args(argv)
    return args.subcommand(args)


if __name__ == "__main__":
    main()
