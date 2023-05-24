from utils.invertible_dict import InvertibleDict

class Connection:
    connected_ips = InvertibleDict()
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = object.__new__(cls)
            cls.instance.__initialized = False
        return cls.instance

    def __init__(self):
        if self.__initialized: return
        self.__initialized = True