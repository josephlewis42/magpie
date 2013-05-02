
import re

def parse_tap(source):
	'''Parses the given text to create a new TestAnythingProtocol out of it.
	
	This doesn't quite match the grammar on CPAN, but that's okay, it should
	work for most of the varients I've seen propigated about through research
	in the past few days.
	
	'''
	
	tap = TestAnythingProtocol()
	
	last_test = None
	for line in source.split("\n"):
		
		if len(line) <= 1:
			continue
		
		if re.match('^\d+\.\.\d+$', line):
			continue # we have the plan!
		
		extra = re.search('^(\s|#)(?P<extratext>.+)$', line)
		if extra != None:
			if last_test != None:
				last_test['description'] += "\n" + extra.groupdict()['extratext']
			continue
		

		test = {'todo':None,
				'skip':None,
				"description":"",
				"passed":True} 
		
		parsed = re.search('^(?P<status>not ok|ok)\s*(?P<line>\d+)?\s*(?P<description>[^#]*)(#\s*(?P<extra_type>todo|skip)\s*(?P<extra>.*))?$', line, re.IGNORECASE)
		
		if parsed == None:
			continue # not a good sign, improperly formattted input

		parsed = parsed.groupdict()
		test['passed'] = True if parsed['status'] == "ok" else False
		test['description'] = parsed['description'] if parsed['description'] != None else ""
		
		if parsed['extra_type'] != None:
			parsed['extra'] = parsed['extra'] if parsed['extra'] else ""
			if "skip" in parsed['extra_type'].lower():
				test['skip'] = parsed['extra']
			elif "todo" in parsed['extra_type'].lower():
				test['todo'] = parsed['extra']
		
		tap._tests.append(test)
		last_test = test
	
	return tap


class TestAnythingProtocol:
	''' A representation of results a suite for tests that allows them to report
	using the TestAnythingProtocol.
	
	'''
	
	_tests = None
	_title = None # the title for the tests before the toHtml is called
	
	_pass_color = "#04f200"
	_fail_color = "#f20004"
	
	def __init__(self, title=""):
		''' Creates a new empty TestAnythingProtocol and gives it the supplied
		title.
		'''
		
		self._tests = []
		self._title = title
	
	def pass_test(self, description, todo=None, skip=None):
		''' Call when a test passed.
		
		description - String, the description of the test.
		todo|skip - mutually exclusive, a string in either of these will append
		a TODO or SKIP to the output with the given string afterwards.
		'''
		self.assert_true(True, description, todo=todo, skip=skip)
		
	def fail(self, description, todo=None, skip=None):
		''' Call when a test failed.
		
		description - String, the description of the test.
		todo|skip - mutually exclusive, a string in either of these will append
		a TODO or SKIP to the output with the given string afterwards.
		'''
		self.assert_true(False, description, todo=todo, skip=skip)
		
	def assert_true(self, condition, description, fail_description=None, todo=None, skip=None):
		''' Call to report the results of something being true or not.
		
		condition - a boolean to tell if the test passed or failed
		description - String, the description of the test.
		fail_description - String to display if condition is False, if None, 
		description is used instead
		todo|skip - mutually exclusive, a string in either of these will append
		a TODO or SKIP to the output with the given string afterwards.
		'''
		if fail_description != None and condition == False:
			description = fail_description
		
		test = {"passed":condition, "todo":todo, "skip":skip, "description":description}
		self._tests.append(test)
		
	def to_html(self, pass_i18n="Pass", fail_i18n="Fail", status_i18n="Status", description_i18n="Description", extra_i18n="Extra"):
		'''Converts this instance of the TAP to an HTML table.
		
		Params
		
		pass_i18n -- Text to use in place of "Pass" in the table results.
		fail_i18n -- Text to use in place of "Fail" in the table results.
		status_i18n -- i18n for "Status"
		description_i18n -- i18n for "Description"
		extra_i18n -- i18n for "Extra"
		
		'''
		
		output = """
<table border='1'>
	<tr><th colspan='3'>{title}</th></tr>
	<tr><th>{status}</th><th>{desc}</th><th>{extra}</th></tr>
""".format(title=self._title, status=status_i18n, desc=description_i18n,extra=extra_i18n )
		
		for test in self._tests:
			color = self._pass_color if test['passed'] else self._fail_color
			status = pass_i18n if test['passed'] else fail_i18n

			extra_info = test['todo'] if test['todo'] else ""
			extra_info = test['skip'] if test['skip'] else extra_info
			
			output += """
	<tr>
		<td style="background-color:{};">{}</td>
		<td>{}</td>
		<td>{}</td>
	</tr>""".format(color, status, test['description'].replace("\n", "<br/>"), extra_info)
		
		output += "\n</table>"
		
		return output
	
	def __str__(self):
		'''Returns a tap style output for the given interface.'''
		if len(self._tests) == 0:
			return ""
		
		output = "1..{}\n".format(len(self._tests))
		
		if self._title != "":
			output += "#{}\n".format(self._title)
		
		for i, test in enumerate(self._tests):
			status = "ok" if test['passed'] else "not ok"
			status += " {} ".format(i + 1)
			
			if test['description'] != None:
				status += str(test['description']).replace("\n","\n\t")
			
			if test['todo']:
				status += " # TODO " + test['todo']
			elif test['skip']:
				status += " # SKIP " + test['skip']
			
			status += "\n"
			output += status
		
		return output
