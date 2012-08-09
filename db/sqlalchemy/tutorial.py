#!/usr/bin/env python
#-*-coding=utf-8-*-

'''
http://docs.sqlalchemy.org/en/rel_0_5/ormtutorial.html
http://docs.sqlalchemy.org/en/rel_0_6/core/engines.html
'''
from sqlalchemy import __version__, create_engine

print 'sqlalchemy.version:',__version__

#absiolute path
#engine = create_engine("sqlite:////home/zhanghui/temp/tutorial.db",echo=True)
#relatie path
engine = create_engine("sqlite:///../tutorial.db",echo=True)
from sqlalchemy import Table,Column,Integer,String,MetaData,ForeignKey

metadata = MetaData()

users = Table('users',metadata,
        Column('user_id',Integer,primary_key=True),
        Column('name',String),
        Column('age',Integer),
        Column('passwd',String)
)

metadata.create_all(engine)
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
