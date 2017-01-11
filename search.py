import os, fnmatch
import shutil
	
def findAndCopy(pattern, path, destPath):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
				srcfile = os.path.join(root, name)
				result.append(srcfile)
				destFolderPath = destPath + "\\" + root.split("\\")[-2] + "\\" + root.split("\\")[-1]
				if not os.path.exists(destFolderPath):
					os.makedirs(destFolderPath)
					shutil.copy(srcfile,destFolderPath)
    return result

def findAndCopyAll(pattern, path, destPath):
	# result = []
	for root, dirs, files in os.walk(path):
		for name in files:
			if fnmatch.fnmatch(name, pattern):
			# srcfile = os.path.join(root, name)
				# result.append(srcfile)
				destFolderPath = destPath + "\\" + root.split("\\")[-2] + "\\" + root.split("\\")[-1]
				# print root
				if not os.path.exists(destFolderPath):
					shutil.copytree(root,destFolderPath)
	# return result
# \\10.58.1.26\9.2_dev\9.2\
# result = findAndCopyAll('*.xtc', r'\\10.58.1.26\9.2_dev\9.2',r'D:\MyBox\Work\SAP\QA\TestCase\ServiceLayer\test\920dev')
# print len(result)

def findAndCopyPureXTC(pattern, path, destPath):
	totalmixCase = 0
	totalPureCase = 0
	for root, dirs, files in os.walk(path):
		#check if pure xtc in files
		#check if contain xtc
		#copy folder if pure
		print root
		totalNum = 0
		XTCNum = 0
		for name in files:
			if fnmatch.fnmatch(name, pattern):
				XTCNum = XTCNum + 1
		totalNum = len(files)
		# print totalNum,XTCNum
		if XTCNum == totalNum and XTCNum > 0:
			totalPureCase = totalPureCase + 1
			destFolderPath = destPath + "\\" + root.split("\\")[-2]
			# print root
			# print destFolderPath
			if not os.path.exists(destFolderPath):
				shutil.copytree(root.replace(root.split("\\")[-1],''),destFolderPath)
		elif XTCNum < totalNum and XTCNum > 0:
			totalmixCase = totalmixCase + 1
	print totalmixCase,totalPureCase

# findAndCopyPureXTC('*.xtc', r'\\10.58.1.26\9.2_dev\9.0',r'D:\MyBox\Work\SAP\QA\TestCase\ServiceLayer\test\9.0')

def findTotalCase(pattern, path):
	totalNum = 0
	for root, dirs, files in os.walk(path):
		for name in files:
			if fnmatch.fnmatch(name, pattern):
				totalNum = totalNum + 1
	print totalNum

findTotalCase('*.xrt', r'\\10.58.1.26\9.2_dev\8.8 SP01')

from xml.dom import minidom
import simplejson as json
def parse_element(file_path):
	result = []
	for file in os.listdir(file_path):
		#print file
		dom = minidom.parse(file_path + '\\' + file)
		for child in dom.getElementsByTagName('action'):
			result.append(child.getAttribute('Title'))
	#print result
	return result
	
#if __name__ == '__main__':
#	file_path = r'D:\MyBox\Work\SAP\QA\TestCase\Service Layer\xtc\920'
#	result = parse_element(file_path)
#	f = open(r'D:\MyBox\Work\SAP\QA\TestCase\Service Layer\xtc\xtcTitle_01.txt', 'w')
#	for item in result:
#		f.write("%s\n" % item.split(' ')[0])
#	f.close()
	
def getService(file_path):
	result = []
	for file in os.listdir(file_path):
		result.append(os.path.splitext(file)[0])
	return result
	
#if __name__ == '__main__':
#	file_path = r'D:\P4\BUSMB_B1\SBO\9.2_COR\Source\SDK\ServiceLayer\api\xml'
#	result = getService(file_path)
#	f = open(r'D:\MyBox\Work\SAP\QA\TestCase\Service Layer\xtc\api.txt', 'w')
#	for item in result:
#		f.write("%s\n" % item)
#	f.close()
	
