from unittest import TestCase
from mock import MagicMock, patch

from shorty.url_shorteners import (
    Bitly,
    TinyUrl,
    UrlShortener,
    ThirdPartyBadResponseError,
)

from shorty.utils import get_secret, AttemptsExceededError

# todo make that in the functional pytest way
class TestUrlShortener(TestCase):
    def setUp(self):
        self.service = UrlShortener()

    @patch("shorty.url_shorteners.logger.warning")
    def test_raises(self, mocked_warning):
        message = "Error message"
        with self.assertRaises(ThirdPartyBadResponseError):
            self.service.raises(message)
        mocked_warning.assert_called_once_with(message)
        pass

    def test_shorten_retry(self):
        shorten = MagicMock()
        shorten.side_effect = Exception
        self.service.shorten = shorten
        with self.assertRaises(AttemptsExceededError):
            self.service.shorten_retry("some_link")
        self.assertEqual(shorten.call_count, self.service.RETRIES)

    def test_shorten(self):
        pass


class TestBitly(TestCase):
    def setUp(self):
        self.service = Bitly()
        self.data = {
            "url": "https://api-ssl.bitly.com/v4/shorten",
            "headers": {
                "Authorization": get_secret('Bitly'),
                "Content-Type": "application/json",
            },
            "json": {"long_url": "url_to_shorten"},
            "timeout": 4.0,
        }
        pass

    @patch("shorty.url_shorteners.requests.post")
    def test_shorten(self, mocked_post):
        mocked_response = MagicMock()
        mocked_response.status_code = 200
        mocked_response.json.return_value = {"link": "short one"}
        mocked_post.return_value = mocked_response

        result = self.service.shorten("url_to_shorten")
        mocked_post.assert_called_once_with(**self.data)
        self.assertEqual(result, "short one")

    @patch("shorty.url_shorteners.requests.post")
    def test_shorten_raises_on_third_party_error(self, mocked_post):
        mocked_response = MagicMock()
        mocked_response.status_code = 500  # bitly has an issue
        mocked_response.json.return_value = {
            "message": "oops something went wrong"
        }
        mocked_post.return_value = mocked_response

        with self.assertRaises(ThirdPartyBadResponseError) as e:
            self.service.shorten("url to shorten")
            self.assertEqual(str(e), "oops something went wrong")


class TestTinyUrl(TestCase):
    def setUp(self):
        self.service = TinyUrl()
        self.url = "http://tinyurl.com/api-create.php?url="
        pass

    @patch("shorty.url_shorteners.requests.post")
    def test_shorten(self, mocked_post):
        mocked_response = MagicMock()
        mocked_response.status_code = 200
        mocked_response.content.decode.return_value = "short one"
        mocked_post.return_value = mocked_response

        result = self.service.shorten("url_to_shorten")
        mocked_post.assert_called_once_with(url=self.url + "url_to_shorten")
        self.assertEqual(result, "short one")
        pass

    @patch("shorty.url_shorteners.requests.post")
    def test_shorten_raises_on_third_party_error(self, mocked_post):
        mocked_response = MagicMock()
        mocked_response.status_code = 500  # bitly has an issue
        mocked_response.json.return_value = {
            "message": "oops something went wrong"
        }
        mocked_post.return_value = mocked_response

        with self.assertRaises(ThirdPartyBadResponseError) as e:
            self.service.shorten("url to shorten")
            self.assertEqual(str(e), "oops something went wrong")
