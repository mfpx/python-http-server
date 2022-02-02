import server
import pytest
import os


@pytest.fixture
def get_config_data():
    return server.readcfg()


def test_config_yaml_imports(get_config_data):
    # must be a dictionary (key-value pairs)
    assert type(get_config_data) == dict
    # must be 13 in length
    assert len(get_config_data) == 13


def test_thread_count_higher_than_zero(get_config_data):
    assert get_config_data["threads"] >= 1


def test_http_response_loader_returns_false_on_bad_file():
    assert server.httpResponseLoader('999') is False


def test_http_response_loader_returns_bytes():
    assert type(server.httpResponseLoader('404')) == bytes


def test_config_file_exists():
    assert os.path.isfile("conf.yml") is True


def test_config_value_types(get_config_data):
    loopctr = 0

    # types for existing config values test_config_yaml_imports
    value_types = [str, int, str, str, str, int,
                   bool, str, str, int, bool, int, bool]

    for x in get_config_data:
        assert type(get_config_data[x]) == value_types[loopctr]
        loopctr += 1


def test_blacklist_imports():
    bl = server.readblacklist()
    # must be a list
    assert type(bl) == list
    # blacklist must be empty during testing
    assert len(bl) == 0


def test_yaml_cloader():
    from yaml import CLoader as Loader
    # if there is an exception, we'll leave it unhandled so the test fails


