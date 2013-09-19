#!/usr/bin/env python3
'''

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
import poplib
import magpie.comm
import base64
import smtplib
from email import parser
from magpie.plugins.abstract_plugin import AbstractPlugin
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class SMTPFrontend(AbstractPlugin):
	'''Provides an email based frontend to the automated grading tool.
	'''
	DEFAULT_CONFIG = {
		'username':u'somebody@gmail.com', 
		'password':u'password', 
		'pop_host':u'pop.gmail.com',
		'pop_port':995,
		'pop_tls_enabled':True,
		'smtp_host':u'smtp.gmail.com',
		'smtp_port':587,
		'smtp_tls_enabled':False,
		'header':u'Welcome to the automated sumission tool!',
		'footer':u'Copyright 2013 Joseph Lewis III',
		'reply_subject':u'Your Recent Submission',
		'enabled':False
	}
	
	def __init__(self):
		AbstractPlugin.__init__(self, "SMTP Frontend", "Joseph Lewis <joehms22@gmail.com>", 0.1, "BSD 3 Clause", self.DEFAULT_CONFIG, {})
	
	def setup(self, *args):
		AbstractPlugin.setup(self, *args)
		self._magpie.call_function(self.task, 1)
	
	def _process_uploads(self):
		documents = []
		# Connect to the server
		if self._config['pop_tls_enabled']:
			pop_conn = poplib.POP3_SSL(self._config['pop_host'], self._config['pop_port'])
		else:
			pop_conn = poplib.POP3(self._config['pop_host'], self._config['pop_port'])
		pop_conn.user(self._config['username'])
		pop_conn.pass_(self._config['password'])
		
		#Get messages from server:
		messages = [pop_conn.retr(i) for i in range(1, len(pop_conn.list()[1]) + 1)]
		

		#Parse message intom an email object:
		for mssg in ["\n".join(mssg[1]) for mssg in messages]:
			message = parser.Parser().parsestr(mssg)
			
			doc = magpie.comm.Document(message['from'], self.get_name())
			subj = message['Subject']
			
			test = ""
			for key in self._magpie.test_configurations.keys():
				if key.lower() in subj.lower():
					test = key
			
			for part in message.walk():
				fn = part.get_filename()
				if fn == None:
					continue
				
				try:
					finfo = base64.b64decode(part.get_payload())
				except TypeError:
					finfo = part.get_payload()
				
				doc.add_file(fn, finfo)
			self._magpie.submit_document(doc, key)
			documents.append(doc)
		pop_conn.quit()
		return documents
	
	def _send_results(self, documents):
		'''Sends the results of the uploads.
		'''
		
		if self._config['smtp_tls_enabled']:
			smtp_conn = smtplib.SMTP_SSL(self._config['smtp_host'], self._config['smtp_port'])
		else:
			smtp_conn = smtplib.SMTP(self._config['smtp_host'], self._config['smtp_port'])
		
		smtp_conn.ehlo()
		smtp_conn.starttls()
		smtp_conn.login(self._config['username'], self._config['password'])
		
		for document in documents:
			msg = MIMEMultipart('alternative')
			msg['Subject'] = self._config['reply_subject']
			msg['From'] = self._config['username']
			msg['To'] = document.user
			
			html = """<html><head></head><body>
			
			<p>{header}</p>
			
			<p>Here are the results of the submission of the following documents:</p>
			<pre>{files}</pre>
			
			{tests}
			
			<hr>
			{footer}
			</body></html>""".format(files="\n".join(document.files), tests=document.to_html(), **self._config)

			# Record the MIME types of both parts - text/plain and text/html.
			part1 = MIMEText(html, 'plain')
			part2 = MIMEText(html, 'html')

			# Attach parts into message container.
			# According to RFC 2046, the last part of a multipart message, in this case
			# the HTML message, is best and preferred.
			msg.attach(part1)
			msg.attach(part2)

			smtp_conn.sendmail(self._config['username'], document.user, msg.as_string())
		
		smtp_conn.quit()
		
	
	def task(self):
		'''Fetches new messages, processes them, and sends back results.'''
		if not self._config['enabled']:
			return
		
		outbox = self._process_uploads()
		self._send_results(outbox)
		
		
	
