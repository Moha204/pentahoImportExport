import ConfigParser
import json
import os
import requests
import tempfile
import time
import shutil

from datetime import datetime
from filecmp import dircmp
from requests.auth import HTTPBasicAuth
from zipfile import ZipFile

class PentahoControl:
	def __init__(self, args):
		self.args = args
		self.ignore_list = []
		if os.path.exists(".phignore"):
			with open(".phignore") as f:
				for line in f:
					if line.endswith('\n'):
						self.ignore_list.append(line[:-1])
		
	def loadConfig(self):
		config = ConfigParser.ConfigParser()

		self.configPath = "config.ini" if (self.args.config is None) else self.args.config
		if not (self.configPath is None):
			config.read(self.configPath)
		
		environment = "TEST" if (self.args.environment is None) else self.args.environment
		self.username = config.get(environment,'username') if (self.args.user is None) else self.args.user
		self.password = config.get(environment,'password') if (self.args.password is None) else self.args.password
		self.url = config.get(environment,'url') if (self.args.url is None) else self.args.url
		self.remotePath = config.get(environment,'remote_path') if (self.args.remote_path is None) else self.args.remote_path
		self.localPath = config.get(environment,'local_path') if (self.args.local_path is None) else self.args.local_path
		self.backupPath = config.get(environment,'backup_path') if (self.args.local_path is None) else self.args.local_path
		
		return not (self.username is None or self.password is None or self.url is None or self.remotePath is None \
			or self.localPath is None or self.backupPath is None)
			
	def clone(self):
		if (self.remotePathExists()):
			print "remote path already exists: downloading backup at " + self.backupPath
			if not (self.doRemoteBackup()):
				return
				
		for root, subdirs, files in os.walk(self.localPath):
			for subdir in subdirs:
				path = os.path.join(root, subdir)
				uploadable = True
				for element in self.ignore_list:
					if element  in path:
						uploadable = False
						print "ignoring dir: " + path
						break
				if uploadable:
					path = path.replace(self.localPath, '', 1)
					if not (self.createPentahoDir(path)):
						return
						
			for file in files:
				path = os.path.join(root, file)
				uploadable = True
				for element in self.ignore_list:
					if element  in path:
						uploadable = False
						print "ignoring dir: " + path
						break
				if uploadable:
					if not (self.uploadFile(path)):
						return
					
	def createPentahoDir(self, directory):
		path = self.remotePath + directory
		path = path.replace('/', ':')
		response = requests.put(self.url + '/pentaho/api/repo/dirs/' + path, auth=HTTPBasicAuth(self.username, self.password))
	   
		if (response.status_code > 300):
			print self.url + '/pentaho/api/repo/dirs/' + path
			print "There was a problem creating directory " + directory +". error code: " + str(response.status_code)
			return False
		return True
		
	def remotePathExists(self):
		path = self.remotePath.replace('/', ':')
		response = requests.get(self.url + '/pentaho/api/repo/files/' + path + '/properties', auth=HTTPBasicAuth(self.username, self.password))
		return response.status_code == 200
		
	def downloadPath(self, remotePath, localPath):
		path = remotePath[:-1] if remotePath.endswith(('/', '\\')) and len(remotePath) > 1 else remotePath
		path = path.replace('/', ':')
		response = requests.get(self.url + '/pentaho/api/repo/files/' + path + '/download', auth=HTTPBasicAuth(self.username, self.password))
		print self.url + '/pentaho/api/repo/files/' + path + '/download'
		with open(localPath, "wb") as downloader:
			downloader.write(response.content)
		print response.status_code
		return response.status_code == 200
		
	def getPentahoFiles(self):
		path = self.remotePath[:-1] if self.remotePath.endswith(('/', '\\')) and len(self.remotePath) > 1 else self.remotePath
		
		if not (os.path.exists(tempfile.gettempdir() + '/pentaho')):
			os.mkdir(tempfile.gettempdir() + '/pentaho')
		filename = tempfile.gettempdir() + '/pentaho/pentaho-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.zip'
		
		if not (self.downloadPath(path, filename)):
			print "Unable to download files. Aborting"
			return False
			
		zip = ZipFile(filename)
		zip.extractall(filename.split(".zip")[0])
		downloadPath = filename.split(".zip")[0] + '/' + path.split('/')[-1]
		
		comparator = dircmp(self.localPath, downloadPath)
		print 'The following files will be overwritten with remote files:'
		self.printReport(comparator)
		self.doLocalBackup()
		shutil.rmtree(self.localPath)
		shutil.move(downloadPath, self.localPath)
		
	def doRemoteBackup(self):
		backupFile = self.backupPath + 'backup' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.zip'
		if not (self.downloadPath(self.remotePath, backupFile)):
			print "There was a problem doing backup. Aborting"
			return False
		print "remote backup done in %s" % (backupFile)
		return True
		
	def doLocalBackup(self):
		if not (os.path.exists(tempfile.gettempdir() + '/pentaho/local_bkp')):
			os.mkdir(tempfile.gettempdir() + '/pentaho/local_bkp')
		filename = tempfile.gettempdir() + '/pentaho/local_bkp/bkp-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.zip'
		bkp = ZipFile(filename, 'w')
		for root, subdirs, files in os.walk(self.localPath):
			for file in files:
				path = os.path.join(root, file)
				bkp.write(path)
		
		print "Backup of overwriten files done in: %s" % (filename)
		bkp.close()
				
	def uploadFile(self, file):
		path = file.replace(self.localPath, '', 1)
		print '--------'
		print self.remotePath
		print '--------'
		path = self.remotePath + path
		path = path.replace(os.sep, ':')
		with open(file, 'rb') as data:
			response = requests.put(self.url + '/pentaho/api/repo/files/' + path, data=data, auth=HTTPBasicAuth(self.username, self.password))
		
		print self.url + '/pentaho/api/repo/files/' + path
		if (response.status_code >= 300):
			print self.url + '/pentaho/api/repo/dirs/' + path
			print "There was a problem uploading file " + file + ". error code: " + str(response.status_code)
			return False
		return True
		
	def printReport(self, dircmp):
		for name in dircmp.common_files:
			print "%s/%s" % (dircmp.left, name)
		for subdir in dircmp.subdirs.values():
			self.printReport(subdir)

