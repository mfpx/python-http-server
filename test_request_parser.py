import pytest
from request_parser import HTTP, RequestParser

def test_parse_request_valid():
    request = "GET /index.html HTTP/1.1\r\nHost: www.example.com\r\n\r\n"
    http = HTTP(request)
    assert http.REQUEST_METHOD == "GET"
    assert http.REQUEST_PATH == "/index.html" 

def test_parse_request_invalid():
    request = "invalid request"
    with pytest.raises(ValueError):
        http = HTTP(request)

def test_parse_value_by_sep_no_key():
    value = "a,b,c"
    result = RequestParser.parse_value_by_sep(value, False)
    assert result == ["a", "b", "c"]

def test_parse_value_by_sep_with_key():
    value = "a=1,b=2"
    result = RequestParser.parse_value_by_sep(value, True)
    assert result == {"a": "1", "b": "2"}

def test_parse_value_by_sep_no_separator():
    value = "abc"
    result = RequestParser.parse_value_by_sep(value, False)
    assert result == "abc"

def test_parse_value_by_sep_invalid_key_separator():
    value = "a:1,b:2" 
    with pytest.raises(ValueError):
        RequestParser.parse_value_by_sep(value, True)