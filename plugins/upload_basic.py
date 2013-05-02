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

from magpie.plugins.abstract_plugin	import AbstractPlugin
import magpie.tap

class BasicUpload(AbstractPlugin):
	'''Reports basic upload information about the files, passes if they fit
	with the specified formatting.
	'''
	
	def __init__(self):
		AbstractPlugin.__init__(self,
			"Basic Upload", 
			"Joseph Lewis <joehms22@gmail.com>", 
			0.1, 
			"BSD 3 Clause")
	
	def process_upload(self, upload):
		''' Very basic tests about the uploaded file. '''
		test = magpie.tap.TestAnythingProtocol(title="Basic Upload")
		one = False
		for path in upload.items():
			one = True
			test.pass_test("Has at least one file")
			test.assert_true(path.endswith(".sb"), "Is a scratch file?", fail_description="Oops, it looks like you didn't upload a scratch file, try again!")

		if not one:
			test.fail("Has at least one file")

		return test
			
