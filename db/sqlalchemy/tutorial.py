#!/usr/bin/env python
#-*-coding=utf-8-*-

'''
http://docs.sqlalchemy.org/en/rel_0_5/ormtutorial.html
http://docs.sqlalchemy.org/en/rel_0_6/core/engines.html
'''
from sqlalchemy import __version__, create_engine

print 'sqlalchemy.version:',__version__

#absiolute path
engine = create_engine("sqlite:////home/zhanghui/temp/tutorial.db",echo=True)
#relatie path
#engine = create_engine("sqlite:///../tutorial.db",echo=True)

from sqlalchemy import Table,Column,Integer,String,MetaData,ForeignKey

metadata = MetaData()

#define a table
t_users = Table('users',metadata,
        Column('user_id',Integer,primary_key=True),
        Column('name',String),
        Column('age',Integer),
        Column('passwd',String)
)

metadata.create_all(engine)

#define an object 
class User(object):
    def __init__(self,name,age,passwd):
        self.name = name
        self.age = age
        self.passwd = passwd

    def __repr__(self):
        return "<User(%s,%s,%s)>"%(self.name,self.age,self.passwd)

#map an object to a table
from sqlalchemy.orm import mapper
mapper(User,t_users)

u = User(name="python",age=18,passwd="amigO123")
print u

#define an table,object,map all in one declaratively
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Author(Base):
    __table__ = 'authors'

    id = Column(Integer,primary_key=True)
    name = Column(String)
    fullname = Column(String)
    passwd = Column(String)

    def __init__(self,name,fullname,passwd):
        self.name = name
        self.fullname = fullname
        self.passwd = passwd

    def __repr__(self):
        return "<Author(%s,%s,%s)>"%(self.name,self.fullname,self.passwd)

print Author.__table__
#print Base.metadata


#
#
#u = users.insert()
#u.execute(name='Mary',age=30,passwd='scoot')
#
#u.execute({name:'Mary1',age:31,passwd:'scoot'},
#        {name:'Mary2',age:32,passwd:'scoot'},
#        {name:'Mary3',age:33,passwd:'scoot'},
#)
#
#us = users.select()
#rs = us.execute()
#
#row = rs.fetchone()
#print 'id:',row[0]
#print 'name:',row['name']
#print 'age:',row.age
#print 'passwd:',row[users.c.passwd]
#
#for row in rs:
#    print row.name,' is ',row.age,' yeard old!'
