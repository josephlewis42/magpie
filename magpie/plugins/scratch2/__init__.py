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
from magpie.plugins.abstract_plugin import AbstractPlugin
import scratch2.decompiler

def min_items(name, count, value):
	if count >= value:
		return (True, "You have {} {}! (You only needed {})".format(count, name, value))
	else:
		return (False, "You have {} {}, but you need {}.".format(count, name, value))


def blocks_gte(project, value, accepted_blocks, name):
	'''Tests if the project has greater than or equal to the given value.
	
	Returns a tuple (value, description)
	'''
	tmp = project.count_blocks_of_type(accepted_blocks)
	return min_items(name, tmp, value)


def min_blocks(project, value):
	tmp = len(project.blocks())
	return min_items("blocks", tmp, value)

def min_costumes(project, value):
	tmp = len(project.costumes())
	return min_items("costumes", tmp, value)

def min_sounds(project, value):
	tmp = len(project.sounds())
	return min_items("sounds", tmp, value)

def min_variables(project, value):
	tmp = len(project.variables())
	return min_items("variables", tmp, value)

def min_lists(project, value):
	tmp = len(project.lists())
	return min_items("lists", tmp, value)

def min_scripts(project, value):
	tmp = len(project.scripts())
	return min_items("scripts", tmp, value)

def min_sprites(project, value):
	tmp = len(project.sprites())
	return min_items("sprites", tmp, value)


SCRATCH_TESTS = [
('Minimum Hat Blocks', 		blocks_gte, -1, scratch2.decompiler.HAT_BLOCKS,		"hat blocks"),
('Minimum Control Blocks',	blocks_gte, -1, scratch2.decompiler.CONTROL_BLOCKS,	"control blocks"),	
('Minimum Custom Blocks',	blocks_gte, -1, scratch2.decompiler.CUSTOM_BLOCKS,	"custom blocks"),
('Minimum Events Blocks',	blocks_gte, -1, scratch2.decompiler.EVENTS_BLOCKS,	"event blocks"),
('Minimum List Blocks',		blocks_gte, -1, scratch2.decompiler.LIST_BLOCKS,	"list blocks"),
('Minimum Looks Blocks',	blocks_gte, -1, scratch2.decompiler.LOOKS_BLOCKS,	"looks blocks"),
('Minimum Motion Blocks',	blocks_gte, -1, scratch2.decompiler.MOTION_BLOCKS,	"motion blocks"),
('Minimum Operator Blocks',	blocks_gte, -1, scratch2.decompiler.OPERATORS_BLOCKS, "operator blocks"),
('Minimum Pen Blocks',		blocks_gte, -1, scratch2.decompiler.PEN_BLOCKS,		"pen blocks"),
('Minimum Sensing Blocks',	blocks_gte, -1, scratch2.decompiler.SENSING_BLOCKS,	"sensing blocks"),
('Minimum Sound Blocks',	blocks_gte, -1, scratch2.decompiler.SOUND_BLOCKS,	"sound blocks"),
('Minimum Variable Blocks',	blocks_gte, -1, scratch2.decompiler.VARIABLE_BLOCKS, "variable blocks"),
('Minimum Interaction blocks (meta category)', blocks_gte, -1, scratch2.decompiler.USER_INTERACTION_BLOCKS, "interaction blocks"),
('Minimum Blocks', min_blocks, -1),
('Minimum Costumes', min_costumes, -1),
('Minimum Sounds', min_sounds, -1),
('Minimum Scripts', min_scripts, -1),
('Minimum Sprites', min_sprites, -1)
]

class Scratch2Backend(AbstractPlugin):
	DEFAULT_CONFIG={}
	DEFAULT_TEST_CONFIG = {
		'enabled':True,
		'DESCRIPTION':'You may change any of the items in this config, if you enter a negative value, the test will not be run.'
	}
	
	def __init__(self):
		for test in SCRATCH_TESTS:
			self.DEFAULT_TEST_CONFIG[test[0]] = test[2]
	
		AbstractPlugin.__init__(self, 
			"Scratch2Parser", 
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
		
		
		print("Test config: {}".format(test_config))
		tests = []
		for path in upload.items():
			if path.endswith(".sb2"):
				scratch = scratch2.decompiler.Scratch2Project(path)
				
				test = magpie.tap.TestAnythingProtocol("Scratch2 Checks")
				for item in SCRATCH_TESTS:
					expected_value = test_config.get(item[0], item[2])
					
					if expected_value < 0:
						continue
					
					fun = item[1]
					result = fun(scratch, expected_value, *item[3:])
					test.assert_true(result[0], result[1], result[1])
					
				tests.append(test)
		
		print("Test config: {}".format(test_config))
		return tests
