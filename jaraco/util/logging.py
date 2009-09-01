from __future__ import absolute_import

def add_options(parser):
	parser.add_option('-l', '--log-level', default='info', help="Set log level (DEBUG, INFO, WARNING, ERROR)")

def setup(options):
	import logging
	logging.basicConfig(level=getattr(logging, options.log_level.upper()))