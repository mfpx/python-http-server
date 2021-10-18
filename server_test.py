import server
import pytest


@pytest.fixture
def get_config_data():
    return server.readcfg()


def test_config_json_imports(get_config_data):
    # must be a dictionary (key-value pairs)
    assert type(get_config_data) == dict
    # must be 13 in length
    assert len(get_config_data) == 13


def test_thread_count_higher_than_zero(get_config_data):
    assert get_config_data["threads"] >= 1


def test_config_value_types(get_config_data):
    loopctr = 0

    # types for existing config values
    value_types = [str, int, str, str, int, str,
                   str, bool, int, bool, bool, str, str]

    for x in get_config_data:
        assert type(get_config_data[x]) == value_types[loopctr]
        loopctr += 1


def test_blacklist_imports():
    bl = server.readblacklist()
    # must be a list
    assert type(bl) == list
    # blacklist must be empty during testing
    assert len(bl) == 0
