import requests
from airflow.logging_config import log


class Request(object):
    def __init__(self, **kwargs):
        """

        Args:
            **kwargs:
                site: sec(https://www.sec.gov/) 이곳은 헤더에 이름 및 이메일을 적어야함
        """
        self.set_headers()
        if kwargs.get("site", None) == "SEC":
            self.headers.update({"User-Agent": "test mariat1717@daum.net"})

    def set_headers(self, **kwargs):
        """
        헤더를 세팅하는 함수
        """
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept": "*/*",
        }
        self.headers.update(kwargs)

    def get(self, url, headers: dict = None, params: dict = None):
        if headers is not None:
            self.headers.update(headers)
        return requests.get(url, headers=self.headers, params=params)

    def post(
        self, url: str, headers: dict = None, data: dict = None, payload: dict = None
    ):
        if headers is not None:
            self.headers.update(headers)

        res = requests.post(url, data=data, json=payload, headers=self.headers)

        if res.status_code != 200:
            log.error(
                f"[CODE: {res.status_code}][URL: {url}] 데이터 수집에 오류가 발생했습니다. {res.text}"
            )
            raise
        return res
