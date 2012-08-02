import types
from django.db import models
#import pyxslt.serialize
from django.utils import simplejson as json
from django.utils.functional import Promise
from django.utils.translation import force_unicode
from django.utils.simplejson import JSONEncoder
from django.core.serializers.json import DateTimeAwareJSONEncoder
from decimal import *
import pdb

class LazyEncoder(DateTimeAwareJSONEncoder):
    def default(self, o):
        if isinstance(o, Promise):
            return force_unicode(o)
        else:
            return super(LazyEncoder, self).default(o)

class DataDumper:
    fields = {}
    def selectObjectFields(self,objectType,fields = []):
        self.fields[objectType] = fields

    def dump(self,data,format='json'):
        """
        The main issues with django's default json serializer is that properties that
        had been added to a object dynamically are being ignored (and it also has 
        problems with some models).
        """
    
        def _any(data):
            ret = None
            if type(data) is types.ListType:
                ret = _list(data)
            elif type(data) is types.DictType:
                ret = _dict(data)
            elif isinstance(data, Decimal):
                # json.dumps() cant handle Decimal
                ret = str(data)
            elif isinstance(data, models.query.QuerySet):
                # Actually its the same as a list ...
                ret = _list(data)
            elif isinstance(data, models.Model):
                ret = _model(data)
            elif type(data) is types.MethodType:
                ret = _any(data())
            else:
                ret = data
            return ret
        
        def _model(data):
            
            ret = {}
            # If we only have a model, we only want to encode the fields.
            objType = data.__class__.__name__
            
            for f in data._meta.fields:
                if (self.fields[objType]) and (f.attname in self.fields[objType]):
                    ret[f.attname] = _any(getattr(data, f.attname))
            '''
            for f in dir(data):
                if (self.fields[objType]) and (f in self.fields[objType]):
                    ret[f] = _any(getattr(data,f))
            '''
            # And additionally encode arbitrary properties that had been added.
            
            fields = dir(data.__class__) + ret.keys()
            add_ons = [k for k in dir(data) if k not in ret.keys()]
            for k in add_ons:
                if (self.fields[objType]) and (k in self.fields[objType]):
                    ret[k] = _any(getattr(data, k))
            return ret
        def _list(data):
            ret = []
            for v in data:
                ret.append(_any(v))
            return ret
        
        def _dict(data):
            ret = {}
            for k,v in data.items():
                ret[k] = _any(v)
            return ret
        
        ret = _any(data)
        if(format == 'xml'):
            return ''
            #return pyxslt.serialize.toString(prettyPrintXml=False,data=ret,)
        else:
            return json.dumps(ret, cls=LazyEncoder)
            #return json.dumps(ret, cls=DateTimeAwareJSONEncoder)

