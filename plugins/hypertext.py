#!/usr/bin/env python3

'''
This file is part of Magpie, an automated checking framework with multiple 
submission forms; it was originally built for automatic grading, but has many
more potential uses than that.

Copyright 2013 Joseph Lewis <joehms22@gmail.com> | <joseph@josephlewis.net>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above
  copyright notice, this list of conditions and the following disclaimer
  in the documentation and/or other materials provided with the
  distribution.
* Neither the name of the  nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
try:
	from http.server import HTTPServer
	from http.server import BaseHTTPRequestHandler
	import socketserver
except Exception: # python 2
	print("using backup")
	from BaseHTTPServer import HTTPServer
	from BaseHTTPServer import BaseHTTPRequestHandler
	import SocketServer as socketserver
	
	def bytes(string, fmt):
		return string


import cgi

from magpie.plugins.abstract_plugin import AbstractPlugin
import magpie.comm
import threading

MAIN_PAGE = """
<!DOCTYPE html>
<html><head>
	<title>{title}</title>
	<meta encoding='utf-8' />
	<style>{style}</style>
</head>
<body>
	<h1>{title}</h1>
	<p>{banner}</p>
	{content}
	<br/>
	<footer>&copy; Joseph Lewis 2013</footer>
</body>
</html>
"""

UPLOAD_FORM = """
<form method='post' enctype='multipart/form-data'>
<input type="file" name="upfile" size="chars"> <br>
<input type='submit'/>
</form>
"""

STYLE = """
html {background-color:#ccc;}
h1 {text-align:center; font-family:Georgia;}
body {
	max-width: 800px;
	margin: auto;
	padding: 1em;
	background: white;
	color: #000;
	font-family:Arial,Helvetica,Sans-serif;
}
table{margin-bottom:1em;margin-left:auto;margin-right:auto;}
footer {
	font-size:.8em; text-align:center; color:#aaa;
}
form {text-align:center;}
"""


class HTTPFrontend(magpie.plugins.abstract_plugin.AbstractPlugin):
	DEFAULT_CONFIG = {'port':8000, 'host':'', 'banner':"""Welcome to the automated submission tool, to begin upload the file you
would like processed.
""", 'title':"Automated Submission Tool"}
	_http_server = None
	
	def __init__(self):
		Handler._frontend_instance = self
		AbstractPlugin.__init__(self, "HTTP", "Joseph Lewis <joehms22@gmail.com>", 0.1, "BSD 3 Clause")
		
	
	def _start_web_server(self):
		''' Starts the web server. '''
		if self._http_server != None:
			self._http_server.shutdown()
		
		serveraddr = (self._config['host'], self._config['port'])
		self._http_server = ThreadedHTTPServer(serveraddr, Handler)
		self._logger.info('Starting server')
		self._http_server.serve_forever()
	
	def teardown(self):
		'''Shuts down the plugin, should exit all threads and do all cleanup
		needed before closing.'''
		if self._http_server != None:
			self._http_server.shutdown()
		
	def update_config(self, config):
		'''Called when the configuration for the plugin has been updated from
		another source.
		'''
		self._supplement_dict(config, self.DEFAULT_CONFIG)
		self._config = config
		self._logger.info("Starting HTTP Server on Port: http://{host}:{port}".format(**self._config))
		background_thread = threading.Thread(target=self._start_web_server)
		background_thread.daemon = True
		background_thread.start()
		
		self._logger.info("Server online and active")



class Handler(BaseHTTPRequestHandler):
	_frontend_instance = None # static variable
	
	def do_GET(self):
		self.send_response(200)
		self.end_headers()
		message =  MAIN_PAGE.format(content=UPLOAD_FORM, style=STYLE, **self._frontend_instance._config)
		self.wfile.write(bytes(message, 'UTF-8'))
		return
	
	def do_POST(self):
		# Parse the form data posted
		form = cgi.FieldStorage(
			fp=self.rfile,
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
					'CONTENT_TYPE':self.headers['Content-Type'],
					})

		doc = magpie.comm.Document("No User", self._frontend_instance.get_name())
		for field in form.keys():
			if form[field].filename:
				doc.add_file(form[field].filename, form[field].file)
		
		
		self._frontend_instance._magpie.submit_document(doc)
		self.send_response(200)
		self.end_headers()
		self.wfile.write(bytes(MAIN_PAGE.format(content=doc.to_html(), style=STYLE, **self._frontend_instance._config), 'utf-8'))
		return
		
class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""



	
