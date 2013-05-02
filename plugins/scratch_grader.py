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

import tempfile

from magpie.plugins.abstract_plugin import AbstractPlugin
import magpie.tap
try:
	import kurt
except ImportError:
	kurt = None


class ScratchGrader(AbstractPlugin):
	''' The plugin that is set to handle all information coming in and going
	from this system.
	
	'''
	
	def __init__(self):
		AbstractPlugin.__init__(self, "Scratch Grader", "Joseph Lewis <joehms22@gmail.com>", 0.1, "BSD 3 Clause")
	
	def process_upload(self, upload):
		'''Called when an upload has been input in to the program.
		
		Returns a dictionary with pairs corresponding to:
		{testname, TAPInstance}
		
		This software will parse 
		http://podwiki.hexten.net/TAP/TAP.html?page=TAP
		
		'''
		if kurt == None:
			test = magpie.tap.TestAnythingProtocol("Scratch Grader Configuration")
			test.fail("kurt is not installed", todo="Install Kurt" )
		
		print("Processing upload");
		tests = []
		for path in upload.items():
			print("Got file")
			if path.endswith(".sb"):
				print("Got scratch file")
				scratch = to_dict(kurt.ScratchProjectFile(path))
				
				test = magpie.tap.TestAnythingProtocol("Assignment 2 Checks")
				test.assert_true(scratch['num_scripts'] > 2, "You have at least 3 scripts.", "You need at least 3 scripts.")
				
				numsounds = sum([len(sprite['sounds']) for sprite in scratch['sprites']]) + len(scratch['stage']['sounds'])
				
				test.assert_true(numsounds >= 1, "You a {} sounds.".format(numsounds), "You need at least one sound")
				import pprint
				pp = pprint.PrettyPrinter(indent=4)
				pp.pprint(scratch)
				
				tests.append(test)
		
		return tests

import io
import json

def count_scripts(scratch):
	''' Counts the number of scripts in a project. '''
	count = len(scratch.stage.scripts)
	for sprite in scratch.stage.sprites:
		count += len(sprite.scripts)
	
	return count 

def count_accessible_scripts(scratch):
	counter = 0
	for script in scratch.stage.scripts:
		if 'EventHatMorph' in script.blocks[0].command:
			counter += 1
	for sprite in scratch.stage.sprites:
		for script in sprite.scripts:
			if 'EventHatMorph' in script.blocks[0].command:
				counter += 1
	
	return counter

recurse_dict = True
def to_dict(item, deepcopy=True):
	''' Converts a scratch project to a Python dictionary. '''
	CLASSNAME = str(item.__class__)
	
	# Top Level of the project, return a python dict
	if "kurt.files.ScratchProjectFile" in CLASSNAME:
		return {'name':to_dict(item.name), 
				'info':to_dict(item.info),
				'sprites':to_dict(item.sprites), 
				'stage':to_dict(item.stage),
				'num_scripts':count_scripts(item),
				'num_accessible_scripts':count_accessible_scripts(item)}
	
	if "kurt.user_objects.Stage" in CLASSNAME:
		return {"fields":to_dict(item.fields, False), 
				"backgrounds":to_dict(item.backgrounds), 
				"sounds":to_dict(item.sounds, False)}
	
	if "kurt.user_objects.SpriteCollection" in CLASSNAME:
		return [to_dict(x) for x in item]
	
	if "kurt.user_objects.Sprite" in CLASSNAME:
		return {"fields":to_dict(item.fields, False), 
				"costumes":to_dict(item.costumes), 
				"sounds":to_dict(item.sounds, False)}
	
	if "kurt.user_objects.Image" in CLASSNAME:
		#x = io.StringIO()
		#item.get_image().save(x, u"PNG")
		#contents = x.getvalue().encode("base64")
		#x.close()
		return "<Image>"# 'data:image/png;base64,' + contents
	
	if 'kurt.scripts.ScriptCollection' in CLASSNAME:
		return [to_dict(x) for x in item]
	
	if 'kurt.scripts.Script' in CLASSNAME:
		has_hat = 'Hat' in item.blocks[0].command
		return {"has_hat":has_hat, "script":str(item)}
	
	if 'kurt.user_objects.Sound' in CLASSNAME:
		return {'fields':to_dict(item.fields, False)}
	
	if isinstance(item, dict):
		to_ret = {}
		
		for key, val in item.items():
			if not str(key).startswith("_"):
				if deepcopy == False and (isinstance(item, list) or isinstance(item, dict)):
					to_ret[key] = str(val)
				else:
					to_ret[key] = to_dict(val)
		return to_ret
	
	if isinstance(item, list):
		return [to_dict(x) for x in item]
	
	if isinstance(item, int):
		return item
	
	if isinstance(item, float):
		return item
	
	return str(item)
