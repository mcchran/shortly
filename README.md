Mission
-------

Our mission, is to build a microservice called `shorty`, 
which supports two URL shortening providers: [bit.ly](https://dev.bitly.com/) and [tinyurl.com](https://gist.github.com/MikeRogers0/2907534).
We don't need to actually sign up to these providers, just implement their API. The
service exposes a single endpoint: `POST /shortlinks`. The endpoint should receive
JSON with the following schema:

| param    | type   | required | description                        |
|----------|--------|----------|------------------------------------|
| url      | string | Y        | The URL to shorten                 |
| provider | string | N        | The provider to use for shortening |

The response should be a `Shortlink` resource containing:

| param    | type   | required | description                        |
|----------|--------|----------|------------------------------------|
| url      | string | Y        | The original URL                   |
| link     | string | Y        | The shortened link                 |

For example:
```json
{
    "url": "https://example.com",
    "link": "https://bit.ly/8h1bka"
}
```

What we did
-------------------

1. Create a Python env (using Python 3.6+) and install the requirements.
2. Build the `POST /shortlinks` endpoint. We've provided a skeleton API using `flask`.
3. Write some tests. We've provided a test blueprint using `pytest`.

What to look for
----------------

In a nutshell, here you can find a tidy, production-quality code, a scalable design and sensible
tests (unit tests, integration tests or both?).

Resources
---------

1. `Flask`: http://flask.pocoo.org/
2. `pytest`: http://pytest.org/latest/
3. `virtualenvwrapper`: https://virtualenvwrapper.readthedocs.io/en/latest/
4. `HTTP statuses`: https://httpstatuses.com/

