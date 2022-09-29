import json
from http import HTTPStatus
import pandas as pd

import pytest


from src.torguapi import torguapi

def test_make_torguapi_json_1():
    """make_torguapi_json basic test"""
    body = {"foo": "bar"}
    status_code = 200
    result = torguapi.make_torguapi_json(status_code, body)
    assert "headers" in result
    assert "statusCode" in result
    assert "body" in result
    assert status_code == result["statusCode"]
    assert body == json.loads(result["body"])

def test_make_torguapi_json_2():
    """make_torguapi_json raised excepiton if body is None"""
    body = None
    status_code = 200
    with pytest.raises(torguapi.TorguapiError):
        torguapi.make_torguapi_json(status_code, body)

def test_make_torguapi_json_3():
    """make_torguapi_json raised excepiton if status_code is None"""
    body = {"foo": "bar"}
    status_code = None
    with pytest.raises(torguapi.TorguapiError):
        torguapi.make_torguapi_json(status_code, body)

def test_torguapi_http_error_1():
    """torguapi_http_error basic test with HTTPStatus"""
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    detail = "Detail message"
    result = torguapi.torguapi_http_error(status_code, detail)
    assert status_code.value == result["statusCode"]
    expected_body = {
        "errors": [{
            "status": str(status_code.value), 
            "detail":detail}]
    }
    assert expected_body == json.loads(result["body"])

def test_torguapi_http_error_2():
    """torguapi_http_error basic test with numeric status"""
    status_code = 500
    detail = "Detail message"
    result = torguapi.torguapi_http_error(status_code, detail)
    assert status_code == result["statusCode"]
    expected_body = {
        "errors": [{
            "status": str(status_code), 
            "detail":detail}]
    }
    assert expected_body == json.loads(result["body"])

def test_torguapi_http_error_3():
    """torguapi_http_error test with no detail"""
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    result = torguapi.torguapi_http_error(status_code)
    assert status_code.value == result["statusCode"]
    expected_body = {
        "errors": [{
            "status": str(status_code.value)}]
    }
    assert expected_body == json.loads(result["body"])


def test_torguapi_result_1():
    """torguapi_result basic test"""
    df = pd.DataFrame({'x': [1,2], 'y': ["a","b"]})
    links = {"self": "foo", "next": "bar"}
    result = torguapi.torguapi_result(df, links)
    body = json.loads(result["body"])
    status_code = result["statusCode"]
    expected_data = [
        {'x':1, 'y':'a'},
        {'x':2, 'y':'b'}
    ]
    assert HTTPStatus.OK == status_code
    assert links == body["links"]
    assert expected_data == body["data"]
    assert "meta" not in body
    

def test_torguapi_result_2():
    """torguapi_result test nonempty meta"""
    df = pd.DataFrame({'x': [1,2], 'y': ["a","b"]})
    links = {}
    meta = {"foo": "bar"}
    result = torguapi.torguapi_result(df, links, meta)
    body = json.loads(result["body"])
    status_code = result["statusCode"]
    assert HTTPStatus.OK == status_code
    assert meta == body["meta"]

def test_torguapi_result_3():
    """torguapi_result test empty meta"""
    df = pd.DataFrame({'x': [1,2], 'y': ["a","b"]})
    links = {}
    meta = {}
    result = torguapi.torguapi_result(df, links, meta)
    body = json.loads(result["body"])
    status_code = result["statusCode"]
    assert HTTPStatus.OK == status_code
    assert "meta" not in body

def test_torguapi_result_4():
    """torguapi_result test empty dataframe"""
    df = pd.DataFrame()
    links = {}
    result = torguapi.torguapi_result(df, links)
    status_code = result["statusCode"]
    assert HTTPStatus.NOT_FOUND == status_code

def test_make_page_link_1():
    """make_page_link basic test"""
    base_url = "https://example.com"
    page_number = 3
    page_size = 10
    expected_link = "https://example.com?page_number=3&page_size=10"
    actual_link = torguapi.make_page_link(base_url, page_number, page_size)
    assert expected_link == actual_link

def test_make_page_links_1():
    """make_page_links base only"""    
    url_base = "https://example.com"
    aux = {}
    links = torguapi.make_page_links(aux, url_base)
    assert {"self": url_base} == links

def test_make_page_links_2():
    """make_page_links raises error when page_number present but page_size missing"""
    url_base = "https://example.com"
    aux = {"page_number": 37}
    with pytest.raises(torguapi.TorguapiError):
        torguapi.make_page_links(aux, url_base)

def test_make_page_links_3():
    """make_page_links with pagination but no page_count"""
    url_base = "https://example.com"
    aux = {"page_number": 37, "page_size": 100}
    links = torguapi.make_page_links(aux, url_base)
    self_link = "https://example.com?page_number=37&page_size=100"
    assert {"self": self_link} == links

def test_make_page_links_4():
    """make_page_links with pagination, first page"""
    url_base = "https://example.com"
    aux = {"page_number": 1, "page_size": 100, "page_count": 10}
    links = torguapi.make_page_links(aux, url_base)
    self_link = "https://example.com?page_number=1&page_size=100"
    next_link = "https://example.com?page_number=2&page_size=100"
    assert {"self": self_link, "next": next_link} == links

