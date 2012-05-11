#!/bin/bash python
#-*- coding=utf-8 -*-
'''
Python 标准库中有很多实用的工具类，但是在具体使用时，标准库文档上对使用细节描述的并不清楚，比如 urllib2 这个 HTTP 客户端库。这里总结了一些 urllib2 库的使用细节。
1 Proxy 的设置
2 Timeout 设置
3 在 HTTP Request 中加入特定的 Header
4 Redirect
5 Cookie
6 使用 HTTP 的 PUT 和 DELETE 方法
7 得到 HTTP 的返回码
8 Debug Log
'''

import urllib2

def test_proxy(enable_proxy=True):
    '''
    urllib2 默认会使用环境变量 http_proxy 来设置 HTTP Proxy。如果想在程序中明确控制 Proxy，而不受环境变量的影响，可以使用下面的方式.
    这里要注意的一个细节，使用 urllib2.install_opener() 会设置 urllib2 的全局 opener。这样后面的使用会很方便，但不能做更细粒度的控制，比如想在程序中使用两个不同的 Proxy 设置等。比较好的做法是不使用 install_opener 去更改全局的设置，而只是直接调用 opener 的 open 方法代替全局的 urlopen 方法。
    '''
    proxy_handler = urllib2.ProxyHandler({'http':'http://www.baidu.com/'})
    null_proxy_handler = urllib2.ProxyHandler({})
    if enable_proxy:
        opener = urllib2.build_opener(proxy_handler)
    else:
        opener = urllib2.build_opener(null_proxy_handler)

    urllib2.install_opener(opener)

def test_timeout(timeout=10):
    '''
    在老版本中，urllib2 的 API 并没有暴露 Timeout 的设置，要设置 Timeout 值，只能更改 Socket 的全局 Timeout 值。 
    在新的 Python 2.6 版本中，超时可以通过 urllib2.urlopen() 的 timeout 参数直接设置。
    '''
    urllib2.socket.setdefaulttimeout(timeout)
    #socket.setdefaulttimeout(10)
    #response = urllib2.urlopen('http://www.facebook.com/',timeout=10)

def test_httpheader(url):
    '''
    要加入 Header，需要使用 Request 对象
    对有些 header 要特别留意，Server 端会针对这些 header 做检查

    User-Agent 有些 Server 或 Proxy 会检查该值，用来判断是否是浏览器发起的 Request
    Content-Type 在使用 REST 接口时，Server 会检查该值，用来确定 HTTP Body 中的内容该怎样解析。

    常见的取值有：
    application/xml ：在 XML RPC，如 RESTful/SOAP 调用时使用
    application/json ：在 JSON RPC 调用时使用

    application/x-www-form-urlencoded ：浏览器提交 Web 表单时使用
    ……

    在使用 RPC 调用 Server 提供的 RESTful 或 SOAP 服务时， Content-Type 设置错误会导致 Server 拒绝服务。

    '''
    request = urllib2.Request(url)
    request.add_header('User-Agent','fake-client')
    response = urllib2.urlopen(request)

def test_redirect(url):
    '''
    urllib2 默认情况下会针对 3xx HTTP 返回码自动进行 Redirect 动作，无需人工配置。要检测是否发生了 Redirect 动作，只要检查一下 Response 的 URL 和 Request 的 URL 是否一致就可以了。
    如果不想自动 Redirect，除了使用更低层次的 httplib 库之外，还可以使用自定义的 HTTPRedirectHandler 类。 
    '''
    response = urllib2.urlopen(url)
    is_redirected = response.geturl() == url
    
    class RedirectHandler(urllib2.HTTPRedirectHandler):
        def http_error_301(self,req,fp,code,msg,headers):
            pass
        def http_error_302(self,req,fp,code,msg,headers):
            pass
    opener = urllib2.build_opener(RedirectHandler)
    opener.open(url)

def test_cookie(url):
    '''
    urllib2 对 Cookie 的处理也是自动的。如果需要得到某个 Cookie 项的值，可以这么做
    '''
    import cookielib
    cookie = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    response = opener.open(url)
    for item in cookie:
        if item.name == 'xxx':
            print item.value

def test_http_put_delete(url,data=None):
    '''
    urllib2 只支持 HTTP 的 GET 和 POST 方法，如果要使用 HTTP PUT 和 DELETE，只能使用比较低层的 httplib 库。虽然如此，我们还是能通过下面的方式，使 urllib2 能够发出 HTTP PUT 或 DELETE 的包,这种做法虽然属于 Hack 的方式，但实际使用起来也没什么问题。
    '''
    request = urllib2.Request(url,data=data)
    request,get_method = lambda:'PUT' #or delete
    response = urllib2.open(request)

def test_http_status_code(url):
    '''
    对于 200 OK 来说，只要使用 urlopen 返回的 response 对象的 getcode() 方法就可以得到 HTTP 的返回码。但对其它返回码来说，urlopen 会抛出异常。这时候，就要检查异常对象的 code 属性了
    '''
    try:
        reponse = urllib2.urlopen(url)
    except urllib2.HTTPError,e:
        print e.code

def test_debug_log(url):
    '''
    使用 urllib2 时，可以通过下面的方法把 Debug Log 打开，这样收发包的内容就会在屏幕上打印出来，方便我们调试，在一定程度上可以省去抓包的工作。
    '''
    httpHandler = urllib2.HTTPHandler(debuglevel=1)
    httpsHandler = urllib2.HTTPSHandler(debuglevel=1)
    opener = urllib2.build_opener(httpHandler,httpsHandler)

    urllib2.install_opener(opener)
    response=urllib2.urlopen(url)
    print '-'*30
    import pprint as p
    print p.pprint(response.__dict__)
    print response.readlines()

if __name__ == '__main__':
    url = 'http://www.baidu.com/'
    urllib2.socket.setdefaulttimeout(6)
    #test_proxy()
    #test_timeout()
    #test_http_header()
    #test_redirect()
    #test_cookie()
    #test_http_put_delete()
    #test_http_status_code()
    test_debug_log(url)

    print 'done...'
