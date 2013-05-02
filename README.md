Magpie
======

Magpie is an automated testing tool aimed at automated assignment submission and
processing. 

Magpie natively supports the submissions from:

* E-Mail
* HTTP

And comes with the ability to grade Scratch files. Additional frontends and 
backends come from Python scripts that extend the `AbstractPlugin` class and
are placed in the plugins directory.

Magpie generates and can parse tests that conform to the 
[Test Anything Protocol](http://en.wikipedia.org/wiki/Test_Anything_Protocol).

The Test Anything Protocol has modules available for most modern languages. 
Oftentimes these modules provide a wrapper to the language's normal testing
framework (e.g. JUnit).

Running
-------

To run the software, run `start.py` with Python 2 or Python 3, it 
will then start the HTTP server on port 8000 and start checking

Configuration
-------------

To configure the software, run it once, then edit the `config.json`
file in the main folder.

From here you can change:

* the email account to check for submission from
* the name of the tool
* the displayed messages from the tool
* the port the webserver starts on
* ...


