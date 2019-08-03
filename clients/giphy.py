# Third party imports
import flask
import requests


class Client(object):
    def make_request(
        self, method="GET", payload=None, params=None, headers=None
    ):
        if not params:
            params = {}
        if not headers:
            headers = {}

        headers["api_key"] = flask.globals.giphy["api_key"]
        params["rating"] = "g"  # Forced G rating

        response = requests.request(
            method=method, data=payload, params=params, headers=headers
        )
        return response.json()

    def search(self, query, limit=25, offset=0, lang="en"):
        return self.make_request(
            params={"q": query, "limit": limit, "offset": offset, "lang": lang}
        )
