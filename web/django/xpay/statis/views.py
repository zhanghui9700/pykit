#coding=utf-8

from django.http import HttpResponseRedirect,HttpResponse, HttpResponseForbidden, Http404


CHART_URL = 'https://chart.googleapis.com/chart?'
CHART_TYPE = 'cht=p3&'
CHART_SIZE = 'chs=800x600&'

def tradechart(request):
    url = CHART_URL+CHART_TYPE+CHART_SIZE
    url += 'chd=t:60,40&'
    url += 'chl=Hello|World'

    print url

    return HttpResponseRedirect(url)
