#coding=utf-8
from django.conf import settings

DB_APP_MAPS = {'audit':'mis',
               'auth':'default',
               'client':'default',
               'core':'default',
               'mis':'mis',
               'risk':'risk',
               'trade':'trade', 
               'settle':'settle'}

class QfAppRoute(object):
    '''
    多数据库路由策略
    默认Model数据库选择由app(app_label)指定
    如果一个App下的ModelA和ModelB需要访问不同的DB
    那么请在Model的Meta Class内容通过db_tablespace指定
    如果db_tablespace为None，则使用App设定
    '''
    def db_for_read(self, model, **hints):
        '''
        get a db for read
        '''
        return self.db_for_write(model,**hints)

    def db_for_write(self, model, **hints):
        '''
        get a db for write
        '''
        dbSetting = model._meta.db_tablespace
        if dbSetting not in settings.DATABASES.keys():
            if DB_APP_MAPS.has_key(model._meta.app_label):
                return DB_APP_MAPS[model._meta.app_label]
        else:
            return dbSetting
        
        return None

    def allow_relation(self, obj1,obj2, **hints):
        '''
        what's this?!
        '''
        db1 = self.db_for_write(obj1,**hints)
        db2 = self.db_for_write(obj2,**hints)
        
        if db1 == db2:
            return True
        return None

    def allow_syncdb(self, db, model):
        '''
        what''s this!?
        '''
        modelUsingDB = self.db_for_write(model)
        if db in DB_APP_MAPS.values():
            return  db == modelUsingDB

        return None
            
