import os
import pathlib
import shutil
import uuid

import pytest


@pytest.fixture(scope="function")
def testdata():
    here = os.path.abspath(os.path.dirname(__file__))
    return pathlib.Path(here) / "testdata"


@pytest.fixture(scope="function")
def get_mp3(testdata, tmpdir):
    def inner(name):
        destination = pathlib.Path(tmpdir.strpath) / f"{uuid.uuid4()}.mp3"
        shutil.copyfile(testdata / name, destination)
        return destination

    return inner
