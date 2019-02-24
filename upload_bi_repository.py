#!/usr/bin/python
import os
import argparse
from PentahoControl import PentahoControl

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--local_path", help="path to upload to pentaho")
parser.add_argument("-r", "--remote_path", help="path where your folder will be uploaded")
parser.add_argument("-u", "--user", help="pentaho user")
parser.add_argument("-p", "--password", help="pentaho passwd")
parser.add_argument("-c", "--config", help="path to the config file")
parser.add_argument("-e", "--environment", help="path to the config file")
parser.add_argument("--url", help="URL to the pentaho BA server")
args = parser.parse_args()

pc = PentahoControl(args)
if (pc.loadConfig()):
	pc.clone()
else:
	print 'There was a problem reading config. Please review'
	parser.print_usage()