def match(file_1,file_2,file_out):
	with open(file_1, 'r') as f:
		xtc = f.readlines()
	with open(file_2, 'r') as f:
		api = f.readlines()
		
	result = []
	
	for i in xtc:
		if i in api:
			result.append(i)
	
	print len(result)
	#print result
	FO = open(file_out, 'w')
	
	
	#print result
	for item in result:
		FO.write("%s\n" % item)
	FO.close()
	# file1.close()
	# file2.close()

# if __name__ == '__main__':
	# file_1 = r'D:\MyBox\Work\SAP\QA\TestCase\Service Layer\xtc\xtcTitle_01.txt'
	# file_2 = r'D:\MyBox\Work\SAP\QA\TestCase\Service Layer\xtc\api.txt'
	# file_out = r'D:\MyBox\Work\SAP\QA\TestCase\Service Layer\xtc\compareResult.txt'
	# match(file_1,file_2,file_out)

# -*- coding: utf-8 -*-
from xml.dom import minidom
import simplejson as json
import os, fnmatch
import shutil

#parse xtc to dict_data
def parse_check(element):
	# If xtc not contain OBJECT, no need to parse it
	if(len(element.getElementsByTagName('OBJECT')) <= 1):
		return 0
	for object in element.getElementsByTagName('action'):
		method = object.getAttribute('Method')
		if method not in ('add','Add','update','Update','remove','Remove'):
			return 0
	for object in element.getElementsByTagName('OBJECT'):
		if 'Service' in str(object.getAttribute('Type')):
			return 0
	# ToDo: check if type supported in SL
	return 1

def batch_check(xtcFolder):
	# jmx = jmxTemplate
	# print "hehe"
	for root, dirs, files in os.walk(xtcFolder):
		for name in files:
			# print name
			if name.endswith(".xtc"):
				xtcFile = os.path.join(root, name)
				dom = minidom.parse(xtcFile)
				if parse_check(dom) == 0:
					print xtcFile
					# print xtcFile
				# addJmxToXrt()
				# print "end"

# replace xtc to jmx in xrt file
def replace_xrt(xrtFile,jmxFolder):
	# step1, analyse xrtFile;
	xrt_dom = minidom.parse(xrtFile)
	for testStep in xrt_dom.getElementsByTagName('TestStep'):
		# print "I am a test step"
		name = testStep.getAttribute('Name')
		type = testStep.getAttribute('Type')
		file = testStep.getAttribute('File')
		print name
		# replace for xtc teststep
		if(name.endswith(".xtc")):
			jmxFileName = file.split('\\')[-1].split('.')[0] + ".jmx"
			# print jmxFileName
			# exist jmx file in folder
			# print os.path.join(jmxFolder, jmxFileName)
			if os.path.exists(os.path.join(jmxFolder, jmxFileName)):
				print "I am in jmx"
				testStep.attributes['Name'].value = jmxFileName
				testStep.attributes['Type'].value = "JMeter"
				testStep.setAttribute('FilePath',file.replace("xtc","jmx"))
				# testStep.attributes['FilePath'].value = file.replace("xtc","jmx")
				del testStep.attributes['File']
				print testStep.attributes['Name'],testStep.attributes['Type'],testStep.attributes['FilePath']
	# step2, write to xrtFile/

	xrtFile = open(xrtFile, 'w')
	xrt_dom.writexml(xrtFile)
	xrtFile.close()
	# print xrt_dom


# if __name__ == '__main__':
# 	xrtFile = r'D:\MyBox\Work\SAP\QA\TestCase\ServiceLayerTools\test\Sanity_DE_JVM.xrt'
# 	jmxFolder = r'D:\MyBox\Work\SAP\QA\TestCase\ServiceLayerTools\test\XTC\test'
# 	# jmxTemplate = r"D:\MyBox\Work\SAP\QA\TestCase\ServiceLayerTools\SLTemplate.jmx"
# 	replace_xrt(xrtFile,jmxFolder)