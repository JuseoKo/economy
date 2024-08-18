import time
import random

def time_sleep(min: int = 1, max: int = 3):
    """
    min ~ max 사이 랜덤으로 슬립하는 함수입니다. 기본값은 1 ~ 3초입니다.
    Args:
        min:
        max:
    Returns:

    """
    time.sleep(random.uniform(min, max))