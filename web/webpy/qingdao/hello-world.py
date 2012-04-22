#-*- coding=utf-8 -*-

import pdb
import web

urls = (
    '/(.*)','index'
)

app = web.application(urls,globals())

class index:
    def GET(self,name):
        #pdb.set_trace()
        if name is None or len(name)==0:
            name = 'world'

        return 'hello ' + name + '!'

if __name__ == '__main__':
    app.run()
