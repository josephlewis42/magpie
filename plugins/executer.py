
from magpie.plugins.abstract_plugin import AbstractPlugin

class Executer(AbstractPlugin):
	''' This plugin executes supplied program paths replacing {file} with the 
	path to a file the user uploaded.
	
	Executer will look for items in the config for keys that start with 
	regex_XXX and cmd_XXX, the regex should match an uploaded file name, and
	the cmd_XXX contains the command to execute with that file name.
	
	Commands should be newline delimited, and options should be whitespace 
	delimited, input the text {file} anywhere that a file path is expected.
	
	For example, if you had the config:
	
	{"regex_javaOne":"*.java", "cmd_javaOne":"/usr/bin/javachecker {file}"}
	
	The program would run /usr/bin/javachecker against every .java file that
	was uploaded.
	
	The output of cmd_javaOne should be a test anything protocol instance.
	
	'''
	
	def __init__(self):
		AbstractPlugin.__init__(self, "Executer", "Joseph Lewis <joehms22@gmail.com>", 0.1, "BSD 3 Clause",{},{'enabled':True})
	
	def process_upload(self, upload, test_config):
		'''Called when an upload has been input in to the program.
		
		Returns a dictionary with pairs corresponding to:
		{testname, TAPInstance}
		
		This software will parse 
		http://podwiki.hexten.net/TAP/TAP.html?page=TAP
		
		'''
		if test_config.get('enabled', False) == False:
			return None
		
		progs = self._config['programs'].split("\n")
		opts = self._config['programs'].split(" ")
		
