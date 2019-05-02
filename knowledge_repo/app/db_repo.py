
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
import os
class DBSession:

    def __init__(self):
        KR_REPO_DB_URI = os.environ['KR_REPO_DB_URI']
        KR_REPO_DB_USER = os.environ['KR_REPO_DB_USER']
        KR_REPO_DB_PWD = os.environ['KR_REPO_DB_PWD']
        KR_REPO_DB_PORT = os.environ['KR_REPO_DB_PORT']
        KR_APP_DB_URI = os.environ['KR_APP_DB_URI']
        KR_REPO_DB_NAME = os.environ['KR_REPO_DB_NAME']


    
        repo_db_conn = u'mysql+mysqlconnector://%s:%s@%s:%s/%s'%(KR_REPO_DB_USER,KR_REPO_DB_PWD,KR_REPO_DB_URI,KR_REPO_DB_PORT,KR_REPO_DB_NAME)
        self.__engine = create_engine(repo_db_conn,pool_recycle=3600,pool_size=300, max_overflow =100, pool_pre_ping=True)
        self.__session = sessionmaker(bind = self.__engine)
    def session(self):
        return self.__session

    def engine(self):
        return self.__engine

