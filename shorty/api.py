import json
from flask import Blueprint, jsonify, request, make_response
from schema import Schema, And, Use, Optional

from shorty.url_shorteners import TinyUrl, Bitly
from shorty.utils import url_is_valid, fallback_chain, logger

api = Blueprint("api", __name__)


# the endpoint schema defintion
schema_definition = Schema(
    And(Use(json.loads), {Optional("provider"): str, "url": str})
)


@api.route("/shortlinks", methods=["POST"])
def create_shortlink():
    """ Endpoint to perform url shortening

    - Accepts a POST message affording the following json schema:
        {
            'provider':  <"bitly"/"tinyUrl">,
            "url": "the long url to be shortened"
        }

    - Response:
        {
            "url": "the long url to be shortened",
            "link": "the shortened link"
        }

        STATUS_CODES:
            200: OK
            400: bad request, json validation error
            422: for not proper long urls
            502: for third party services not properly behaving
    """

    try:
        request_json = schema_definition.validate(request.data)
    except Exception as e:
        logger.debug(e)
        return make_response(jsonify({"error": str(e)}), 400)
    provider = request_json.get("provider", None)
    url = request_json.get("url", "")

    logger.debug(
        "-- create_shortlink, retrived request_json: {}".format(request_json)
    )

    if not url_is_valid(url):
        logger.info("-- create_shortlink: invlid ur: {}".format(url))
        return make_response(
            jsonify(
                {"url": request_json.get("url", ""), "error": "invalid url"}
            ),
            422,
        )

    if not provider or provider.lower() == "bitly":
        shorten = fallback_chain(Bitly().shorten_retry, TinyUrl().shorten_retry)
    else:
        shorten = fallback_chain(TinyUrl().shorten_retry, Bitly().shorten_retry)

    shortened_url = shorten(url)

    if not shortened_url:
        logger.critical(
            "-- create_shortlink: no results for url: {}, preferred provider: {} pair".format(
                url, provider
            )
        )
        return make_response(
            jsonify(
                {
                    "url": request_json.get("url", ""),
                    "error": "None of the two providers are behaving",
                }
            ),
            502,
        )

    return make_response(
        jsonify({"url": request_json.get("url", ""), "link": shortened_url}),
        200,
    )
