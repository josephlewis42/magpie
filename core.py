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

import logging
import time
import threading
import json
import imp
import os
import sys
import inspect

from magpie.plugins.abstract_plugin import AbstractPlugin

TASK_CHECK_SLEEP_S = 60

class Magpie:
	_logger = None
	_loaded_plugins = None
	_loaded_plugins_lock = threading.Lock()
	_config_file_location = None
	_configuration = None
	_tasks = None # [function to call, n minutes, last_running_thread]

	def __init__(self, config_file="config.json"):
		''' Sets up the core of the program.
		'''
		self._config_file_location = config_file
		self._tasks = {}
		
		
		self._logger = self.get_logger("Magpie Core")
		self._logger.info("Starting Program")
		
		self._configuration = self.__load_configuration()
		

		self._loaded_plugins = []
		self._logger.info("Setting Up Plugins")
		
		load_plugins("plugins/", AbstractPlugin)
		plugins = AbstractPlugin.__subclasses__()
		
		for plugin in plugins:
			self._logger.info("Loading plugin: {}".format(plugin))
			plugin = plugin()
			pconfig = {}
			if plugin.get_name() in self._configuration:
				pconfig = self._configuration[plugin.get_name()]
			
			plugin.setup(pconfig, self.get_logger(plugin.get_name()), self)
			
			with self._loaded_plugins_lock:
				self._loaded_plugins.append(plugin)

		self._logger.info("Finished Init")
		
		
		running_tasks = {}
		try:
			while True:
				self._logger.info("Waking up to do CRON tasks")
				tm = int(time.time() / 60) # get current minute
				for function, minutes in self._tasks.items():
					if tm % minutes != 0:
						continue
					
					last = running_tasks.get(function, None)
					
					if last != None and last.is_alive(): # don't re-spawn proceses that are already running
						continue
					
					try:
						last = threading.Thread(target=function)
						last.daemon = True
						last.start()
						
						running_tasks[function] = last
					except Exception as e:
						self._logger.error(str(e))
					
				time.sleep(TASK_CHECK_SLEEP_S)
				# TODO check for tasks that need to be run, and run them.
		except(KeyboardInterrupt,SystemExit):
			self.shutdown()
		
	def __load_configuration(self):
		'''Loads the main configuration file for the project.'''
		try:
			with open(self._config_file_location) as config:
				return json.load(config)
		except IOError:
			return {}
		
	def get_logger(self, name):
		'''	Creates a logger with the given name that writes to the default
		locations and returns it.
		'''
		logger = logging.getLogger(name)
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
		handlers = [logging.StreamHandler(), logging.FileHandler('auto_grader.log')]
		
		for handler in handlers:
			handler.setFormatter(formatter)
			logger.addHandler(handler)

		logger.setLevel(logging.INFO)
		return logger
	
	def get_reporter(self):
		pass
	
	def submit_document(self, document):
		with self._loaded_plugins_lock:
			for plug in self._loaded_plugins:
				document.add_results(plug.process_upload(document))
				
		return document
		
	
	def call_function(self, function, minutes):
		''' Calls the given function every x minutes in a new thread if it is 
		not still executing from the last time it was run.
		
		'''
		self._tasks[function] = minutes
	
	def shutdown(self):
		self._logger.info("Shutting down...")
		full_config = {}
		
		with self._loaded_plugins_lock:
			for plug in self._loaded_plugins:
				full_config[plug.get_name()] = plug.get_config()
		
		print(full_config)
		
		with open(self._config_file_location, 'w') as output:
			json.dump(full_config, output)
		
		self._logger.info("Shutdown complete.")



def load_plugins(plugin_path, instance):
	'''Loads a set of plugins at the given path.
	
	Arguments:
	plugin_path - the OS path to look for plugins at.
	instance - classes of this instance will be returned
	'''
	plugins = []
	plugin_dir = os.path.realpath(plugin_path)
	sys.path.append(plugin_dir)
	

	
	for f in os.listdir(plugin_dir):
		if f.endswith(".py"):
			name = f[:-3]
		elif f.endswith(".pyc"):
			name = f[:-4]
		elif os.path.isdir(os.path.join(plugin_dir, f)):
			name = f
		else:
			continue
		
		try:
			mod = __import__(name, globals(), locals(), [], 0)

			for piece in inspect.getmembers(mod):
				if isinstance(piece, instance):
					plugins.append(piece)

		except ImportError as e:
			print(e)
			pass # problem importing
		
	return plugins
