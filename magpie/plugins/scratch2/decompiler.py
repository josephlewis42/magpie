#!/usr/bin/env python
'''
A scratch 2 parser written in Python

Copyright 2013 Joseph Lewis <joehms22@gmail.com>
'''

import zipfile
import json

# an enumeration of all the hat blocks available
HAT_BLOCKS = frozenset([u"whenKeyPressed", u"whenClicked", u"whenSceneStarts", 
	u"whenSensorGreaterThan", u"whenIReceive", u"whenCloned", u"procDef",
	u"whenGreenFlag"])

MOTION_BLOCKS = frozenset([u'bounceOffEdge', u'changeXposBy:', u'changeYposBy:',
	u'forward:', u'glideSecs:toX:y:elapsed:from:', u'gotoSpriteOrMouse:',
	u'gotoX:y:', u'heading', u'heading:', u'pointTowards:', u'setRotationStyle',
	u'turnLeft:', u'turnRight:', u'xpos', u'xpos:', u'ypos', u'ypos:'])
 
LOOKS_BLOCKS = frozenset([u'backgroundIndex', u'changeGraphicEffect:by:',
	u'changeSizeBy:', u'comeToFront', u'costumeIndex', u'filterReset',
	u'goBackByLayers:', u'hide', u'lookLike:', u'nextCostume', u'nextScene',
	u'say:', u'say:duration:elapsed:from:', u'scale', u'sceneName',
	u'setGraphicEffect:to:', u'setSizeTo:', u'show', u'startScene',
	u'startSceneAndWait', u'think:', u'think:duration:elapsed:from:'])


SOUND_BLOCKS = frozenset([u'changeTempoBy:', u'changeVolumeBy:', 
	u'doPlaySoundAndWait', u'instrument:', u'noteOn:duration:elapsed:from:',
	u'playDrum', u'playSound:', u'rest:elapsed:from:', u'setTempoTo:',
	u'setVolumeTo:', u'stopAllSounds', u'tempo', u'volume'])

PEN_BLOCKS = frozenset([u'changePenHueBy:', u'changePenShadeBy:', 
	u'changePenSizeBy:', u'clearPenTrails', u'penColor:', u'penSize:',
	u'putPenDown', u'putPenUp', u'setPenHueTo:', u'setPenShadeTo:', 
	u'stampCostume'])

LIST_BLOCKS = frozenset([u'append:toList:', u'contentsOfList:', 
	u'deleteLine:ofList:', u'getLine:ofList:', u'hideList:', 
	u'insert:at:ofList:', u'lineCountOfList:', u'list:contains:',
	u'setLine:ofList:to:', u'showList:'])

VARIABLE_BLOCKS = frozenset([u'changeVar:by:', u'hideVariable:', 
	u'readVariable', u'setVar:to:', u'showVariable:'])

EVENTS_BLOCKS = frozenset([u'broadcast:', u'doBroadcastAndWait',u'whenClicked',
	u'whenGreenFlag', u'whenIReceive', u'whenKeyPressed', u'whenSceneStarts',
	u'whenSensorGreaterThan'])

CONTROL_BLOCKS = frozenset([u'createCloneOf', u'deleteClone', u'doForever',
	u'doIf', u'doIfElse', u'doRepeat', u'doUntil', u'doWaitUntil', 
	u'stopScripts', u'wait:elapsed:from:', u'whenCloned'])

SENSING_BLOCKS = frozenset([u'answer', 	u'color:sees:',	u'distanceTo:',
	u'doAsk', u'getAttribute:of:',	u'getUserName',	u'keyPressed:',
	u'mousePressed', u'mouseX', u'mouseY', u'senseVideoMotion',
	u'setVideoState', u'setVideoTransparency', u'soundLevel', u'timeAndDate',
	u'timer', u'timerReset', u'timestamp', u'touching:', u'touchingColor:'])

OPERATORS_BLOCKS = frozenset([u'%', u'&', u'*', u'+', u'-', u'/', u'<', u'=',
	u'>', u'computeFunction:of:', u'concatenate:with:', u'letter:of:',
	u'not', u'randomFrom:to:', u'rounded', u'stringLength:', u'|']) 
	
CUSTOM_BLOCKS = frozenset([u'call', u'procDef'])


# Meta categories
USER_INTERACTION_BLOCKS = frozenset([u'whenClicked', u'whenKeyPressed', 
u'keyPressed:', u'mousePressed', u'mouseX', u'mouseY'])




class Scratch2Project:
	__jsondoc = None
	
	
	def __init__(self, filepath):
		'''Takes a filepath and parses the file.'''
		with zipfile.ZipFile(filepath) as fp:
			with fp.open("project.json") as js_doc:
				self.__jsondoc = json.load(js_doc)
	
	def sprites(self):
		'''Returns an array containing all sprites for the project'''
		return self.__jsondoc["children"]
	
	def stage(self):
		'''Returns the stage for the project.'''
		return self.__jsondoc
		
	def _from_stage_and_sprites(self, property_name):
		tmp = []
		tmp += self.stage().get(property_name, [])
		
		for sprite in self.sprites():
			tmp += sprite.get(property_name, [])
		
		return tmp
		
	def scripts(self, return_non_attached=False):
		'''Returns an array containing all of the scripts in the project.
		
		'''
		tmp = self._from_stage_and_sprites('scripts')
		
		# the third param is the actual script array
		scripts = [t[2] for t in tmp]
		
		if return_non_attached:
			return scripts
		
		return [s for s in scripts if s[0][0] in HAT_BLOCKS]
		
		
	def blocks(self, return_non_attached=False):
		'''Returns a list containing all the blocks that are rechable in the 
		project
		
		'''
		blocks = []
		
		for script in self.scripts(return_non_attached):
			for block in script:
				blocks.append(block)
		
		# fetch hidden inner blocks like operators
		extrablocks = []
		
		def lookforlists(block, extrablocks):
			for item in block:
				if type(item) != list:
					continue
				if len(item) == 0:  # ignore empty lists
					continue
				if type(item[0]) in [type(u''), type('')]:
					extrablocks += [item]
					lookforlists(item, extrablocks)
				if type(item[0]) == list:
					lookforlists(item, extrablocks)
		
		lookforlists(blocks, extrablocks)
		
		return extrablocks
	
	
	def costumes(self):
		'''Returns a list containing all the costumes and backgrounds
		for the project.
		
		'''
		return self._from_stage_and_sprites('costumes')
		
		
	def sounds(self):
		'''Returns a list containing all the sounds in the project.
		
		'''
		return self._from_stage_and_sprites('sounds')
	
	def variables(self):
		'''Returns a list containing all of the variables in the project.
		
		'''
		return self._from_stage_and_sprites('variables')
	
	def lists(self):
		'''Returns a list containing all of the lists in the project.
		
		'''
		return self._from_stage_and_sprites('lists')
		
	
	def info(self):
		'''Returns information about the scratch project.
		
		'''
		
		return self.__jsondoc["info"]
	
	def count_blocks_of_type(self, block_types):
		'''Returns the number of blocks that fit with the given category.
		'''
		return sum([1 for b in self.blocks() if b[0] in block_types])
		
