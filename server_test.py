import server
import pytest
import os


@pytest.fixture
def get_config_data():
    return server.HelperFunctions().readcfg()


def test_config_yaml_imports(get_config_data):
    # must be a dictionary (key-value pairs)
    assert type(get_config_data) == dict
    # must be 17 in length
    assert len(get_config_data) == 17


@pytest.mark.skip
def test_http_response_loader_returns_false_on_bad_file():
    assert server.Server.http_response_loader('999') is False


@pytest.mark.skip
def test_http_response_loader_returns_bytes():
    assert type(server.Server.http_response_loader('404')) == bytes


def test_config_file_exists():
    assert os.path.isfile("conf.yml") is True


def test_config_value_types(get_config_data):
    # types for existing config values test_config_yaml_imports
    value_types = [str, int, str, str, str, int,
                   str, bool, str, str, int, bool,
                   bool, str, str, str, bool]

    for x, y in enumerate(get_config_data):
        assert type(get_config_data[y]) == value_types[x]


def test_yaml_cloader():
    from yaml import CLoader as Loader
    # if there is an exception, we'll leave it unhandled so the test fails
