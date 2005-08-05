#!/usr/bin/python
# -*- coding:utf-8 -*-
from cStringIO import StringIO
from httplib import UnimplementedFileMode,HTTPResponse,HTTPConnection

import cherrypy
from cherrypy._cphttpserver import  CherryHTTPRequestHandler


class EmptyClass:
    pass


class FakeSocket:
    def __init__(self, text=None, fileclass=StringIO):
        self.text = text
        self.fileclass = fileclass
        self.data= ''
    def makefile(self, mode, bufsize=None):
        if mode != 'r' and mode != 'rb':
            raise UnimplementedFileMode()
        return self.fileclass(self.text)

    def sendall(self,*args,**kwargs):
        self.data+=args[0]
    def getData(self):
        return self.data



class FakeHTTPResponse(HTTPResponse):
    debuglevel=0



class FakeHTTPRequest(HTTPConnection):
    debuglevel=0
    def __init__(self, host=None, port=None, strict=None):
        self.sock = None
        self._buffer = []
        self.__response = None
        self.__state = None
        self._method = None
        if strict is not None:
            self.strict = strict
    def connect(self):
        self.sock=FakeSocket()
        self.set_debuglevel(0)
    def close(self):
        self.sock=None
        print self.debuglevel
        if self.__response:
            self.__response = None
        self.__state = None
    def putrequest(self, method, url, **skips):
        self._method = method
        if not url:
            url = '/'
        str = '%s %s %s' % (method, url, self._http_vsn_str)
        self._output(str)
    def putheader(self, header, value):
        str = '%s: %s' % (header, value)
        self._output(str)
    def endheaders(self):
        self._send_output()
    def send(self, str):
        if self.sock is None:
            self.connect()
        self.sock.sendall(str)
    #--------------------------
    def getRequest(self):
        return self.sock.getData()

class FakeRequest:
    def __init__(self):
        self.headers_out={
            'Date':'Thu, 28 Apr 2005 04:31:23 GMT',
            'Server':'Microsoft-IIS/6.0',
            'Content-Type':'text/html; charset=utf-8',
            'Content-Length':'3209',
            }
        self.headers_in={
            'Accept':'image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, application/x-shockwave-flash, application/vnd.ms-excel, application/vnd.ms-powerpoint, application/msword, */*',
            'Accept-Language':'zh-cn',
            'Accept-Encoding':'gzip, deflate',
            'User-Agent':' Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322)',
            'Host':'www.donews.net',
            'Connection':'Keep-Alive',
            #'Cookie':'CommentUser=Name=python&Url=; Q=q1=AACAAAAAAAAAcw--&q2=Qm4kOQ--',
            }
        self.method='GET'
        self.body=''
        self.connection=EmptyClass()
        self.connection.remote_addr=['127.0.0.1',0]
        self.unparsed_uri='/'
    def read(self,l):
        if l>0:
            result=self.body[:l]
        else:
            result=self.body
        return result



class RequestHandler(CherryHTTPRequestHandler):

    #------------------------------
    def _w_send_response(self, resp):
        code=resp.status
        message=resp.reason
        self._request.status = code
        #print self._request.status
        #print message
        return code,message
    def _w_send_header(self, key, value):
        self._request.headers_out[key] = str(value)
    def _w_turn_header(self,resp):
        self.ContentType = 'text/plain' # default
        if hasattr(resp.msg, 'headers'):
            for header in resp.msg.headers:
                k,v = header.split(':',1)
                k,v = k.strip(),v.strip()
                self._w_send_header(k,v)
                if header.lower().startswith('content-type'):
                    self.ContentType = v
    def _w_end_header(self):
        pass
    def _w_send_body(self,resp):
        self.wfile= StringIO()
        self.wfile.write(resp.read())
    #---------------------------------
    def _r_get_headers(self):
        request=self._request
        command = request.method
        headers = dict(request.headers_in)
        body = ""
        if command == 'POST':
            body=self._request.read(-1)
            headers['Content-length'] = len(body)
        return command,headers,body
    #---------------------------------
    def setup(self):
        self._request=self.request
        if self.client_address is None:
            self.client_address=self._request.connection.remote_addr
        if self.server is None:
            self.server=None
        try:
            #CherryHTTPRequestHandler.setup(self)
            pass
        except:
            pass
        self.wfile=StringIO()
        self.rfile=StringIO()
        self._setRequest()
    def finish(self):
        self._setResponse()
    #---------------------------------
    def _setRequest(self):
        cx = FakeHTTPRequest()
        request=self._request
        path= request.unparsed_uri
        command,headers,body=self._r_get_headers()
        cx.request(command, path, body, headers)
        self.rfile=StringIO(cx.getRequest())
    def _setResponse(self):
        resp =FakeHTTPResponse(FakeSocket(self.wfile.getvalue()), 0)
        resp.begin()
        self.mystatus=self._w_send_response(resp)
        self._w_turn_header(resp)
        self._w_end_header()
        self._w_send_body(resp)
        resp.close()


class ServerCherrypy:
    def __init__(self,startfunc,request=None):
        startfunc(1)
        self.setRequestClass(request)
    def setRequestClass(self,request):
        if request is None:
            self.request=FakeRequest()
        else:
            self.request=request
    #----------------------------
    def setDefaultHeader(self):
        self.setHeader('Accept','image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, application/x-shockwave-flash, application/vnd.ms-excel, application/vnd.ms-powerpoint, application/msword, */*')
        self.setHeader('Accept-Language','zh-cn')
        self.setHeader('Accept-Encoding','gzip, deflate')
        self.setHeader('User-Agent',' Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322)')
    #----------------------------
    def setHeader(self,key,value):
        self.request.headers_in[key]=value
    def setCookieString(self,value):
        self.setHeader('Cookie',value)
    def setCookie(self,value):  #todo
        self.setHeader('Cookie',value)
    def setRequest(self,key,value):
        setattr(self.request,key,value)
    def setClientIP(self,value):
        self.request.connection.remote_addr=[value,1234]
    def setPath(self,value):
        self.setRequest('unparsed_uri',value)
    def setBody(self,value):
        self.setRequest('body',value)
    #----------------------------
    def getRequest(self):
        return self.response.rfile.getvalue()
    #----------------------------
    def getType(self):
        return self.response.ContentType
    def getHeaderDict(self):
        return self.response.request.headers_out
    def getHeader(self,key):
        try:
            result=self.response.request.headers_out[key]
        except:
            result=None
        return result
    def getStatus(self):
        return self.response.mystatus
    def getResponse(self):
        return self.response.wfile.getvalue()
    def getCookie(self):
        return self.getHeader('Cookie')
    def getSetCookieString(self):
        return self.getHeader('Set-Cookie')
    def getSetCookieString(self):
        return self.getHeader('Set-Cookie')  #todo
    #----------------------------
    def execute(self):
        self.response = RequestHandler(self.request,None,None)
