import abc


class RPCAPIService(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def getblock(self, blockhash):
        pass  # pragma: no cover

    @abc.abstractmethod
    def getrawtransaction(self, txid, **kwargs):
        pass  # pragma: no cover

    @property
    @abc.abstractmethod
    def available(self) -> bool:
        pass  # pragma: no cover


class StorageInterface(metaclass=abc.ABCMeta):
    def set(self, *a, ttl: int=0):
        pass  # pragma: no cover

    def get(self, *a):
        pass  # pragma: no cover

    def remove(self, *a):
        pass  # pragma: no cover