def test_make_page_links_5():
    """make_page_links with pagination, last page"""
    url_base = "https://example.com"
    aux = {"page_number": 10, "page_size": 100, "page_count": 10}
    links = torguapi.make_page_links(aux, url_base)
    self_link = "https://example.com?page_number=10&page_size=100"
    prev_link = "https://example.com?page_number=9&page_size=100"
    assert {"self": self_link, "previous": prev_link} == links

def test_make_page_links_6():
    """make_page_links with pagination, middle page"""
    url_base = "https://example.com"
    aux = {"page_number": 4, "page_size": 100, "page_count": 10}
    links = torguapi.make_page_links(aux, url_base)
    self_link = "https://example.com?page_number=4&page_size=100"
    prev_link = "https://example.com?page_number=3&page_size=100"
    next_link = "https://example.com?page_number=5&page_size=100"
    assert {"self": self_link, "previous": prev_link, "next": next_link} == links

def test_make_meta_1():    
    """make_meta basic text"""
    aux = {"page_count":3, "record_count":4, "extra_1":5, "extra_2":6}
    expected_meta = {"page_count":3, "record_count":4}
    assert expected_meta == torguapi.make_meta(aux)

def test_calculate_page_count_1():
    """calculate_page_count basic test"""
    aux = {"record_count": 100, "page_size": 10}
    torguapi.calculate_page_count(aux)
    assert aux["page_count"] == 10

def test_calculate_page_count_2():
    """calculate_page_count rounds up"""
    aux = {"record_count": 101, "page_size": 10}
    torguapi.calculate_page_count(aux)
    assert aux["page_count"] == 11

def test_torguapi_make_links_and_meta_1(monkeypatch):
    """torguapi_make_links_and_meta basic test"""
    monkeypatch.setenv("API_ROOT", "https://example.com")

    aux = {"page_number": 3, "record_count": 101, "page_size": 10}
    links, meta = torguapi.torguapi_make_links_and_meta(aux, "foo/bar")
    expected_links = {
        "self": "https://example.com/foo/bar?page_number=3&page_size=10",
        "next": "https://example.com/foo/bar?page_number=4&page_size=10",
        "previous": "https://example.com/foo/bar?page_number=2&page_size=10"
    }
    expected_meta = {
        "page_count": 11,
        "record_count": 101
    }
    assert expected_links == links
    assert expected_meta == meta

def test_torguapi_make_links_and_meta_2():
    """torguapi_make_links_and_meta No API_ROOT env variable"""
    aux = {"page_number": 3, "record_count": 101, "page_size": 10}
    links, meta = torguapi.torguapi_make_links_and_meta(aux, "foo/bar")
    expected_links = {
        "self": "/foo/bar?page_number=3&page_size=10",
        "next": "/foo/bar?page_number=4&page_size=10",
        "previous": "/foo/bar?page_number=2&page_size=10"
    }
    assert expected_links == links

def test_torguapi_make_links_and_meta_3(monkeypatch):
    """torguapi_make_links_and_meta API_ROOT env variable has trailing '/'"""
    monkeypatch.setenv("API_ROOT", "https://example.com/")
    aux = {"page_number": 3, "record_count": 101, "page_size": 10}
    links, meta = torguapi.torguapi_make_links_and_meta(aux, "foo/bar")
    expected_links = {
        "self": "https://example.com/foo/bar?page_number=3&page_size=10",
        "next": "https://example.com/foo/bar?page_number=4&page_size=10",
        "previous": "https://example.com/foo/bar?page_number=2&page_size=10"
    }
    assert expected_links == links

def test_torguapi_get_page_parameters_1():
    """torguapi_get_page_parameters use default query parameters"""
    query_parameters = {"a":"b"}
    params = torguapi.torguapi_get_page_parameters(query_parameters)
    expected_params = {"page_size": 100}
    assert expected_params == params

def test_torguapi_get_page_parameters_2():
    """torguapi_get_page_parameters basic test"""
    query_parameters = {"a":"b", "page_size": "37", "page_number": "2"}
    params = torguapi.torguapi_get_page_parameters(query_parameters)
    expected_params = {"page_size": 37, "page_number": 2}
    assert expected_params == params    

def test_torguapi_get_page_parameters_3():
    """torguapi_get_page_parameters invalid page size (non-numeric)"""
    query_parameters = {"a":"b", "page_size": "foo", "page_number": "2"}
    with pytest.raises(torguapi.TorguapiInvalidRequest):
        torguapi.torguapi_get_page_parameters(query_parameters)

def test_torguapi_get_page_parameters_4():
    """torguapi_get_page_parameters invalid page size (less than 1)"""
    query_parameters = {"a":"b", "page_size": "0", "page_number": "2"}
    with pytest.raises(torguapi.TorguapiInvalidRequest):
        torguapi.torguapi_get_page_parameters(query_parameters)

def test_torguapi_get_page_parameters_5():
    """torguapi_get_page_parameters invalid page number"""
    query_parameters = {"a":"b", "page_size": "37", "page_number": "foo"}
    with pytest.raises(torguapi.TorguapiInvalidRequest):
        torguapi.torguapi_get_page_parameters(query_parameters)
