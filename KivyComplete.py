
###
# -*- coding: utf-8 -*-

import sys
import sublime, sublime_plugin
import subprocess, time
import os
import re
import spdb

# data files
dirname 		= os.path.dirname(__file__)
api_list 		= []
lib_querier 	= {}
method_querier 	= {}


IS      = isinstance
_cls    = {}
_file 	= open(os.path.join(dirname,'api2.txt'))
_api 	= set([line for line in _file.read().split('\n')]); _file.close()
scope_ptn  = r'([A-Z][a-zA-Z]+)|(canvas.[a-z]+)'
import_ptn = r'#:import ([a-zA-Z]+\.[a-zA-Z_\.]+)'


tail 			= lambda s,sep: s[s.rfind(sep)+1:]
rowcol  		= lambda view: view.rowcol(view.sel()[0].begin())
rowcol_to_point = lambda view, row, col: view.text_point(row, col)
def trace(msg):
	#pass
    sys.stderr.write(str(msg) + '\n')    

def iscls(s):
	s = s.strip(':').strip()
	if not s: return False
	return s[0] == '<' and s[-1] == '>' and '@' in s

def keytrace(**kargs):
	output = ''
	for k,v in kargs.items():
		if 		 IS(v, list): 	v = str(v)
		elif not IS(v, str): 	v = str(v)
		msg = '{}:{}'.format(k, v)
		output = output + msg +",  "
	sys.stderr.write(output + '\n') 

def get_loc(view, shiftr=0, shiftc=0):
	row,col = rowcol(view)
	loc = rowcol_to_point(view, row + shiftr, col+shiftc)
	return loc

def get_linen(view, div=0):
	loc  = get_loc(view, div, 0)	
	locb = get_loc(view, -1, 0)
	keytrace(loca=loc, locb=locb)
	ret = view.substr(view.line(loc))
	retb = view.substr(view.line(locb))
	keytrace(lineA=ret, lineB=retb)
	return ret

def get_line_region(view, shiftr=0, shiftc=0):
	row,col = rowcol(view)
	loca = rowcol_to_point(view, row + shiftr, 0)
	locb = rowcol_to_point(view, row + shiftr, col)
	return sublime.Region(loca, locb)

def get_line_by_row(view,row):
	loca = rowcol_to_point(view, row , 0)
	return view.substr(view.line(loca))

def get_region(view,a,b):
	return sublime.Region(a,b)

def getScope(view, row, current_line):
	indent 	= len(current_line) - len(current_line.lstrip())
	substr, getline  = view.substr, view.line
	for i in range(row,0,-1):
		line    = substr(getline(rowcol_to_point(view, i,0)))
		if line:
			_indent = len(line) - len(line.lstrip())
			if _indent < indent:
				if iscls(line):
						return line.strip(' <>\t:').strip().split('@')[1].split('+')
				else:	return [line.strip(' \t:').strip()]

def elem(a,b):
	if IS(a,str):
		if IS(b,list):  		return a in b
		else:    				return a in b
	elif IS(b,str):		
		for ai in a:
			if ai in b:			return True
		return False

	for ai in a:
		if ai in b: 			return True
	return False

def is_kivylang(view):
    return '/KivyLang.tmLanguage' in view.settings().get('syntax')

def show_path():
	pass


class UpdateFromPhotoShopCommand(sublime_plugin.TextCommand):
	pass

class UpdateKivyRunnerTemplateCommand(sublime_plugin.TextCommand):
	pass

class GenKivyRunnerTemplateCommand(sublime_plugin.TextCommand):
	pass


class KivylangImportCommand(sublime_plugin.TextCommand):
	def run(self, edit, **kargs):
		if is_kivylang(self.view):
			keytrace(run=kargs['line'])
			ra,rb = kargs['ra'], kargs['rb']
			if kargs['line'][0] == '#': self.view.replace( edit, sublime.Region(ra,rb), kargs['line'])
			else:						self.view.replace( edit, sublime.Region(ra,rb), "#:"+ kargs['line'])
				

class KivyLangCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if is_kivylang(self.view):
			s 	= self._run(s)

	def _run(self):
		packages_path = join(sublime.packages_path(), package)
		os.chdir(packages_path)
		settings 	= sublime.load_settings(package + ".sublime-settings")
		kivy_path 	= settings.get("kivy_path")
		templatep 	= setting.get("template_runner")
		ps_path     = setting.get("ps_path")


