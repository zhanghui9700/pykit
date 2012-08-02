#!/usr/bin/env python
#coding=utf-8

import pdb,json,logging

from django.conf import settings
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from qfpay import MY_QFPAY_COM_URL

def manual(request):
    return render_to_response('mis/manual_apply.html',
                              {'MY_URL':u'%s/api/v1/signup' % MY_QFPAY_COM_URL},
                              context_instance=RequestContext(request))
