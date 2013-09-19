Magpie
======

Magpie is an automated testing tool aimed at automated assignment submission and
processing. Currently it supports grading Scratch and Scratch2 documents.

It accepts submissions from both Email or HTTP so students do not need to use
a VPN if the server hosting it is behind a firewall.

Installing
----------

The easiest way to get the software is by running the install_magpie.sh script that you can download from the scripts folder.

The script automatically grabs the source, removes the old version and starts the new one with default settings.

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


Extending
---------

Magpie is easy to extend, just write your own script and plop it in the plugins
directory.

Magpie generates and can parse tests that conform to the 
[Test Anything Protocol](http://en.wikipedia.org/wiki/Test_Anything_Protocol).

The Test Anything Protocol has modules available for most modern languages. 
Oftentimes these modules provide a wrapper to the language's normal testing
framework (e.g. JUnit).

