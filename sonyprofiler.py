#!/usr/bin/env python

"""
Sony Ebook Reader Time Profiler  
https://github.com/PicciMario/Sony-Ebook-Reader-Time-Profiler
Copyright (c) 2011 PicciMario <mario.piccinelli@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from xml.dom.minidom import *
import sys, base64, os, getopt
from datetime import datetime
import codecs

# archive for logging data
logData = []

# enabling single timeline features
enableBookCreationDate 		= False	# book creation date from cache.xml
enableBookmarkDate 			= True	# bookmark date from cache.xml
enableCurrentPosition 		= True	# current position from cacheExt.xml
enableDicHist 				= True	# dictionary lookups from cacheExt.xml
enableFreeHandMarkups		= True	# free hand markups from cacheExt.xml
enableAnnotationMarkups		= True	# annotation markups from cacheExt.xml
enableHistory				= True	# history records from cacheExt.xml
enableBookmarkMarkups		= True	# boormark markups from cacheExt.xml

# Globals
dirs = []
gnuplot = False

# stringa per la ricerca libri
findString = ""

# Usage
def banner():
	print("")
	print("Sony Ebook Reader Time Profiler")
	print("by PicciMario <mario.piccinelli@gmail.com>")
	print("")
	print("Analyzes files cache.xml, cacheExt.xml and media.xml found in")
	print("Sony Ebook Readers and creates a timeline of the events, on the")
	print("console and in a data file which can be used with GnuPlot.")
	print("")

def usage():
	banner()
	print("Usage:")
	print("-h              this help")
	print("-p <dir>        a dir to search for archive files (this option can be used many times)")
	print("-s <string>     a specific string to search in ebooks file names")
	print("-g              also writes output in a file \"out.dat\" suitable for being plotted by GnuPlot")
	print("")

# Command line options parser
try:
	opts, args = getopt.getopt(sys.argv[1:], "hp:s:g")
except getopt.GetoptError:
	usage()
	sys.exit(0)

for o,a in opts:
	if o == "-h":
		usage()
		sys.exit(0)
	elif o == "-p":
		dirs.append(a)
	elif o == "-s":
		findString = a
	elif o == "-g":
		gnuplot = True

# general purpose functions -----------------------------------------------------------------------------------------

# converts a raw date string (in the Sony Reader format) in a date object
def string2date(string):
	return datetime.strptime(string, "%a, %d %b %Y %H:%M:%S %Z")

# checks whether a node has the attributes listed in attrList
# returns an array of the same size of attrList if all attributes found,
# else returns None
def hasAttributes(node, attrList):
	ret = []
	for attr in attrList:
		if (node.hasAttribute(attr)):
			ret.append(node.getAttribute(attr))
		else:
			#print("WARNING: analyzing node %s, not found attribute %s"%(node.nodeName, attr))
			return None
	return ret

# extract text from a child (with specified name) of the specified node
# something like:
#   <node>
#      <child>TEXT</child>
#   </node>
# or returns an empty string if child not found
def textFromChild(node, childName):
	for child in node.childNodes:
		if (child.nodeType == Node.TEXT_NODE): continue
		if (child.nodeName == childName):
			return child.firstChild.toxml()
	return ""

# returns the first child of the specified node with a specified name
def getChildNode(node, childName):
	for child in node.childNodes:
		if (child.nodeType == Node.TEXT_NODE): continue
		if (child.nodeName == childName):
			return child
	return None

# splits a string into a list of sequences with the specified max length
def splitLen(seq, length):
	return [seq[i:i+length] for i in range(0, len(seq), length)]

# HEADER ---------------------------------------------------------------------------------------------------------------

banner()

# CACHE FILE -----------------------------------------------------------------------------------------------------------

def analyzeCacheFile(cacheFileName):
	print("Analyzing file \"%s\"..."%(cacheFileName))
	data = parse(cacheFileName)
	
	cacheExt = data.getElementsByTagName("cache")
	if (len(cacheExt) == 0):
		print("ERROR: no cache node at the first level")
		sys.exit(1)
	cacheExt = cacheExt[0]
	
	if (len(findString) > 0):
		print("Searching for string \"%s\""%findString)
	
	for node in cacheExt.childNodes:
		
		if (node.nodeType == Node.TEXT_NODE): continue
		
		# text node
		if (node.nodeName == "text"):
		
			if (node.hasAttribute("path")):
				path = node.getAttribute("path")
			else:
				path = ""
	
			# check whether the path contains the search string
			if (len(findString) > 0):
				if (path.find(findString) == -1):
					continue;
	
			print("- Found book entry: \"%s\""%path)
			
			# scan attributes searching for a "date" one
			attr = hasAttributes(node, ["date"])
			if (attr != None and enableBookCreationDate):
				logData.append([string2date(attr[0]), "Creation date ", path])
			
			# analyze child nodes
			for child in node.childNodes:
				
				if (child.nodeType == Node.TEXT_NODE): continue
				if (child.nodeName == "bookmarkDate" and enableBookmarkDate):
					logData.append([string2date(child.firstChild.toxml()), "Bookmark date", path])

# MEDIA FILE -----------------------------------------------------------------------------------------------------------

def analyzeMediaFile(mediaFileName):
	print("Analyzing file \"%s\"..."%(mediaFileName))
	data = parse(mediaFileName)
	
	xdblite = data.getElementsByTagName("xdbLite")
	if (len(xdblite) == 0):
		print("ERROR: no xdbLite node at the first level")
		sys.exit(1)
	xdblite = xdblite[0]
	
	records = xdblite.getElementsByTagName("records")
	if (len(records) == 0):
		print("ERROR: no records node at the second level")
		sys.exit(1)
	records = records[0] 
	
	if (len(findString) > 0):
		print("Searching for string \"%s\""%findString)
	
	for node in records.childNodes:
		
		if (node.nodeType == Node.TEXT_NODE): continue
		
		# text node
		if (node.nodeName == "cache:text"):
		
			if (node.hasAttribute("path")):
				path = node.getAttribute("path")
			else:
				path = ""
	
			# check whether the path contains the search string
			if (len(findString) > 0):
				if (path.find(findString) == -1):
					continue;
	
			print("- Found book entry: \"%s\""%path)
			
			# scan attributes searching for a "date" one
			attr = hasAttributes(node, ["date"])
			if (attr != None and enableBookCreationDate):
				logData.append([string2date(attr[0]), "Creation date ", path])
			
			# analyze child nodes
			for child in node.childNodes:
				
				if (child.nodeType == Node.TEXT_NODE): continue
				if (child.nodeName == "bookmarkDate" and enableBookmarkDate):
					logData.append([string2date(child.firstChild.toxml()), "Bookmark date", path])

# CACHE EXT FILE ------------------------------------------------------------------------------------------------

def analyzeCacheExtFile(cacheExtFileName):
	print("Analyzing file \"%s\"..."%(cacheExtFileName))
	data = parse(cacheExtFileName)
	
	cacheExt = data.getElementsByTagName("cacheExt")
	if (len(cacheExt) == 0):
		print("ERROR: no cacheExt at the first level")
		sys.exit(1)
	cacheExt = cacheExt[0]
	
	if (len(findString) > 0):
		print("Searching for string \"%s\""%findString)
	
	for node in cacheExt.childNodes:
		
		if (node.nodeType == Node.TEXT_NODE): continue
		
		# text node
		if (node.nodeName == "text"):
		
			if (node.hasAttribute("path")):
				path = node.getAttribute("path")
			else:
				path = ""
	
			# check whether the path contains the search string
			if (len(findString) > 0):
				if (path.find(findString) == -1):
					continue;
			
			print("- Found book entry: \"%s\""%path)
			
			# analyze child nodes
			for child in node.childNodes:
				
				if (child.nodeType == Node.TEXT_NODE): continue
				
				# "current position" node
				if (child.nodeName == "currentPosition" and enableCurrentPosition):
					attr = hasAttributes(child, ["date", "page", "pages", "pageOffset"])
					if attr != None:
						logData.append([
							string2date(attr[0]), 
							"Current position page %s of %s (offset %s)"%(attr[1], attr[2], attr[3]),
							path
						])
				
				# "preferences" node
				if (child.nodeName == "preferences"):
					dicHistories = getChildNode(child, "dicHistories")
					if (dicHistories != None):
						for dicHist in dicHistories.childNodes:
						
							if (dicHist.nodeType == Node.TEXT_NODE): continue
							
							# "dicHist" children nodes
							if (dicHist.nodeName == "dicHist" and enableDicHist):
								attr = hasAttributes(dicHist, ["date", "word", "contentsID"])
								
								if (attr != None):				
									logData.append([
										string2date(attr[0]), 
										"Looked for word \"%s\" in dictionary \"%s\""%(
											attr[1], 
											attr[2],
										),
										path
									])
																	
				# "markups" node
				if (child.nodeName == "markups" or child.nodeName == "deletedMarkups"):
					
					deleted = ""
					if (child.nodeName == "deletedMarkups"): deleted = "(Deleted) "
					
					for markup in child.childNodes:
						
						if (markup.nodeType == Node.TEXT_NODE): continue
						
						# "free hand" markup
						if (markup.nodeName == "freehand" and enableFreeHandMarkups):
							attr = hasAttributes(markup, ["date", "page", "pages", "pageOffset"])
							if (attr != None):
								
								svgFile = textFromChild(markup, "svgFile")
								
								logData.append([
									string2date(attr[0]), 
									"%sFreehand markup (%s) at page %s of %s (offset %s)"%(
										deleted,
										svgFile, 
										attr[1], 
										attr[2], 
										attr[3]
									),
									path
								])							
			
						# "annotation" markup
						if (markup.nodeName == "annotation" and enableAnnotationMarkups):
							attr = hasAttributes(markup, ["date", "page", "pages", "pageOffset"])
							attrName = hasAttributes(markup, ["name"])
							if (attr != None):	
								name = ""
								if (attrName != None): name = attrName[0]						
								logData.append([
									string2date(attr[0]), 
									"%sAnnotation markup (\"%s\", from %s to %s) at page %s of %s (offset %s)"%(
										deleted,
										name, 
										base64.b64decode(textFromChild(markup, "start")),
										base64.b64decode(textFromChild(markup, "end")),
										attr[1], 
										attr[2], 
										attr[3]
									),
									path
								])						
	
						# "bookmark" markup
						if (markup.nodeName == "bookmark" and enableBookmarkMarkups):
							attr = hasAttributes(markup, ["date", "page", "pages", "pageOffset"])
							if (attr != None):
								logData.append([
									string2date(attr[0]), 
									"%sBookmark markup at page %s of %s (offset %s)"%(
										deleted,
										attr[1], 
										attr[2], 
										attr[3]
									),
									path
								])		
	
						# "bookmark2" markup
						if (markup.nodeName == "bookmark2" and enableBookmarkMarkups):
							attr = hasAttributes(markup, ["date", "page", "pages", "pageOffset"])
							if (attr != None):
								logData.append([
									string2date(attr[0]), 
									"%sBookmark2 markup (%s) at page %s of %s (offset %s)"%(
										deleted,
										base64.b64decode(textFromChild(markup, "mark")),
										attr[1], 
										attr[2], 
										attr[3]
									),
									path
								])	
									
				# "history" node
				if (child.nodeName == "history" and enableHistory):
					for item in child.childNodes:
					
						 if (item.nodeType == Node.TEXT_NODE): continue
						 
						 if (item.nodeName == "item"):
						 	attr = hasAttributes(item, ["date", "page", "pages", "pageOffset"])
							if (attr != None):					 	
								logData.append([
									string2date(attr[0]), 
									"Reading page %s of %s (offset %s)"%(
										attr[1], 
										attr[2], 
										attr[3]
									),
									path
								])
# RUNNING THE EXAMS ------------------------------------------------------------------------------------------------

for dirname in dirs:

	cacheFileName = os.path.join(dirname, "cache.xml")
	cacheExtFileName = os.path.join(dirname, "cacheExt.xml")
	mediaFileName = os.path.join(dirname, "media.xml")
	
	if (os.path.isfile(cacheFileName)):
		analyzeCacheFile(cacheFileName)
	if (os.path.isfile(cacheExtFileName)):
		analyzeCacheExtFile(cacheExtFileName)
	if (os.path.isfile(mediaFileName)):
		analyzeMediaFile(mediaFileName)
		
# RESULTS ----------------------------------------------------------------------------------------------------------

print("")
print("Timeline data found (%i records):"%len(logData))
print("")

maxLengthForBookPath = 30
maxLengthForDescriptiveRow = 110

curMonth = -1
for element in sorted(logData, key=lambda data: data[0]):
	
	if (curMonth == -1 or curMonth != element[0].month): 
		curMonth = element[0].month
		print("###### %s/%s ###############################################################"%(element[0].month, element[0].year))		

	bookPath = element[2]
	if (maxLengthForBookPath > 0):
		if (len(bookPath) > maxLengthForBookPath):
			bookPath = "%s..."%bookPath[0:maxLengthForBookPath]
	
	if (maxLengthForDescriptiveRow > 0):
		rows = splitLen("%s of book %s"%(element[1], bookPath), 110)
		firstRow = True
		for row in rows:
			if firstRow:
				firstRow = False
				print("%s\t%s"%(element[0],row))
			else:
				print("\t\t\t  %s"%row)
	else:
		print("%s\t%s of book %s"%(element[0], element[1], bookPath))	

# GNUPLOT RESULTS ------------------------------------------------------------------------------------------------

if (gnuplot):
	# write to file out.dat for gnuplot timeline
	out_file_name = "out.dat"
	out_file = codecs.open(out_file_name, "w", "utf-8")
	
	# create set with file names
	books_set = set([])
	for element in logData:
		books_set.add(element[2])
	indice = 1
	books = []
	for element in books_set:
		books.append([indice, element])
		indice = indice + 1
	
	for element in sorted(logData, key=lambda data: data[0]):	
	
		bookPath = element[2]
	
		indice = 0
		for book in books:
			if (bookPath == book[1]):
				indice = book[0]
				break
	
		if (maxLengthForBookPath > 0):
			if (len(bookPath) > maxLengthForBookPath):
				bookPath = "%s..."%bookPath[0:maxLengthForBookPath]
		
		out_file.write("%s %i \"%s\\n%s\"\n"%(element[0].strftime("%Y-%m-%d-%H:%M:%S"), indice, element[1], bookPath))		
	
	out_file.close()
	
	print("\nWritten to gnuplot data file: %s\n"%out_file_name)
	print("GnuPlot file legend:")
	for book in books:
		print("%i\t%s"%(book[0], book[1]))	

print("")
