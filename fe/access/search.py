import requests
import simplejson
from urllib.parse import urljoin

class Search:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "search/")

    def search_only_store(self, choose: int, store_id: str, keyword: str, page: int, limit: int):
        json = {
            "choose": choose,
            "store_id": store_id,
            "keyword": keyword,
            "page": page,
            "limit": limit
        }
        url = urljoin(self.url_prefix, "search_only_store")
        r = requests.post(url, json=json)
        data = r.json()
        code = r.status_code
        message = data.get("message")
        result = data.get("result")
        return code, message, result

    def search_all(self, choose: int, keyword: str, page: int, limit: int):
        json = {
            "choose": choose,
            "keyword": keyword,
            "page": page,
            "limit": limit
        }
        url = urljoin(self.url_prefix, "search_all")
        r = requests.post(url, json=json)
        data = r.json()
        code = r.status_code
        message = data.get("message")
        result = data.get("result")
        return code, message, result

    def get_detail_info(self, book_id):
        json = {
            "book_id": book_id
        }
        url = urljoin(self.url_prefix, "get_detail_info")
        r = requests.post(url, json=json)
        data = r.json()
        code = r.status_code
        message = data.get("message")
        result = data.get("result")
        return code, message, result