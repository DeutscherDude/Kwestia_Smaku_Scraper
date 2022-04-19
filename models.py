from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    ingredients = Column(String)
    preparation = Column(String)
    tags = Column(String)

    def __repr__(self):
        return "<Recipe(name='%s', ingredients='%s', preparation='%s', tags='%s')>" % (self.name, self.ingredients, self.preparation, self.tags)

def recreate_database(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)