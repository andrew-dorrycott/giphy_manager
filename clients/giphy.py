# Third party imports
import requests

# Application imports
import config


class Client(object):
    def make_request(
        self, url, method="GET", payload=None, params=None, headers=None
    ):
        """
        Centralized handler of all requests to GIPHY

        :param url: URL being requested
        :type url: str
        :param method: GET/POST/PUT/DELETE
        :type method: str
            :default: GET
        :param payload: Data or json being sent
        :type payload: str
        :param params: Dict of parameters being sent
        :type params: dict
        :param headers: Additional headers being sent
        :type headers: dict
        :returns: Results from GIPHY
        :rtype: dict
        """
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
        """
        Search GIPHY's APIs

        :param query: What to search for
        :type query: str
        :param limit: Amount of items to return per page
        :type limit: int
            :default: 25
        :param offset: Where to start in the total results
        :type offset: int
            :default: 0
        :param lang: What language to send back
        :type lang: str
            :default: en
        :returns: Results from GIPHY
        :rtype: dict
        """
        return self.make_request(
            url=config.giphy["search_endpoint"],
            params={
                "q": query,
                "limit": limit,
                "offset": offset,
                "lang": lang,
            },
        )

    def get(self, gifid):
        """
        Search GIPHY's APIs

        :param query: What to search for
        :type query: str
        :param limit: Amount of items to return per page
        :returns: Results from GIPHY
        :rtype: dict
        """
        return self.make_request(
            url="{}/{}".format(config.giphy["get_endpoint"], gifid)
        )
