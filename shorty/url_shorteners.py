import requests

from shorty.utils import retry, logger, get_secret


class ThirdPartyBadResponseError(Exception):
    """ An excpetion raised by any Url shortener service
    whenever a third party responds with any error code
    """

    pass


class UrlShortener(object):
    """The base class for any UrlShortener service
    """

    MAX_DELAY = 10
    RETRIES = 3

    @classmethod
    def raises(cls, message=None):
        """Raise the related exception.

        :param str mesage: a message for the exception

        :raises: ThirdPartyBadResponseError
        """
        message = message or "UrlShortener error"
        logger.warning(message)
        raise ThirdPartyBadResponseError(message)

    def shorten(self, link):
        """Should be implemented. Add the shortening business logic here
        i.e. the interaction with any third party API

        :param string link: the url to be shortened
        """
        raise NotImplementedError

    @retry(
        attempts=RETRIES,
        max_delay=MAX_DELAY,
        no_catch=ThirdPartyBadResponseError,
    )
    def shorten_retry(self, link):
        return self.shorten(link)


class Bitly(UrlShortener):

    URL = "https://api-ssl.bitly.com/v4/shorten"
    CONTENT_TYPE = "application/json"
    AUTHENTICATION_TOKEN = get_secret('Bitly')
    TIMEOUT = 4.0
    SUCCESS_STATUS_CODES = [200, 201]

    def shorten(self, long_link):
        response = requests.post(
            url=self.URL,
            headers={
                "Authorization": self.AUTHENTICATION_TOKEN,
                "Content-Type": self.CONTENT_TYPE,
            },
            json={"long_url": long_link},
            timeout=self.TIMEOUT,
        )
        if response.status_code not in self.SUCCESS_STATUS_CODES:
            self.raises(
                "Bitly response status code: {}".format(response.status_code)
            )

        logger.debug(
            "Bitly input: {input_link}, output {shortened}".format(
                input_link=long_link, shortened=response.json().get("link")
            )
        )

        return response.json().get("link")


class TinyUrl(UrlShortener):

    URL = "http://tinyurl.com/api-create.php?url="
    SUCCESS_STATUS_CODES = [200]

    def shorten(self, long_link):
        response = requests.post(
            url="{base_url}{link}".format(base_url=self.URL, link=long_link)
        )
        if response.status_code not in self.SUCCESS_STATUS_CODES:
            self.raises(
                "TinyUrl response status code: {}".format(response.status_code)
            )
        logger.debug(
            "TinyUrl input: {input_link}, output {shortened}".format(
                input_link=long_link, shortened=response.json().get("link")
            )
        )

        return response.content.decode("utf-8")
