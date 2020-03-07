import time

from mock import patch
from unittest import TestCase

from shorty.utils import (
    retry,
    url_is_valid,
    get_secret,
    AttemptsExceededError,
    MaxDelayExceededError,
    SecretNotFoundError
)


class TestRetryUtils(TestCase):
    @patch("shorty.utils.logger")
    @patch("shorty.utils.time")
    def test_retry_success_in_the_first_attempt(
        self, mocked_time, mocked_logger
    ):

        should_respond = "proper response"

        @retry()
        def func():
            return should_respond

        response = func()
        self.assertEqual(response, should_respond)
        self.assertEqual(mocked_logger.warning.call_count, 0)

    @patch("shorty.utils.logger")
    @patch("shorty.utils.time.sleep")
    def test_retry_exceeds_max_attempts(self, mocked_sleep, mocked_logger):
        max_attempts = 2

        @retry(exception=NotImplementedError, attempts=max_attempts)
        def func():
            raise NotImplementedError

        with self.assertRaises(AttemptsExceededError):
            func()

        self.assertEqual(mocked_sleep.call_count, max_attempts - 1)
        self.assertEqual(mocked_logger.warning.call_count, max_attempts)

    @patch("shorty.utils.time.sleep")
    def test_retry_raises_not_handled_excpetion(self, mocked_sleep):

        max_attempts = 2

        @retry(exception=NotImplementedError, attempts=max_attempts)
        def func():
            raise ZeroDivisionError

        with self.assertRaises(ZeroDivisionError):
            func()
        self.assertEqual(mocked_sleep.call_count, 0)

    @patch("shorty.utils.time.sleep")
    def test_retry_exceeds_max_delay(self, mocked_sleep):
        attempts = 2
        max_delay = 1

        @retry(exception=Exception, attempts=attempts, max_delay=max_delay)
        def func():
            time.sleep(10)
            raise Exception

        with self.assertRaises(MaxDelayExceededError):
            func()

    @patch("shorty.utils.time.sleep")
    def test_raises_on_no_catch(self, mocked_sleep):
        attempts = 10
        max_delay = 10
        no_catch = NotImplementedError

        @retry(no_catch=no_catch)
        def func():
            raise NotImplementedError

        with self.assertRaises(AttemptsExceededError):
            func()
        self.assertEqual(mocked_sleep.call_count, 0)


class TestValidateUrl(TestCase):
    def test_true_on_success(self):
        self.assertTrue(url_is_valid("https://www.google.com"))

    def test_false_on_failure(self):
        self.assertFalse(url_is_valid("malformed one"))


@patch("shorty.utils.os")
class Test_get_secret(TestCase):

    def test_success(self, mocked_os):
        mocked_os.environ = {'test': 'some secret'}
        expected_secret = 'some secret'
        secret = get_secret('test')
        self.assertEqual(secret, expected_secret)

    def test_fail_raises(self, mocked_os):
        mocked_os.environ = {'test': 'some secret'}
        with self.assertRaises(SecretNotFoundError):
            _ = get_secret('key does not exist')
