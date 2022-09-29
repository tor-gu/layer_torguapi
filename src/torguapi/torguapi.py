import json
import os
from http import HTTPStatus


class TorguapiError(Exception):
    pass


class TorguapiInvalidRequest(TorguapiError):
    pass


def torguapi_get_page_parameters(query_parameters):
    page_params = {}
    page_size = query_parameters.get("page_size", "100")
    page_number = query_parameters.get("page_number", None)

    if not page_size is None:
        if not page_size.isnumeric():
            raise TorguapiInvalidRequest(f"Invalid page_size {page_size}")
        else:
            page_params["page_size"] = int(page_size)
    if page_params["page_size"] < 1:
        raise TorguapiInvalidRequest(f"Invalid page_size {page_size}")
    
    if not page_number is None:
        if not page_number.isnumeric():
            raise TorguapiInvalidRequest(f"Invalid page_number {page_number}")
        else:
            page_params["page_number"] = int(page_number)
    return page_params         



def torguapi_make_links_and_meta(aux, url_path):
    calculate_page_count(aux)
    url_base = make_url_base(url_path)
    links = make_page_links(aux, url_base)
    meta = make_meta(aux)
    return links, meta



def torguapi_http_error(status_code, detail=None):
    # JSON:API standard is to return the the errors as an array, with the status code as a string
    # Example:  {"errors": ["status":"404","detail":"Not found"]}
    if isinstance(status_code, HTTPStatus):
        status = str(status_code.value)
    else:
        status = str(status_code)
    error = {"status": status}
    if detail is not None:
        error["detail"] = detail
    errors = {"errors": [error]}
    return make_torguapi_json(status_code, errors)


def torguapi_result(result, links, meta=None):
    if result.empty:
            return torguapi_http_error(404)
    body = {
            "data": result.to_dict(orient='records'),
            'links': links
        }
    if meta is not None and len(meta) > 0:
        body["meta"] = meta
    return make_torguapi_json(HTTPStatus.OK, body)            


def make_url_base(path):
    API_ROOT = os.environ.get('API_ROOT', '/')
    if not API_ROOT.endswith("/"):
        API_ROOT = API_ROOT + "/"
    return f"{API_ROOT}{path}"

def make_torguapi_json(status_code, body):
    if status_code is None:
        raise TorguapiError("status_code must be specified")
    if body is None:
        raise TorguapiError("body must be specified")
    return {
        'headers': { 
            "Content-Type": "application/vnd.api+json", 
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET" 
        },
        "statusCode": status_code,
        "body": json.dumps(body)
    }


def make_page_link(base_url, page_number, page_size):
    return f'{base_url}?page_number={page_number}&page_size={page_size}'

def make_page_links(aux, url_base):
    links = {}
    if "page_number" not in aux:
        links["self"] = url_base
    else:
        if "page_size" not in aux:
            raise TorguapiError("page_size param missing")
        page_number = aux["page_number"]
        page_size= aux["page_size"]
        links["self"] = make_page_link(url_base, page_number, page_size)
        if "page_count" in aux:
            page_count = aux["page_count"]
            if page_number > 1: 
                links["previous"] = make_page_link(url_base, page_number - 1, page_size)
            if page_number < page_count:
                links["next"] = make_page_link(url_base, page_number + 1, page_size)
    return links


def make_meta(aux):
    meta = {}
    for field_name in {"page_count", "record_count"}:
        if field_name in aux: meta[field_name] = aux[field_name]
    return meta


def calculate_page_count(aux):
    if "record_count" in aux and "page_size" in aux:
        record_count = aux["record_count"]
        page_size = aux["page_size"]
        aux["page_count"] = (record_count - 1) // page_size + 1



