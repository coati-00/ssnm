import  os, os.path, sys
from cStringIO import StringIO
from urllib import urlencode

os.chdir(os.path.normpath(os.path.dirname(__file__)))


from mod_python import apache, Cookie
from httplib import UnimplementedFileMode,HTTPResponse,HTTPConnection


#-------------------------------------------
#private for cherrypy
#-------------------------------------------
import cherrypy
from cherrypy._cphttpserver import  CherryHTTPRequestHandler

#-------------------------------------------
#Need for website
import website
if hasattr(cherrypy,'root'):
	pass
else:
	website.start(1)  #1----initOnly
#-------------------------------------------


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


def mylogfile(txt):
	fp=open('/tmp/cp.log','a')
	fp.write(txt)
	fp.close()


class FakeHTTPRequest(HTTPConnection):
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
	def close(self):
		self.sock=None
		if self.__response:
			self.__response = None
		self.__state = None
	def putrequest(self, method, url, skip_host=0):
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



class RequestHandler(CherryHTTPRequestHandler):

	#------------------------------
	def _w_send_response(self, resp):
		code=resp.status
		message=resp.reason
		self._request.status = code
	def _w_send_header(self, key, value):
		self._request.headers_out.add(key, str(value))
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
		t=cx.getRequest()
		fp=open('/tmp/cp.log','a')
		fp.write(t)
		fp.close()
		self.rfile=StringIO(t)
	def _setResponse(self):
		resp =HTTPResponse(FakeSocket(self.wfile.getvalue()), 1)
		resp.begin()
		self._w_send_response(resp)
		self._w_turn_header(resp)
		self._w_end_header()
		self._w_send_body(resp)
		resp.close()


def handler(request):
	cherrypy_handler = RequestHandler(request,None,None)
	request.content_type = cherrypy_handler.ContentType
	response = cherrypy_handler.wfile.getvalue()
	request.write(response)
	return apache.OK
