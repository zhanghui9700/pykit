#coding=utf-8

import pdb
from django.http import HttpResponse
from pyExcelerator import *

def export_as_xls(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    wb = Workbook()
    ws0 = wb.add_sheet('0')
    col=0
    field_names=[]

    #write header row
    for field in modeladmin.list_display: #opts.fields:
        if len(queryset)>0 and hasattr(queryset[0],field):
            ws0.write(0,col,field)
            field_names.append(field)
            col = col+1
    
    row = 1
    #write data row
    for obj in queryset:
        col = 0
        for field in field_names:
            attr = getattr(obj,field)
            try:
                if callable(attr):
                    val = unicode(str(attr()),'utf-8').strip() 
                else:
                    val = unicode(attr).strip()
            except:
                val = '---'
            ws0.write(row,col,val)
            col = col+1
        row = row+1
    
    xlsPath = u'/tmp/%s_%s.xls' % (request.user.id,modeladmin.model.__name__)
    wb.save(xlsPath)
    response = HttpResponse(open(xlsPath, 'r').read(), mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s.xls' %unicode(opts).replace('.','_')
    return response

def PageList(totalPage,index=1,groupSize=7):
    '''
    totalPage : total page
    index : current page index
    groupSize : the size of page list
    '''
    groupSize = totalPage < groupSize and totalPage or groupSize
    if index <=0 or index > totalPage:
        return range(1,groupSize+1)
    elif totalPage <= groupSize:
        return range(1,totalPage+1)
    else:
        offset = int(groupSize/2)
        start,end = 0,0
        if index - offset <= 0:
            start = 1
            end = start + groupSize
        elif index + offset > totalPage:
            end = totalPage + 1
            start = end - groupSize
        else:
            start = index - offset
            end = index + offset+1
        
        return range(start,end)
