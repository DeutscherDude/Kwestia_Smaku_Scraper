from requests import session
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from psql_settings import postgresql


def get_engine(user, password, host, port, db):
    """Creates a mock connection to the database"""
    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(url, pool_size=50, echo=False)
    return engine

def get_engine_from_settings():
    """Uses settings to create a mock connection to the database"""
    keys = ['pguser', 'pgpass', 'pghost', 'pgport', 'pgdb']
    if not all(key in keys for key in postgresql.keys()):
        raise Exception('Missing keys in postgresql settings')
    
    return get_engine(postgresql['pguser'], 
                      postgresql['pgpass'], 
                      postgresql['pghost'], 
                      postgresql['pgport'], 
                      postgresql['pgdb']) 

def get_session() -> sessionmaker:
    """Creates a session to use the database"""
    engine = get_engine_from_settings()
    session = sessionmaker(bind=engine)
    return session
