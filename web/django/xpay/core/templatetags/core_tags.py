#coding=utf-8

from django import template

register = template.Library()

@register.filter
def get_money(money):  #计算出结算记录的总共手续费
    try:
        m = int(money)/100.0
    except:
        m = 0
    str_money = "%.2f" %(m)
    return str_money

