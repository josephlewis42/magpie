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

import tap
import uuid
import os

class Document:
	''' Represents a submitted document from a particular user
	'''
	frontend = None # the frontend that created this document
	user = None # username
	files = None # list of files the user submitted
	results = None # list of results <magpie.tap.TestAnythingProtocol>
	meta = None # store junk in here you may want cross-plugin, 
	#but don't depend on it being there!
	_document_id = None
	
	def __init__(self, user, frontend):
		self.results = []
		self.frontend = frontend
		self.user = user
		self.files = []
		self.meta = {}
		self._document_id = str(uuid.uuid4()) # a unique id for the document
	
	def add_results(self, results):
		'''Adds results to the internal list of results.
		
		'''
		if results == None:
			return
		
		try:
			for result in results:
				self.results.append(result)
		except TypeError:
			self.results.append(results)
	
	def to_html(self):
		'''Converts the representation of this document to an HTML 
		report.
		
		'''
		
		return "<br>".join([x.to_html() for x in self.results])
	
	def add_file(self, name, data):
		''' Adds a file to the document.
		'''
		parent_path = os.path.join('uploads', self._document_id)
		os.makedirs(parent_path)
		file_path = os.path.join(parent_path, name)
		
		with open(file_path, 'wb') as fout:
			try:
				fout.write(data.read())
			except AttributeError:
				fout.write(data)

		self.files.append(file_path)
	
	def items(self):
		'''Returns a list of file paths to copies of the uploaded files
		associated witht this document.
		'''
		return self.files
