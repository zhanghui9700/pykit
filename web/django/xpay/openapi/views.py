# Create your views here.
from django.http import HttpResponseRedirect, \
    HttpResponse, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.utils.decorators import available_attrs
import pdb,json,datetime,time,types


def init(request):
    return HttpResponse(json.dumps({'ret':True, 'msg':'Fuck Django'}))



def payment(*args, **kwargs):
    pass
