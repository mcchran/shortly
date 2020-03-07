import json
from flask import jsonify
from mock import patch, MagicMock

# unittests
def test_api_success_response(client):
    pass


def test_invalid_schema(client):
    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    url = "/shortlinks"
    data = {"link": "https://www.google.com", "provider": "bitly"}
    response = client.post(url, data=json.dumps(data), headers=headers)
    assert response.status_code == 400


def test_invalid_url(client):
    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    url = "/shortlinks"
    data = {"url": "google.com", "provider": "bitly"}
    response = client.post(url, data=json.dumps(data), headers=headers)
    assert response.status_code == 422
    pass


@patch("shorty.api.schema_definition.validate")
@patch("shorty.api.url_is_valid")
@patch("shorty.api.fallback_chain")
def test_api_failure_response(
    mocked_fallback_chain, url_is_valid, mocked_schema_validation, client
):
    mocked_schema_validation.return_value = {"url": "https://www.google.com"}
    url_is_valid.return_value = True
    shorten = MagicMock()
    shorten.return_value = (
        ""
    )  # third pary services did not provide any response
    mocked_fallback_chain.return_value = shorten

    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {"url": "https://www.google.com", "provider": "bitly"}
    url = "/shortlinks"

    response = client.post(url, data=json.dumps(data), headers=headers)
    assert response.content_type == mimetype
    assert response.json["url"] == "https://www.google.com"
    assert response.status_code == 502  # that is an unknown issue


# end to end integration test
def test_bitly_integration(client):

    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {"url": "https://www.google.com", "provider": "bitly"}
    url = "/shortlinks"

    response = client.post(url, data=json.dumps(data), headers=headers)

    assert response.content_type == mimetype
    assert response.json["url"] == "https://www.google.com"
    assert response.status_code == 200


def test_tinyurl_integration(client):

    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {"url": "https://www.google.com", "provider": "tinyUrl"}
    url = "/shortlinks"

    response = client.post(url, data=json.dumps(data), headers=headers)

    assert response.content_type == mimetype
    assert response.json["url"] == "https://www.google.com"
    assert response.status_code == 200
