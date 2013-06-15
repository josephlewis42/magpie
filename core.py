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
import traceback

from magpie.plugins.abstract_plugin import AbstractPlugin

TASK_CHECK_SLEEP_S = 60
PLUGINS_DIRECTORY = "plugins/"
CONFIG_FILE_LOCATION = "config.json"
DEFAULT_TEST_CONFIGURATION_NAME = "Default"

DEFAULT_MAGPIE_CONFIG = {
"Title":u"Automated Submission Tool",
"Header":u"Welcome to the automated submission tool!",
"Footer":u"Copyright 2013 Joseph Lewis III"
}

DEFAULT_CONFIGURATION_CONFIG = {}


def log_results(fn):
	''' A decorator to log the calls to a function.'''
	def new(*args):
		args[0]._logger.info("Calling {}...".format(fn.__name__))
		ret = fn(*args)
		args[0]._logger.info("{} finished".format(fn.__name__))
		return ret
	return new

class Magpie:
	_logger = None
	_loaded_plugins = None
	_loaded_plugins_lock = threading.Lock()
	_tasks = None # [function to call, n minutes, last_running_thread]
	
	# various configurations
	test_configurations = None
	magpie_configuration = None
	plugin_configuration = None
	

	def __init__(self):
		''' Sets up the core of the program.
		'''
		self._tasks = {}
		self._logger = self.get_logger("Magpie Core")
		
		self._logger.info("Starting Program")
		
		self.__load_configuration()
		self.__load_plugins()
		
		self.upgrade_test_configurations()
		
		if len(self.test_configurations) == 0:
			self.make_new_test_configuration(DEFAULT_TEST_CONFIGURATION_NAME)

		self._logger.info("Finished Init")
		
		# write the config file every few minutes
		self.call_function(self.write_config, 1)
		
		
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
		except(KeyboardInterrupt,SystemExit):
			self.shutdown()
		
	def __load_configuration(self):
		'''Loads the main configuration file for the project, on JSON
		error, returns a blank config.'''
		cfg = {}
		try:
			with open(CONFIG_FILE_LOCATION) as config:
				cfg = json.load(config)
		except IOError:
			pass
			
		
		self.test_configurations = cfg.get('tests', {})
		self.magpie_configuration = cfg.get('magpie', DEFAULT_MAGPIE_CONFIG)
		AbstractPlugin._supplement_dict(self.magpie_configuration, DEFAULT_MAGPIE_CONFIG)
		self.plugin_configuration = cfg.get('plugins', {})
	
	def __load_plugins(self):
		'''Loads the plugins from the plugin directory and sets up core with 
		them.
		
		'''
		self._logger.info("Setting Up Plugins")
		
		self._loaded_plugins = []
		load_plugins(PLUGINS_DIRECTORY, AbstractPlugin)
		plugins = AbstractPlugin.__subclasses__()
		
		for plugin in plugins:
			self._logger.info("Loading plugin: {}".format(plugin))
			plugin = plugin()
			pconfig = self.plugin_configuration.get(plugin.get_name(), {})
			if pconfig == None:
				pconfig = {}
			plugin.setup(pconfig, self.get_logger(plugin.get_name()), self)
			
			with self._loaded_plugins_lock:
				self._loaded_plugins.append(plugin)
		
	
	def global_config(self, key, default_value):
		''' Returns a portion of the global config.'''
		return self.magpie_configuration.get(key, default_value)
		
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
		
	def make_new_test_configuration(self, name):
		""" Returns a new test configuration for all of the given plugins.		
		"""

		cfg = {}
		
		for p in self._loaded_plugins:
			cfg[p.get_name()] = p.get_default_test_configuration()
		
		self.test_configurations[name] = cfg
		
		return cfg
	
	def _decompose_plugin_identifier(self, identifier):
		'''Decomposes a plugin identifier in to a name and version.
		
		'''
		if "|" not in identifier:
			return [identifier, ""]
		
		return identifier.split("|",1)
	
	def upgrade_test_configurations(self):
		'''Upgrades all of the test configurations in the project.'''
		new_configurations = {}
		plugins_by_name = dict((p.get_name(), p) for p in self._loaded_plugins)
		
		for testname, configurations in self.test_configurations.items():
			new_configurations[testname] = dict()
			
			for identifier, config in configurations.items():
				name, version = self._decompose_plugin_identifier(identifier)
				plugin = plugins_by_name[name]
				
				# if version is new enough, don't upgrade
				if version >= str(plugin.get_version()):
					new_configurations[testname][identifier] = config
				else:
					AbstractPlugin._supplement_dict(config, plugin.get_default_test_configuration())
					new_configurations[testname][plugin.get_name_version()] = config
		
		self.test_configurations = new_configurations
	
	def submit_document(self, document, configuration_type):
		''' Processes an uploaded document.
		'''
		
		cfgs = self.test_configurations.get(configuration_type, {})
		
		if len(cfgs) == 0:
			cfgs = self.test_configurations.get(DEFAULT_TEST_CONFIGURATION_NAME, {})
		
		plugins = []
		with self._loaded_plugins_lock:
			plugins += self._loaded_plugins
			
		for plug in plugins:
			
			# get the configuration for the given type for the given plugin
			cfg = cfgs.get(plug.get_name_version(), None)
			if cfg == None:
				cfg = plug.get_default_test_configuration()
				cfgs[plug.get_name()] = cfg
		
			try:
				document.add_results(plug.process_upload(document, cfg))
			except Exception as e:
				print("Failed loading {}".format(plug.get_name()))
				print(str(e))
				traceback.print_exc()
		return document
		
	
	def call_function(self, function, minutes):
		''' Calls the given function every x minutes in a new thread if it is 
		not still executing from the last time it was run.
		
		'''
		self._tasks[function] = minutes
	
	@log_results
	def write_config(self):
		'''Writes the configuration to a file.'''
		cfg = {
			'tests':self.test_configurations,
			'magpie':self.magpie_configuration,
			'plugins':{}
		}

		with self._loaded_plugins_lock:
			for plug in self._loaded_plugins:
				cfg['plugins'][plug.get_name()] = plug.get_config()
		
		with open(CONFIG_FILE_LOCATION, 'w') as output:
			json.dump(cfg, output)
	
	@log_results
	def shutdown(self):
		self.write_config()



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
