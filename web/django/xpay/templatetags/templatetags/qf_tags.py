#!/bin/bash python
#-*-coding=utf-8-*-

import pdb

from django import template
from django.template import Library,Node,TemplateSyntaxError
from django.template import Variable,resolve_variable
from django.core.urlresolvers import reverse
from django.contrib.admin.models import User

GROUP_HEADER = {
    '10003':'''<div class="header"><a class="logo_shenma" href="#">神州数码</a><p>小微商户移动支付系统</p></div>''',
    'default':'''<div class="header"><a class="logo" href="#"></a></div>'''
}

GROUP_NAME_ID = {
    'smsh':'10003',
    'default':'default'
}

def qf_tags_header(parser,token):
    try:
        tag_name,user,group = token.split_contents()
    except ValueError,e:
        pass

    return HeaderLogoNode(user,group)

class HeaderLogoNode(Node):
    def __init__(self,user,group):
        self.user = template.Variable(user)
        self.group = template.Variable(group)

    def render(self,context):
        try:
            from audit.models import Apply
            from util.define import GROUP_ID
        except ImportError:
            pass
        
        user,group = None,'default'
        try: user,group = self.user.resolve(context),self.group.resolve(context)
        except Exception,ex:pass
        if isinstance(user,User) and user.is_authenticated():
            try:
                group = str(Apply.objects.get(user=user.id).groupid)
            except:pass
        else:
            group = GROUP_NAME_ID.get(group,'default')

        return GROUP_HEADER.get(group,GROUP_HEADER.get('default'))
        
register = Library()
register.tag('qf_tags_header',qf_tags_header)
