from abc import abstractmethod, ABC, ABCMeta

class SingletonMeta(ABCMeta):
    """
    싱글톤 패턴을 적용하는 메타클래스입니다.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]