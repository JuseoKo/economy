import os
from dotenv import load_dotenv
import zipfile
import io
import pickle
from typing import Any
import pandas as pd
import chardet

def setings_env() -> None:
    """
    루트 경로에 있는 env 파일을 로드하는 함수
    """
    env_path = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    load_dotenv(f"{env_path}/.env")
    print(env_path)
    return None

def load_zip_file_to_text(file_bytes: io.BytesIO, encoding: str=None) -> list:
    """
    zip 파일 내부에 있는 text 파일을 압축해제해여 데이터 리스트에 담아 반환하는 함수
    """
    datas = []
    # ZIP 파일 열기
    with zipfile.ZipFile(file_bytes, 'r') as z:
        # ZIP 내부 파일 목록 확인
        file_list = z.namelist()
        # 디코딩

        for file_name in file_list:
            with z.open(file_name) as file:

                # 인코딩 자동 감지
                if encoding is None:
                    raw_data = file.read()
                    encoding = chardet.detect(raw_data)['encoding']
                    file.seek(0)

                datas.append({"name": file_name.encode('cp437').decode('EUC-KR', 'ignore'), "data": file.read().decode(encoding)})
    return datas

def detect_encoding(file):
    """
    파일을 바이너리 모드로 읽어서 인코딩을 감지하는 함수
    """
    raw_data = file.read()
    result = chardet.detect(raw_data)
    file.seek(0)  # 파일 포인터를 다시 처음으로 돌려줌
    return result['encoding']


def save_pickle(data: Any) -> None:
    """
    데이터를 pickle로 저장하는 함수
    """
    with open("data.pkl", "wb") as f:
        pickle.dump(data, f)

def load_pickle(path: str = "data.pkl") -> Any:
    with open(path, "rb") as f:
        loaded_data = pickle.load(f)

    return loaded_data