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
import io
import json

from magpie.plugins.abstract_plugin import AbstractPlugin
import magpie.tap
try:
	import kurt
except ImportError:
	kurt = None


def count_scripts(scratch):
	''' Counts the number of scripts in a project. '''
	count = len(scratch.stage.scripts)
	for sprite in scratch.sprites:
		count += len(sprite.scripts)
	
	return count 

def count_costumes(scratch):
	ct = 0
	for sprite in scratch.sprites:
		ct += len(sprite.costumes)
	return ct

def count_sounds(scratch):
	count = len(scratch.stage.sounds)
	return count + sum([len(x.sounds) for x in scratch.sprites])

def count_sprites(scratch):
	return len(scratch.sprites)

def count_backgrounds(scratch):
	return len(scratch.stage.backgrounds)

def count_blocks(scratch):
	return sum([len(s) for s in scratch.stage.scripts]) + sum([sum([len(s) for s in x.scripts]) for x in scratch.sprites])

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

def count_variables(scratch):
	return len(scratch.stage.variables) + sum([len(x.variables) for x in scratch.sprites])

def count_lists(scratch):
	return len(scratch.stage.lists) + sum([len(x.lists) for x in scratch.sprites])

# lines for telling the user what the results were
MIN_PASS_LINE = "You have over {{n}} {obj}!"
MIN_FAIL_LINE = "You have fewer than {{n}} {obj}"


MIN_SCRIPTS = lambda scratch, n: count_scripts(scratch) >= n
MIN_SOUNDS	= lambda scratch, n: count_sounds(scratch) >= n
MIN_SPRITES	= lambda scratch, n: count_sprites(scratch) >= n
MIN_BGRDS	= lambda scratch, n: count_backgrounds(scratch) >= n
MIN_COSTUMES= lambda scratch, n: count_costumes(scratch) >= n
MIN_BLOCKS	= lambda scratch, n: count_blocks(scratch) >= n
MIN_VARIABLES = lambda scratch, n: count_variables(scratch) >= n
MIN_LISTS = lambda scratch, n: count_lists(scratch) >= n

# user-configurable functions for the results, in the format:
# JSON_NAME, default value, evaluation function, if true, if false
SCRATCH_FUNCTIONS = [
('Minimum Scripts', 3, MIN_SCRIPTS, MIN_PASS_LINE.format(obj="scripts"), MIN_FAIL_LINE.format(obj="scripts")),
('Minimum Sounds', 3, MIN_SOUNDS, MIN_PASS_LINE.format(obj="sounds"), MIN_FAIL_LINE.format(obj="sounds")),
('Minimum Sprites', 3, MIN_SPRITES, MIN_PASS_LINE.format(obj="sprites"), MIN_FAIL_LINE.format(obj="sprites")),
('Minimum Backgrounds', 3, MIN_BGRDS, MIN_PASS_LINE.format(obj="backgrounds"), MIN_FAIL_LINE.format(obj="backgrounds")),
('Minimum Costumes', 1, MIN_COSTUMES, MIN_PASS_LINE.format(obj="costumes"), MIN_FAIL_LINE.format(obj="costumes")),
('Minimum Blocks', 3, MIN_BLOCKS, MIN_PASS_LINE.format(obj="blocks"), MIN_FAIL_LINE.format(obj="blocks")),
('Minimum Variables', 0, MIN_VARIABLES, MIN_PASS_LINE.format(obj="variables"), MIN_FAIL_LINE.format(obj="variables")),
('Minimum Lists', 0, MIN_LISTS, MIN_PASS_LINE.format(obj="lists"), MIN_FAIL_LINE.format(obj="lists"))
]


class ScratchGrader(AbstractPlugin):
	''' The plugin that is set to handle all information coming in and going
	from this system.
	
	'''
	DEFAULT_CONFIG = {}
	DEFAULT_TEST_CONFIG = {
	'enabled':True,
	"DESCRIPTION":"You may change any of the items in this config, if you enter a negative value, the test will not be run."
	}
	
	def __init__(self):
		
		# append all possible tests to the default config
		for name, val, fun, t, f in SCRATCH_FUNCTIONS:
			self.DEFAULT_TEST_CONFIG[name] = val
		
		
		AbstractPlugin.__init__(self, 
					"Scratch Grader", 
					"Joseph Lewis <joehms22@gmail.com>", 
					0.1, 
					"BSD 3 Clause",
					self.DEFAULT_CONFIG,
					self.DEFAULT_TEST_CONFIG)
	
	def process_upload(self, upload, test_config):
		'''Called when an upload has been input in to the program.
		
		Returns a dictionary with pairs corresponding to:
		{testname, TAPInstance}
		
		This software will parse 
		http://podwiki.hexten.net/TAP/TAP.html?page=TAP
		
		'''
		
		if test_config.get("enabled", False) == False:
			return None
		
		if kurt == None:
			test = magpie.tap.TestAnythingProtocol("Scratch Grader Configuration")
			test.fail("kurt is not installed", todo="Install Kurt" )
		
		print("Processing upload");
		tests = []
		for path in upload.items():
			if path.endswith(".sb"):
				#scratch = to_dict(kurt.ScratchProjectFile(path))
				scratch = kurt.ScratchProjectFile(path)
				
				test = magpie.tap.TestAnythingProtocol("Scratch Checks")
				for name, val, fun, t, f in SCRATCH_FUNCTIONS:
					expected_value = test_config.get(name, val)
					
					if expected_value < 0:
						continue
					
					t = t.format(n=expected_value)
					f = f.format(n=expected_value)
					test.assert_true(fun(scratch, expected_value), t, f)
					self.DEFAULT_TEST_CONFIG[name] = val
					
				tests.append(test)
		
		return tests
