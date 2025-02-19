import requests

class Request(object):

    def __init__(self, **kwargs):
        """

        Args:
            **kwargs:
                site: sec(https://www.sec.gov/) 이곳은 헤더에 이름 및 이메일을 적어야함
        """
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept": "*/*"
        }
        if kwargs.get('site', None) == "SEC":
            self.headers.update({"User-Agent": "test mariat1717@daum.net"})

    def get(self, url, headers: dict = {}):
        self.headers.update(headers)
        return requests.get(url, headers=self.headers)

    def post(self, url, data, headers: dict = {}):
        self.headers.update(headers)
        return requests.post(url, data=data, headers=self.headers)
