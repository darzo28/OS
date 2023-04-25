import os
import pytest
from prog_parser import *

TEST_PATH = os.path.join(os.path.dirname(__file__), "tests")

def test_parser_no_exception():
    VALID_TEST_PATH = os.path.join(TEST_PATH, "valid")    

    for file in os.listdir(VALID_TEST_PATH):
        try:
            parseFile(os.path.join(VALID_TEST_PATH, file))
        except Exception as e:
            assert False

def test_parser_raise_exception():
    INVALID_TEST_PATH = os.path.join(TEST_PATH, "invalid")    

    for file in os.listdir(INVALID_TEST_PATH):
        with pytest.raises(Exception):
            parseFile(os.path.join(INVALID_TEST_PATH, file))
