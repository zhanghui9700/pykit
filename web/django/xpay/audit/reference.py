def recharge(request):
    p = request.user.get_profile()
    if request.method == 'GET':
        return render_to_response('recharge.html',
                {'profile': profile_point(p), },
            context_instance=RequestContext(request))
    elif request.method == 'POST':
        num = float(request.POST.get('money', 0))
        if num <= 0:
            return render_to_response('recharge.html',
                    {'profile': profile_point(p), 'error': u'金额必须大于0'},
                context_instance=RequestContext(request))
        else:
            r = Recharge.objects.create(user=request.user, money=num)
            pay = alipay.Alipay()
            url = pay.create_order_url(
                '2088002089455812',
                'create_direct_pay_by_user',
                'fenyon@126.com',
                '',
                settings.SITE_NAME + '/charge_return',
                settings.SITE_NAME + '/charge_notify',
                'recharge',
                'recharge',
                r.id, num)
            logging.info(url)
            return HttpResponseRedirect(url)


def charge_notify(request):
    seller = request.POST['seller_email']
    no = request.POST['out_trade_no']
    trade_status = request.POST['trade_status']

    logging.info('alipay notify: seller:%s trade_no:%s status:%s' % (seller, no, trade_status))

    if trade_status == 'TRADE_FINISHED':
        r = Recharge.objects.get(id=no)
        r.notify = str(datetime.datetime.now())
        r.email = seller
        r.status = 1
        r.save()

    return HttpResponse('success')


def charge_return(request):
    issuc = request.GET['is_success']
    total = request.GET['total_fee']
    buyer = request.GET['buyer_email']
    seller = request.GET['seller_email']

    if issuc == 'T':
        s = u'<div style="padding:10px;width:300px;border:1px solid #cccccc;">支付宝交易成功! 金额:' + total + u'</div>'
        return HttpResponse(s)
    else:
        s = u'<div style="padding:10px;width:300px;border:1px solid #cccccc;">支付宝交易失败!</div>'
        return HttpResponse(s)
