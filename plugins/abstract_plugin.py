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

class AbstractPlugin(object):
	''' The plugin that is set to handle all information coming in and going
	from this system.
	
	'''
	_config = None
	_logger = None
	_magpie = None
	_name = None
	_author = None
	_version = None
	_license = None
	_default_config = None
	_default_test = None
	
	def __init__(self, plugin_name, plugin_author, plugin_version, plugin_license, default_config, default_test):
		self._name = plugin_name
		self._author = plugin_author
		self._version = plugin_version
		self._license = plugin_license
		self._default_config = default_config
		self._default_test = default_test
		
		# convert everything to unicode for consistency with the JSON loader.
		for key, value in self._default_config.items():
			if type(value) == type(''):
				self._default_config[key] = unicode(value)
	
	def setup(self, config, logger, core):
		'''Initializes the plugin with the given configuration dictionary.
		
		config - either a blank dictionary, or the same dictionary returned
		by "get_config" last time the program was shut down.
		
		logger - an instance of Logger from the logging package that this 
		plugin can use as a log.
		
		core - an instance of magpie.core.Magpie that you can use as the main app
		
		
		By defualt, this function sets self._config, self._logger and 
		self._magpie, then calls self.update_config() with the given config.
		
		'''
		self._logger = logger
		self._magpie = core
		logger.info("Loaded Module: {}".format(self.get_name()))
		self.update_config(config)
	
	def teardown(self):
		'''Shuts down the plugin, should exit all threads and do all cleanup
		needed before closing.'''
		pass
		
	def update_config(self, config):
		'''Called when the configuration for the plugin has been updated from
		another source.
		
		By default, simply updates self._config and supplements it with the 
		default config.
		
		'''
		self._config = self._supplement_dict(config, self._default_config)
	
	def get_config(self):
		'''Gets the configuration for the plugin.
		
		By default, returns self._config, you may wish to override however.
		'''
		return self._config
	
	def process_upload(self, upload, test_configuration):
		'''Called when an upload has been input in to the program.
		
		Returns a dictionary with pairs corresponding to:
		{testname, TAPInstance}
		
		This software will parse 
		http://podwiki.hexten.net/TAP/TAP.html?page=TAP
		
		'''
		pass
	
	def upload_processed(self, upload):
		'''Called after process_upload has been completed on the upload.'''
		pass
	
	def get_name(self):
		'''Returns the name for the plugin.'''
		return self._name
	
	def get_author(self):
		'''Returns the author for the plugin.'''
		return self._author
	
	def get_version(self):
		'''Returns the version of the plugin.'''
		return self._version
	
	def get_license(self):
		'''Returns the license of the plugin.'''
		return self._license
	
	def get_default_test_configuration(self):
		''' Gets a default configuration used for a test.
		'''
		return self._default_test
		
	@staticmethod
	def _supplement_dict(to_supplement, supplement):
		'''Finds any keys in supplement that don't exist in to_supplement,
		and adds the key->value paris found in supplement. Also replaces
		keys that exist in to_supplement if their type does not match that given
		in supplement.
		
		Example:
		
		>>> _supplement_dict({"port":"cookie!", "key":"value"}, {"port":8080, "host":"localhost"})
		{"port":8080, "key":"value","host":"localhost"}
		
		port is changed because its type is wrong, key is left alone, and host
		is added.
		
		'''
		
		for key, value in supplement.items():
			if not key in to_supplement:
				to_supplement[key] = value
			else:
				if not type(to_supplement[key]) == type(value):
					to_supplement[key] = value
		
		return to_supplement
