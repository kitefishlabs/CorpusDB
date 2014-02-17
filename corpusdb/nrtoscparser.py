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


import sc, time, struct, math, os, string
import numpy as np
from scosc import OSC
from scosc import tools
from scosc import osctools

class NRTOSCParser:
	"""
	anchor = corpus anchor (directory where corpus resides)
	"""
	def __init__(self, crps, num_features=24):
		self.corpus = crps
		self._analysis_synth = 'bus_analyzer_power_mfcc24_mn_nrt'
		self._analysis_features = num_features
	
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
		#print "score: ", score
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
				bundle.extend(types)
				#print 'bundle: ', bundle
				for item in commands[1:]:
						translated = self.padBytes(item)
						#print 'translated:: ', translated
						bundle.extend(translated)
				total_length += len(bundle)
				bundle[3] = len(bundle) - 4
				bundle[23] = len(bundle) - 24
				f.write(bundle)
			footer = bytearray("\x00\x00\x00\x1c#bundle\x00")
			
			footer.extend(self.absToOSCTimestamp(max_timestamp))
			
			footer += "\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00,\x00\x00\x00"
			total_length += len(footer)
			
			f.write(footer)
			f.close()
	
	
	def createNRTAnalysisScore(self, sfpath = '/Users/me/corpus/snd/76444.wav',
						pBuf = 10,
						aBuf = 11,
						tratio = 1.0,
						duration = 1.0,
						oscDir = '/Users/me/corpus/snd/score.osc',
						synthdef = 'monoSamplerNRT',
						efxSynthdefs = None,
						params = None):
		"""
		args:
			sfpath			-	full path to sound file that is being played/processed/analyzed
			pBuf			-	playback buffer id
			aBuf			-	analysis buffer id
			tratio			-	transposition
			duration 		-	make this longer for processed sounds with delay components
			oscDir			-	path to dir where SC .osc files are saved (.../corpus/osc/ by convention)
			synthdef		-	playback synthdef
			efxSynthdefs	-	list of processing synthdefs
			params			-	list of lists of processing synthdefs' parameters
		"""	
		
		# change to directory containing sound file and add an md dir if not already present
		cwd = os.path.abspath(sfpath)
		fname = string.split(os.path.basename(sfpath), '.')
		cwd = os.path.dirname(cwd)		
		os.chdir(cwd)
		## create a subdirectory 'md' if it doesn't already exist (ignore the error)
		try: 
			os.mkdir('md')
		except OSError:
			#print "Warning: md already exists"
			pass
		
		# full path to metadata (md) file
		mdpath = cwd + '/md/' + fname[0] + '_' + `tratio` + '.md.' + fname[1]
	
		## the two buffer alloc calls
		oscList = [[0.0, ["/b_allocReadChannel", pBuf, sfpath, 0, -1, '[0]']]]
		oscList += [[0.01, ["/b_alloc", aBuf, int(math.ceil((duration/0.04) / tratio)), self._analysis_features]]]
		
		# minimal list of 2 Synthdefs, playback --> analysis
		sdefs = [synthdef, self._analysis_synth]
		# insert effect/processing Synthdefs...
		if efxSynthdefs is not None:
			for sdef in efxSynthdefs:
				sdefs.insert(-1, sdef)
		# ... and their parameters
		rows = [['srcbufNum', pBuf, 'outbus', 0, 'dur', duration, 'transp', tratio], ['inbus', 0, 'savebufNum', aBuf, 'transp', tratio]]
		# params are parameters unique to efx synths
		if params is not None:
			# insert params into middle of rows!
			for prow in params:
				rows.insert(-1,prow)
		# rewrite the params in rows so that they have correct/logical values		
		currBus = 10
		for r, row in enumerate(rows):
			for index, val in enumerate(row):
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
			# now write the Synths
			if r == 0:
				oscList += [[0.02, (["/s_new", sdefs[r], -1, 0, 0] + rows[r])]]
			else:
				oscList += [[0.02, (["/s_new", sdefs[r], -1, 1, 0] + rows[r])]]
		
		# now write the buffer-write and end-point lines
		oscList += [[((duration / tratio) + 0.03), ["/b_write", aBuf, mdpath, "wav", "float32"]]]
		oscList += [[((duration / tratio) + 0.04), ["/c_set", 0, 0]]]
		
		# pass the osc list to function that writes binary .osc file
		self.processAndWriteFile(oscList, oscDir)
		# always return pwd to the anchor dir
		os.chdir(self.corpus.anchor)


	def createNRTAssemblyScore(self, 
						triosList,
						oscDir = '/Users/me/corpus/snd/score.osc'):
		"""
		args:
			triosList		-	np list of [sfid, onset, duration] trios
			oscDir			-	path to dir where SC .osc files are saved (.../corpus/osc/ by convention)
		"""	
		
		## the buffer alloc calls
		
		sfsToUse = np.unique(np.array(triosList[:,0], dtype='int32'))
		sfPaths = [self.corpus.sftree.nodes[sfid].sfpath for sfid in sfsToUse]
		# filter any duplicate (parent-->child) sound files before the alloc stage???!!!
		#oscList = [[0, ["/b_alloc", 0, np.sum(triosList[:,2]), 2]], [0.01, []]]
		oscList = []
		runningbuffertotal = 1
		
		# now build a dict with the synthdefs and params for each sfid
		sfInfo = dict()
		for i,sfid in enumerate(sfsToUse):
			try:
				node = self.corpus.sftree.nodes[sfid]
				sfInfo[sfid] = {
					'bufnum' : runningbuffertotal,
					'sfpath' : (self.corpus.anchor + '/snd/' + node.sfpath),
					'synthdef': [node.synth],
					'params' : None,
					'tratio' : node.tratio}
				oscList += [[0.0, ["/b_allocRead", runningbuffertotal, (self.corpus.anchor + '/snd/' + sfpth), 0, -1]] for sfpth in sfPaths]
				runningbuffertotal += 1
			
			# if the first .sfpath throws an Error, then we have a child node!
			except AttributeError:
				print "@@@TO DO!!! : handle child nodes!"
				pass
				# 				parentnode = self.corpus.sftree.nodes[ self.corpus.sftree.nodes[sfid].parent_id ]
				# 				childnode = self.corpus.sftree.nodes[ sfid ]
				# 				sfInfo[sfid] = dict(
				# 					'sfpath' : parentnode.sfpath,
				# 					'onset': triosList[i,1],
				# 					'dur': triosList[i,2],
				# 					'synthdefs' : [parentnode.synth, childnode.synth],
				# 					'params' : [None, childnode.params],
				# 					'tratio' : self.corpus.sftree.nodes[sfid].tratio)
		print sfInfo
		print oscList
		runningdur = 0
		for segment in triosList:
			sfid = segment[0]
			#print 'sfid: ', type(sfid)
			offset = segment[1]
			dur = segment[2]
			#print type(offset)
			#print type(dur)
			print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
			print sfInfo[sfid]['synthdef'][0]
			print int(sfid)
			print float(offset)
			print float(dur)
			print sfInfo[sfid]['tratio']
			print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
			oscList += [[(0.01+runningdur), ["/s_new", 
				sfInfo[sfid]['synthdef'][0], 
				-1, 
				0, 
				0, 
				'srcbufNum', 
				int(sfInfo[sfid]['bufnum']), 
				'outbus', 
				0, 
				'start', 
				float(offset), 
				'dur', 
				float(dur), 
				'transp', 
				sfInfo[sfid]['tratio']]]]
			runningdur += (dur - 0.01)
		
		oscList += [[(runningdur + 0.02), ["/c_set", 0, 0]]]

		print "======================"
		print oscList
				
		# pass the osc list to function that writes binary .osc file
		self.processAndWriteFile(oscList, oscDir)
		# always return pwd to the anchor dir
		os.chdir(self.corpus.anchor)


