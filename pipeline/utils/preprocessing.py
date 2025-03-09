import pandas as pd

def create_ucode(country: str, symbol: str) -> str:
    """
    유니크코드를 생성하는 함수입니다.
    Args:
        country: US/KR
        symbol: APPL/098120 등
        s_type: ETF/ETN/STOCK/INDEX 등
    Returns:

    """
    return f"{country}_{symbol}"


def convert_numeric(numeric_cols: list, data: pd.DataFrame):
    """
    수치형 컬럼을 숫자형으로 변환하는 함수입니다.
    """
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col].str.replace(',', '', regex=False), errors='coerce')
    return data
