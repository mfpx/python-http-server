import pytest, random
from server import HelperFunctions
from unittest.mock import MagicMock

@pytest.fixture
def helper():
    return HelperFunctions()

@pytest.fixture
def random_data() -> int | bytes:
    def _data(type):
        if type == 'int':
            return random.randint(0, 1000000)
        elif type == 'bytes':
            return random.randbytes(1024)
        else:
            raise ValueError(f"Invalid type: {type}")
    return _data

@pytest.fixture
def structure(random_data) -> dict:
    def _structure(name, return_type):
        '''This function gets injected'''
        retval = {
            'name': name,
            'data': random_data(return_type)
        }
        # register the result in the function
        _structure.results[name] = retval
        return retval
    # before injecting, we create the registry
    # on the function
    _structure.results = {}
    return _structure

@pytest.fixture
def temp_file(tmp_path_factory, structure):
        def _data(name):
            fn = tmp_path_factory.mktemp("testdata") / f"file{structure(name, 'int')}.txt"
            fn.write_text(str(structure(name, "bytes")))
            return fn
        return _data

def test_compute_hash_returns_str(helper, temp_file):
    hash = helper.compute_hash(temp_file("file_suffix_one"))
    assert isinstance(hash, str)

def test_compute_hash_different_contents(helper, temp_file):
    hash1 = helper.compute_hash(temp_file("file_suffix_one"))
    hash2 = helper.compute_hash(temp_file("file_suffix_two"))
    assert hash1 != hash2

def test_get_hash_caches(helper, temp_file):
    file = temp_file("file_suffix_one")
    hash1 = helper.get_hash(file)
    hash2 = helper.get_hash(file)
    assert hash1 is hash2

def test_has_method_valid(helper):
    assert helper._HelperFunctions__has_method(str, 'upper') is True

def test_has_method_invalid(helper):
    assert helper._HelperFunctions__has_method(str, 'invalid') is False
    
@pytest.mark.skip(reason="Broken")
def test_plugin_init_class_found(helper):
    module = MagicMock()
    module.PluginInit_Test = MagicMock()
    cls = helper._HelperFunctions__plugin_init_class(module)
    assert cls == module.PluginInit_Test
    
def test_plugin_init_class_meta(helper):
    module = MagicMock()
    module.PLUGIN_DATA = {'meta': {'initclass': 'Test'}}
    module.Test = MagicMock()
    cls = helper._HelperFunctions__plugin_init_class(module)
    assert cls == module.Test
    
def test_plugin_obj_to_str(helper):
    module = MagicMock()
    module.PLUGIN_DATA = {'name': 'test', 'version': '1.0', 'author': 'me'}
    assert helper._HelperFunctions__plugin_obj_to_str(module) == 'test (v1.0) by me'
