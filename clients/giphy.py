# Third party imports
import requests

# Application imports
import config


class Client(object):
    def make_request(
        self, url, method="GET", payload=None, params=None, headers=None
    ):
        if not params:
            params = {}
        if not headers:
            headers = {}

        headers["api_key"] = config.giphy["api_key"]
        params["rating"] = "g"  # Forced G rating

        response = requests.request(
            url=url,
            method=method,
            data=payload,
            params=params,
            headers=headers,
        )
        return response.json()

    def search(self, query, limit=25, offset=0, lang="en"):
        return self.make_request(
            url=config.giphy["search_endpoint"],
            params={
                "q": query,
                "limit": limit,
                "offset": offset,
                "lang": lang,
            },
        )
