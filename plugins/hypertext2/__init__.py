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

import magpie
from flask import Flask, render_template, request, url_for, redirect
from magpie.plugins.abstract_plugin import AbstractPlugin
import threading
import pprint
import json

frontend_instance = None # used by flask to access methods of HTTPFrontend2
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
	try:
		if request.method == 'GET':
			tests = frontend_instance._magpie.test_configurations.keys()
			return render_template('upload.html', tests=tests, **frontend_instance._config)

		else: # POST
			doc = magpie.comm.Document("No User", frontend_instance.get_name())

			
			file = request.files['upfile']
			doc.add_file(file.filename,file)
			
			test = request.form['test']
			frontend_instance._magpie.submit_document(doc, test)
			return render_template('results.html', document=doc, **frontend_instance._config)

	except Exception as e:
		frontend_instance._logger.exception(e)
		print("Exception")
		return (str(e))

@app.route('/config', methods=['GET'])
def configure_app():
	contents = "<h3>Tests<h3>"
	for testname, testconfig in frontend_instance._magpie.test_configurations.items():
		contents += "<h4>{}</h4><pre>{}</pre>".format(testname, pprint.pformat(testconfig))
		contents += "<br><a href='{}'>Delete</a>".format(url_for('delete_test', test_name=testname))
		contents += "<br><a href='{}'>Edit</a>".format(url_for('edit_test', test_name=testname))
	
	return render_template('configure.html', config = contents, **frontend_instance._config)

@app.route('/edit/<test_name>', methods=['GET', 'POST'])
def edit_test(test_name):
	if request.method == 'GET':
		# check to see if we're making a new config or editing an existing one
		testval = frontend_instance._magpie.test_configurations.get(test_name, None)
		if testval == None:
			testval = frontend_instance._magpie.make_new_test_configuration(test_name)
		
		testval = json.dumps(testval, sort_keys=True, indent=4, separators=(',', ': '))
		return render_template('edit_test.html', test_name=test_name, test_value=testval, msg="", **frontend_instance._config)
	else: # POST
		testval = request.form['test']
		print testval
		newtests = json.loads(testval)
		
		frontend_instance._magpie.test_configurations[test_name] = newtests
		return redirect(url_for('configure_app'))
		
@app.route('/delete/<test_name>')
def delete_test(test_name):
	if test_name in frontend_instance._magpie.test_configurations:
		del frontend_instance._magpie.test_configurations[test_name]
	return redirect(url_for('configure_app'))

@app.route('/newtest', methods=['POST'])
def new_test():
	try:
		name = request.form['name']
	except KeyError:
		name = 'New Test'
	return redirect(url_for('edit_test', test_name=name))

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

DEFAULT_CONFIG = {
	'port':8080, 
	'host':'', 
	'upload_instructions':"""Welcome to the Magpie submission tool, to begin upload the file you would like processed.""", 
	'title':"Magpie",
	'results_header':"",
	'results_tail':"",
	'message_of_the_day':''
	}

class HTTPFrontend2(AbstractPlugin):
	def __init__(self):
		global frontend_instance
		AbstractPlugin.__init__(self, "HTTP2", "Joseph Lewis <joehms22@gmail.com>", 0.1, "BSD 3 Clause", DEFAULT_CONFIG, {})
		frontend_instance = self
	
	def teardown(self):
		'''Shuts down the plugin, should exit all threads and do all cleanup
		needed before closing.'''

		
	def update_config(self, *args):
		'''Called when the configuration for the plugin has been updated from
		another source.
		'''
		AbstractPlugin.update_config(self, *args)
		try:
			shutdown_server()
		except RuntimeError:
			pass # not running yet.
		
		self._logger.info("Starting HTTP2 Server on Port: http://{host}:{port}".format(**self._config))
		background_thread = threading.Thread(target=app.run, kwargs={'host':self._config['host'], 'port':self._config['port'], 'threaded':True})
		background_thread.daemon = True
		background_thread.start()
		
