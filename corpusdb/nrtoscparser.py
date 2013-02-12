#

"""
Part of corpusdb, corpus-based processing for SuperCollider + Python.

Overview
========

etc.

"""

__version__ = '1.0'
__author__ = 'Thomas Stoll'
__copyright__ = "Copyright (C) 2012, Thomas Stoll, All Rights Reserved"
__license__ = "gpl 3.0 or higher"
__email__ = 'tms@kitefishlabs.com'


import struct, math, os, string
from scosc import OSC
from scosc import tools
from scosc import osctools

class NRTOSCParser:
	def __init__(self, sr=44100, anchor='/Users/kfl/'):
		self.lib = { 'bndl': self.padBytes('#bundle'), 'zero': self.padBytes(0), 'anchor': anchor }
	
	def absToOSCTimestamp(self, abs):
		return struct.pack('!LL', math.floor(abs), long(float(abs - long(abs)) * 4294967296L))
	
	def padBytes(self, val):
		if type(val) == type('str'):
			pad = (math.ceil(((len(val) + 1) / 4.0)) * 4)
			ba = bytearray(val)
			while len(ba) < pad:
				ba.append(0)
			return ba
		elif type(val) == type(1):
			return struct.pack('!i', val)
		elif type(val) == type(0.2):
			return struct.pack('!f', val)

	def processAndWriteFile(self, score, output):
		header = bytearray("\x00\x00\x00$#bundle\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10/g_new\x00\x00,i\x00\x00\x00\x00\x00\x01\x00\x00\x00$#bundle\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10/g_new\x00\x00,i\x00\x00\x00\x00\x00\x01")
		total_length = 0
		with open(output, 'wb') as f:
			f.write(header)
			total_length += len(header)
			max_timestamp = 1.0
			for line in score:
				bundle = bytearray("\x00\x00\x00\x00#bundle\x00")
				timestamp = self.absToOSCTimestamp(line[0])
				max_timestamp = max(max_timestamp, (line[0] + 0.01))
				bundle.extend(timestamp)
# 				print line[1]
				bundle.extend("\x00\x00\x00\x00")
				commands = line[1]
				bundle.extend(self.padBytes(commands[0]))
				types = ","
				for item in commands[1:]:
					if type(item) == type('str'):
						types += 's'
					elif type(item) == type(1):
						types += 'i'
					elif type(item) == type(0.2):
						types += 'f'
				types = self.padBytes(types)
# 				print "BUNDLE: " + bundle
				bundle.extend(types)
				for item in commands[1:]:
						translated = self.padBytes(item)
						#print "        ", translated
						bundle.extend(translated)
# 				print "***LENGTH: ", len(bundle)
				total_length += len(bundle)
# 				for c in bundle: print("::: ", c, chr(c))
				bundle[3] = len(bundle) - 4
				bundle[23] = len(bundle) - 24
				f.write(bundle)
			footer = bytearray("\x00\x00\x00\x1c#bundle\x00")
			
			footer.extend(self.absToOSCTimestamp(max_timestamp))
			
			footer += "\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00,\x00\x00\x00"
			total_length += len(footer)
# 			print "footer:"
# 			for c in footer: print("::: ", c, chr(c))
			
			f.write(footer)
#			print "total_length: " + `total_length`

	def createNRTScore(self, sfpath = '/Users/kfl/76444.wav',
						sfid = 0,
						pBuf = 10,
						aBuf = 11,
						currBus = 10, # internally?
						tratio = 1.0, # arg?
						srate = 44100,
						duration = 1.0,
						oscDir = '/Users/kfl/score.osc',
						synthdef = 'monoSamplerNRT',
						efxSynthdefs = None,
						params = None):
		
		cwd = os.path.abspath(sfpath)
		fname = string.split(os.path.basename(sfpath), '.')
		cwd = os.path.dirname(cwd)
		
		#print 'CWD: ',  cwd
		os.chdir(cwd)
		## create a subdirectory 'md' if it doesn't already exist (ignore the error)
		try: 
			os.mkdir('md')
		except OSError:
			#print "Warning: md already exists"
			pass
	
		mdpath = cwd + '/md/' + fname[0] + '_' + `tratio` + '.md.' + fname[1]
	
		## the two alloc calls
		oscList = [[0.0, ["/b_allocReadChannel", pBuf, sfpath, 0, -1, '[0]']]]
		oscList += [[0.01, ["/b_alloc", aBuf, int(math.ceil((duration/0.04) / tratio)), 26]]]
		
		sdefs = [synthdef, 'power_centroid_mfcc24BusAnalyzerNRT']
		
		if efxSynthdefs is not None:
			for sdef in efxSynthdefs:
				sdefs.insert(-1, sdef)
		#print '===EFX:::'
		#print sdefs
		
		rows = [['srcbufNum', pBuf, 'outbus', 0, 'dur', duration, 'transp', tratio], ['inbus', 0, 'savebufNum', aBuf, 'transp', tratio]]
		
		if params is not None:
			# insert params into middle of rows!
			for prow in params:
				rows.insert(-1,prow)
		
		#print 'rows INITIALLY: ' + `rows`
		##for node in row:
		for r, row in enumerate(rows):
			#print 'enumerating row: ' + `row`
			#print 'row INITIALLY: ' + `row`
			for index, val in enumerate(row):
				##print 'enumerating val: ' + `val` + ' ' + `index`
				if val == 'srcbufNum':
					row[index+1] = pBuf
				elif val == 'savebufNum':
					row[index+1] = aBuf
# 				elif val == 'transp':
# 					row[index+1] = tratio
				elif val == 'outbus':
					row[index+1] = currBus
				elif val == 'inbus':
					row[index+1] = currBus
					currBus += 1
			#print 'row FINALLY: ' + `row`
			#print 'currBus currently: ' + `currBus`
			if r == 0:
				oscList += [[0.02, (["/s_new", sdefs[r], -1, 0, 0] + rows[r])]]
			else:
				oscList += [[0.02, (["/s_new", sdefs[r], -1, 1, 0] + rows[r])]]
		
		oscList += [[((duration / tratio) + 0.03), ["/b_write", aBuf, mdpath, "wav", "float32"]]]
		## don't free any buffers (yet)
		oscList += [[((duration / tratio) + 0.04), ["/c_set", 0, 0]]]
	
# 		print "\nTHE LIST:: " + `oscList` + "\n"
	
		self.processAndWriteFile(oscList, oscDir)
		
		os.chdir(self.lib['anchor']) # always return pwd to the anchor dir
	
