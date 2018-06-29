import json
from urllib.parse import urlencode
from urllib.request import urlopen

API_ROOT = "http://www.omdbapi.com/"
API_KEY = "847c88a1"
PLACEHOLDER_POSTER = "https://123-bijles.nl/placeholder.jpg"

class OMDB:

    cache = {}

    def api_call(self, title, year):
        """
            Retreive data from the OMDB server.
        """
        if not title:
            return

        query = {"apikey": API_KEY, "t": title}
        if year:
            query["y"] = str(year)
        query_url = API_ROOT + "?" + urlencode(query)

        req = urlopen(query_url)
        res = json.load(req)

        if "Error" in res:
            return {"Poster": PLACEHOLDER_POSTER, "Plot": "Unknown"}

        self.cache[title.casefold()] = res
        return res

    def get(self, title, year=None):
        """
            Safe implementation of the api_call() function. Returns
            data from the OMDB api.
        """
        title_id = title.casefold()

        if title_id in self.cache.keys():
            return self.cache[title_id]

        return self.api_call(title, year)
