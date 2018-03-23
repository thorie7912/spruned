import os

import leveldb
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import threading
from functools import wraps
from spruned.application import settings

Base = declarative_base()


class Header(Base):
    __tablename__ = 'headers'
    id = Column(Integer, primary_key=True)
    blockheight = Column(Integer, index=True, unique=True)
    blockhash = Column(String, index=True, unique=True)
    data = Column(String)


engine = create_engine('sqlite:///' + settings.SQLITE_DBNAME)
if not settings.SQLITE_DBNAME or os.path.exists(settings.SQLITE_DBNAME):
    Base.metadata.create_all(engine)

sqlite = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

storage_ldb = leveldb.LevelDB(settings.LEVELDB_BLOCKCHAIN_ADDRESS)
cache_ldb = leveldb.LevelDB(settings.LEVELDB_CACHE_ADDRESS)

_local = threading.local()
_local.session = sqlite
_local.storage_ldb = storage_ldb
_local.cache_ldb = cache_ldb


def atomic(fun):
    @wraps(fun)
    def decorator(*args, **kwargs):
        try:
            try:
                _local.counter += 1
            except AttributeError:
                _local.counter = 1
            r = fun(*args, **kwargs)
            if _local.counter == 1:
                _local.session.commit()
                _local.counter -= 1
            return r
        except Exception as e:
            if _local.counter == 1:
                _local.session.rollback()
                _local.counter -= 1
            raise e
        finally:
            _local.session.close()
    return decorator


def ldb_batch(fun):
    @wraps(fun)
    def decorator(*args, **kwargs):
        try:
            _local.leveldb_counter += 1
        except AttributeError:
            _local.leveldb_counter = 1
        if _local.leveldb_counter == 1:
            _local.current_batch = leveldb.WriteBatch()
        r = fun(*args, **kwargs)
        if _local.leveldb_counter == 1:
            _local.storage_ldb.Write(_local.current_batch)
            _local.current_batch = None
            _local.leveldb_counter -= 1
        return r
    return decorator
