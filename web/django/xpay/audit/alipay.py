# -*- coding: utf-8 -*-  
#!/usr/bin/env python  
import hashlib

class Alipay(object):
    def __init__(self):
        self.params = {}
        # 支付宝gateway   
        self.pay_gate_way = 'https://www.alipay.com/cooperate/gateway.do'
        #self.pay_gate_way = 'https://mapi.alipay.com/gateway.do'
        #self.pay_gate_way = 'https://api.test.alipay.com/cooperate/gateway.do'  
        # 安全码 ***处请填具体安全码  
        self.security_code = 'gs4a2oi8e0brc5i4ttczs81v4xw82t8e'

        #---------------------------------------------------------------------------

        # 根据订单生成支付宝接口URL
    # <<<<< Protocol Param >>>>>  
    # @ input_charset: 编码方式  
    # @ service: 接口名称, 有两种方式 =>  
    #            1. trade_create_by_buyer (担保付款)   
    #            2. create_direct_pay_by_user (直接付款)  
    # @ partner : 商户在支付宝的用户ID  
    # @ show_url: 商品展示网址  
    # @ return_url: 交易付款成功后，显示给客户的页面  
    # @ sign_type: 签名方式  
    #  
    # <<<<< Business Param >>>>>  
    # @ subject: 商品标题  
    # @ body: 商品描述  
    # @ out_trade_no: 交易号（确保在本系统中唯一）  
    # @ price: 商品单价  
    # @ discount: 折扣 -**表示抵扣**元  
    # @ quantity: 购买数量  
    # @ payment_type: 支付类型  
    # @ logistics_type: 物流类型 => 1. POST (平邮) 2. EMS 3. EXPRESS (其他快递)  
    # @ logistics_fee: 物流费  
    # @ logistics_payment: 物流支付类型 =>   
    #                      1. SELLER_PAY (卖家支付) 2. BUYER_PAY (买家支付)  
    # @ seller_email: 卖家支付宝帐户email  
    #   
    # @return   
    #---------------------------------------------------------------------------  
    def create_order_url(self,
                         partner,
                         service,
                         seller_email,
                         show_url,
                         return_url,
                         notify_url,
                         subject,
                         body,
                         out_trade_no,
                         total_fee,
                         #price,
                         #discount=0,
                         #quantity=1,
                         sign_type='MD5',
                         payment_type=1,
                         #logistics_type='express',
                         #logistics_fee=0,
                         #logistics_payment=2,
                         input_charset='utf-8',
                         ):
        self.params['_input_charset'] = input_charset
        self.params['service'] = service
        self.params['partner'] = partner
        #self.params['show_url'] = show_url  
        self.params['return_url'] = return_url
        self.params['notify_url'] = notify_url
        self.params['subject'] = subject
        self.params['body'] = body
        self.params['out_trade_no'] = str(out_trade_no)
        self.params['total_fee'] = str(total_fee)
        #self.params['price'] = str(price)
        #self.params['discount'] = str(discount)
        #self.params['quantity'] = str(quantity)
        self.params['payment_type'] = str(payment_type)
        #self.params['logistics_type'] = logistics_type  
        #self.params['logistics_fee'] = str(logistics_fee)
        #self.params['logistics_payment'] = str(logistics_payment)
        self.params['seller_email'] = seller_email
        # 返回结果  
        return self._create_url(self.params, sign_type)

    def _create_url(self, params, sign_type='MD5'):
        param_keys = params.keys()
        # 支付宝参数要求按照字母顺序排序  
        param_keys.sort()
        # 初始化待签名的数据  
        unsigned_data = ''
        # 生成待签名数据  
        for key in param_keys:
            print key + '=' + params[key]
            unsigned_data += key + '=' + params[key]
            if key != param_keys[-1]:
                unsigned_data += '&'
                # 添加签名密钥
        unsigned_data += self.security_code

        print unsigned_data

        # 计算sign值  
        if sign_type.lower() == 'md5':
            M = hashlib.md5()
            M.update(unsigned_data)
            sign = M.hexdigest()
        else:
            sign = ''
        request_data = self.pay_gate_way + '?'
        for key in param_keys:
            request_data += key + '=' + params[key].decode('utf8').encode(params['_input_charset'])
            request_data += '&'
        request_data += 'sign=' + sign + '&sign_type=' + sign_type.upper()
        # 返回结果  
        return request_data


def test():
    p = Alipay()
    print p.create_order_url(
        '2088002089455812',
        'trade_create_by_buyer',
        'xxx@bb.om',
        '',
        'http://www.return.com',
        '充值',
        '充值',
        1, 100)


def test2():
    pay = Alipay()
    url = pay.create_order_url(
        '2088002089455812',
        'create_direct_pay_by_user',
        'fenyon@126.com',
        '',
        'http://jumayi.com/charge_return',
        'http://jumayi.com/charge_notify',
        'recharge',
        'recharge',
        1, 0.01)
    print url

if __name__ == '__main__':
    test2()