class KivyComplete(sublime_plugin.EventListener):
	cls_scanned = False
	cls_rows = []
	altered_cls_rows = []
	last_line = ''
	current_scope = ''
	import_loc = 0
	current_row = 0
	last_row  = 0
	def isInterSectRowRegions(self, row):
		for _row in self.cls_rows:
			if row == _row: return True
		return False

	def parsecls(self,ret , line):
		clsname,inherits = line.strip('>< \t\n').split('@')
		if '+' in inherits:	inherits = inherits.split('+')
		else: 				inherits = [inherits]
		keytrace(parseCls=True, line=line)
		for _inherit in inherits:
			for pth in libpaths:
				if _inherit in pth:
					if not pth in ret: ret[pth] = set([clsname])
					else:					 ret[pth].add(clsname)
		return ret

	def testRegionChanged(self, view):
		keytrace(testRegionChanged='')
		ret = {}
		for row in self.cls_rows:
			line = get_line_by_row(view, row)
			if iscls(line):
				self.parsecls(ret, line)
				for pth,clsname in ret.items():
					if pth in _cls:
						if clsname in _cls[pth]: pass
						else: 					 return True
					else:						 return True
			else:				  				 return True

	def scancls(self, view, rows=False):
		ret 		= {}
		clsrows 	= []
		substr 		= view.substr
		cls_rows = self.cls_rows
		parsecls 	= self.parsecls
		self.cls_scanned = True
		#------------------------------------------
		if rows:
			for _row in rows:
				i = cls_rows.index(_row)
				line = get_line_by_row(view, _row)
				if line.strip(): parsecls(_cls, line)
			return
		#---------------------------------------------
		for i in range(500):
			row 	=  i
			line 	=  get_line_by_row(view, row)
			if line.strip():
				line = line.rstrip(':').rstrip()
				keytrace(scanClsRos=True, row=row, line = line)
				if iscls(line):
					clsrows.append(row)
					ret = parsecls(ret, line)
					
				elif line[0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz':
					# exit when scannig walk through widget
					_cls = ret
					self.cls_rows = clsrows
					return
				elif not line[0]:
					pass


	def alterClsRegion(self,view, line, eatline=False, newline=False):
		row, col = rowcol(view)
		altered_cls_rows = self.altered_cls_rows
		is_intersect = self.isInterSectRowRegions
		def alter_region(l,r,d):
			keytrace(alterRegion=d, l=l, r=r)
			cls_rows = self.cls_rows
			for i in range(l,r):
				cls_rows[i]+= d

		if newline:
			if self.testRegionChanged(view): self.cls_scanned = False
			
		#---------------------------------------------
		# when:
		# enter newline before class region
		# delete newline before class region
		# altering class region
		if eatline or newline:
			for i, _row in enumerate(self.cls_rows):
				if   row < _row and eatline: 	
					alter_region(i, len(self.cls_rows), -1)
					keytrace(alterClsRegion=True, eatline=eatline, cls_rows=self.cls_rows)
					return
				elif row < _row and newline:	
					alter_region(i, len(self.cls_rows), 1)
					keytrace(alterClsRegion=True, newline=newline, cls_rows=self.cls_rows)
					return
		
		#-------------------------------------
		# when
		# create class region
		if not eatline and not newline and line.strip():
			if iscls(line):
				keytrace(catch_editing_cls_region=True)
				self.parsecls(_cls, line)
				if not row in self.cls_rows:
					self.cls_rows.append( row )
				return

	def on_query_context(self,view, key, operator, operand, match_all):
		if is_kivylang(view):
			keytrace(onqueryContext='on_query_context', key=key, operator=operator)

	# -----------------------------------------------------
	# 				catch text commands
	#------------------------------------------------------
	def on_text_command(self, view, command_name, args):
		if is_kivylang(view):
			keytrace(command_name=command_name, args = args)
			if not self.cls_scanned: self.scancls(view)

			if   command_name == 'left_delete': 
				row, col = rowcol(view)
				if col == 0:
					self.alterClsRegion(view, '', eatline=True)

			elif command_name == 'insert':		
				if args == {'characters':'\n'}:
					# read current line
					l = get_linen(view, 0)
					self.alterClsRegion(view, l, newline=True)
					#----------------------------------------------
					# translate "#:import b.a" to "#:import a b.a"
					translate = re.search(import_ptn, l)
					keytrace(translate_import=translate != None)
					if translate:
						nl 		= translate.group().split(' ')
						nl 		= ' '.join([nl[0] , tail(nl[1], '.') + ' ' + nl[1]])
						region  = get_line_region(view)
						keytrace(translate_currentline=nl)
						view.run_command('kivylang_import', dict(ra=region.a, rb=region.b, line=nl))

				elif args == {'characters':'>'}:
					pass
			elif command_name == 'drag_select': 
				row, col = rowcol(view)
				self.last_row = row

			elif command_name == 'move':
				row, col = rowcol(view)
				if args['by'] == 'lines':
					d = 1 if args['forward'] else -1
					self.current_row = row+d

			# commit autocomplete
			elif command_name == 'insert_best_completion':
				substr, getline = view.substr, view.line
				current_line 	= get_linen(view, 0)
				keytrace(bestComplete_line=current_line, args=args)


	def on_query_completions(self, view, prefix, locations):
		substr 			= view.substr
		getword 		= view.word
		getline 		= view.line
		isClassRegion 	= lambda row     : row in self.cls_rows
		getpath 		= lambda lin    : lin[lin.rfind(' ')+1:]	

		if is_kivylang(view):
			location = locations[0]
			row,col  = view.rowcol(view.sel()[0].begin())

			current_line 	= get_linen(view, 0)
			last_line 		= get_linen(view, -1)
			scopes 		= getScope(view, row, current_line)
			path 		= getpath(current_line)
			secs 	= path.split('.')
			lib 	= secs[0]

			self.last_line 		= current_line
			self.current_scope 	= scopes

			if current_line.strip():
				keytrace(	current_line  = current_line,	last_line = last_line,
							current_scope = scopes,			path = path,
							lib = lib,						loc= location)
				#-----------------------------------------------
				# import snippet: transform import kivy to #:import kivy
				if 'import' == current_line[:6]:
					self.import_loc = location - len(current_line)
					region = sublime.Region(self.import_loc, location)
					view.run_command( 'kivylang_import' ,dict(ra=region.a, rb=region.b, line=current_line))
					return
				#--------------------------------
				# lib auto completion
				if lib in "kivy": 
					if len(secs) == 1:
						trace('lib completeitons')
						return [('kivy','kivy')]
					trace('--------------------------------------')
					ret = [i for i in libpaths if path in i]
					trace(','.join(ret))
					return [(i,i.split(path[:-1])[1]) for i in ret]

			if scopes:
				#----------------------------------
				# kivy widget property autocomplete
				

				ret = [lib_querier[k] for k in libpaths if elem(scopes, k)]
				ret = set([i for rec in ret for i in rec])
				if path.strip(): 	ret = [[prop, prop] for prop in ret if path in prop]
				else:    			ret = [[prop, prop] for prop in ret]

				keytrace(widget_completion=True, scopes=scopes, clsvalues = list(_cls.values()))
				for scope in scopes:
					if scope in _cls.values():
						keytrace(fetch_class_scope_attributes=True)
						retB = [lib_querier[pth] for pth,clss in _cls.items() for cls in clss if cls in libpaths ]
						#retB = set([i for rec in retB for i in rec ])
						retB = [[prop, prop] for rec in retB for prop in rec if path in prop]
						ret = ret + retB
				keytrace(classes=list(_cls.values()))
				for rec in ret:
					trace(','.join(rec))
				return ret




#-------------------------------------------
#		read api list
for line in _api:
	if line:
		rec = line.split(' ', 1)
		raw = ' '.join(rec[1:])
		fn = rec[0]
		libpth = raw.strip(' ,()\n\r').strip(').')
		l = len(libpth)
		mloc, aloc, mmloc, cloc = libpth.rfind('method'), libpth.rfind('attribute'), libpth.find('in module '), libpth.find('class in ')
		is_method 		= mloc  == l -6
		is_attr 		= aloc  >= l - 9
		is_mod_method 	= mmloc == 0
		is_class 		= cloc  == 0

		if    is_method:	_libpth = libpth[:mloc]
		elif  is_attr: 		_libpth = libpth[:aloc]
		elif  is_mod_method:_libpth = libpth[10:]
		elif  is_class:     _libpth = libpth[9:]

		if 'class in' in _libpth:
			trace('unknown bug triggered!')
			_libpth = libpth[9:]

		api_list.append([fn, _libpth])

# dict:methodname: [libs]
method_querier 	= {m[0]:[] for m in api_list}
# dict:libpath: [methods]
lib_querier 	= {libpth[1]:[] for libpth in api_list}
for line in api_list:
	fn, libpth = line
	method_querier[fn].append(libpth)
	lib_querier[libpth].append(fn)

libpaths 	= set(list(lib_querier.keys()))
methods 	=  [ [k,v] for k,v in method_querier.items()]  

#print method_querier['text']
#print lib_querier['kivy.adapters.models']