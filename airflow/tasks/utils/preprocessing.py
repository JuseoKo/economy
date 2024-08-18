
def uniq_code_prep(country: str, symbol: str, s_type: str) -> str:
    """
    유니크코드를 생성하는 함수입니다.
    Args:
        country: US/
        symbol: APPL 등
        s_type: ETF/ETN/STOCK/INDEX 등
    Returns:

    """
    return f"{country}_{s_type}_{symbol}"
