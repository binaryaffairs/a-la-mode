import pytest
import hashlib
from deepdiff import DeepDiff
from a_la_mode import Dag, sha

from .shared import eg_dag, encoded_dag

def sha_file(file):
    h = hashlib.sha256()
    with file.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def test_roundtrip(tmpdir):
    tmpfile = tmpdir.join("eg.dag")
    eg_dag.save(tmpfile)

    assert DeepDiff(Dag.load(tmpfile), encoded_dag)

def test_sha_of_file(tmpdir):
    tmpfile = tmpdir.join("eg.dag")
    eg_dag.save(tmpfile)

    assert sha(eg_dag.bencode()) == sha_file(tmpfile)
