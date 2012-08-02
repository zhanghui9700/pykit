# Create your views here.

import logging
from django.template import RequestContext
from django.http import HttpResponseRedirect, \
                        HttpResponse,HttpResponseForbidden,Http404
from django.contrib.auth.decorators import user_passes_test, login_required 
from django.conf import settings
from django.contrib.auth.models import User
from util.DataDumper import DataDumper

dumper = DataDumper()
dumper.selectObjectFields('Item',['id','user','name','price','photo','date','amount','status'])
dumper.selectObjectFields('Order',['id','user','sum','mobile','email','date','list','desc'])

def items(request):
    items = Item.objects.filter(user=request.user)
    jsdata = dumper.dump({'success':True,'items':items,'user':request.user})
    return HttpResponse(jsdata,mimetype="application/x-javascript")

def add_item(request):
    if request.method == 'POST':
        name,price,amount,photo = request.POST.get('name').request.POST.get('price'),request.POST.get('amount'),request.FILES.get('photo')
        item = Item(user=request.user,name=name,price=price,amount=amount,photo=photo)
        item.save()
        jsdata = dumper.dump({'success':True,'item':item})
        return HttpResponse(jsdata,mimetype="application/x-javascript")

def update_item(request):
    pass

def delete_item(request):
    pass

def order(request):
    pass

def orders(request):
    order = order.objects.filter(user=request.user)
    jsdata = dumper.dump({'success':True,'orders':orders,'user':request.user})
    return HttpResponse(jsdata,mimetype="application/x-javascript")

def add_order(request):
    if request.method == 'POST':
        name,sum,mobile,email,list,desc = request.POST.get('name').request.POST.get('sum'),request.POST.get('mobile'),request.POST.get('email'),
        request.POST.get('list'),request.POST.get('desc')
        order = Order(user=request.user,sum=sum,mobile=mobile,email=email,list=list,desc=desc)
        jsdata = dumper.dump({'success':True,'order':order})
        return HttpResponse(jsdata,mimetype="application/x-javascript")
        
