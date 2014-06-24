#

"""
Part of corpusdb, corpus-based processing for SuperCollider + Python.

Overview
========

CorpusDB maintains a database of sound files, raw data, processed data, and segmented units that together comprise a structured approach to characterizing, storing, and retrieving sound data based on features of that data.

This system works with the following work flow:
# Load audio file.
# Analyze it.
# Using raw analysis data, segment the audio into units.
# Store units.
# [Repeat steps 1-4 for additional audio files]
# Export corpus to JSON file.
# Use metadata for matching, similarity, etc. algorithms. 

Metadata are mapped to units which represent segments of audio. Every sound file incorporated in a corpus is stored according to the Synthdefs that produce it. This way, a sound file and the chain of processing stages that modify said sound are represented. This is a simple form of data compression. Once analyzed, metadata produced by the analysis are stored in a table. An index links the metadata to the sound-recording-plus-processing recipe.

Analytical tasks and compositional processes are built on top of this structured representation of sounds. The user is free to use the data as he/she wishes.

This Python implementation uses SC-0.3.1, SuperCollider---the command line interface, plus the subprocess module to trigger non-real time analysis and synthesis. The parallel SC-native implementation (cbpsc) is better suited for real time use and is currently (2/2013) being rewritten to reflect changes made when developing the Python version. It is the developer's goal to maintain parallel, interoperable versions of this software.

TO DO:
* finish SC reimplementation/upgrade
* extend SFTree/nodes model
* implement synthesis nodes
* simplify workflows
* more wrapping of functionality into classes

"""

__version__ = '1.0'
__author__ = 'Thomas Stoll'
__copyright__ = "Copyright (C) 2012-14, Thomas Stoll, All Rights Reserved"
__license__ = "gpl 3.0 or higher"
__email__ = 'tms@kitefishlabs.com'


import os, sys, string, math, resource
import shlex, subprocess, jsonpickle, json
import numpy as np
import nrtoscparser, sftree
from corpusfeatures import *

class CorpusDB:
	"""
		
	"""
	def __init__(self, name, rate=44100, sudo_flag='False', verb=False):
		self.anchor = name
		self.rate = rate
		self.HOP_SECS = 0.04
		self.HOP_MS = self.HOP_SECS * 1000
		
		self.reset_corpus()
		self.parser = nrtoscparser.NRTOSCParser(self, self.alist.synthdef_string, self.num_raw_features)
		self.sound_file_units_mapped = False
		
		#if sudo_flag is True: resource.setrlimit(resource.RLIMIT_NOFILE, (16384, 16384)) #!!!
		os.chdir(self.anchor) # just in case we created this corpus using a link...
	
	def reset_corpus(self, verb=False):
		
		self.sftree = sftree.SFTree(self, self.anchor)
		self.cutable = dict()
		# data structures for raw data and corpus data
		self.rawtable	=	dict()
		self.rawmaps	= 	dict()
		self.powers		= 	dict()
		self.mfccs		= 	dict()
		self.chromas	= 	dict()
		# information about the corpus's current state
		self.sf_offset = 0
		self.cu_offset = 0
		self.alist = MFCC_Chromas(var_flag=True)
		# double-check size
		if self.alist.powers.indexes.numfeatures == 9:
			self.dtable = self.alist.powers.indexes
		self.num_raw_features = self.alist.powers.rawwidth + self.alist.rawwidth
		self.num_cooked_features = self.alist.powers.width + self.alist.width # after variance, stats, etc. are calculated
	
	def add_sound_file(self, filename=None, sfid=None, srcFileID=None, tratio=1.0, synthdef=None, params=None, procid=None, subdir=None, reuseFlag=None, importFlag=None, uflag=None, verb=False):
		"""
		Add a sound file to the corpus. Either a filename or an sfid must be provided.
		"""
		# check for duplicate entries having same sndfile and tratio ???

		if sfid is None:
			#NEED A MUCH BETTER ALGORITHM HERE! search for lowest unused sfid!
			sfid = self.sf_offset
			self.sf_offset = sfid + 1

		if srcFileID is None:
			
			root_node = self.sftree.add_root_node(filename, sfid, tratio, procid=procid, snd_subdir=subdir, uniqueFlag=uflag)
			if verb: print "add_root_node res: ", root_node.sfpath, ', ', root_node.sfid, ', ', root_node.tratio
			return root_node
			
			# if verb: print "import flag: ", importFlag, 
			if importFlag: self.import_sound_file_to_buffer(root_node.sfpath, sfid)
		
		else:
			if verb: print 'ADD CHILD: ', srcFileID, ' | ', sfid, ' | ', tratio, ' | ', synthdef, ' | ', params
			# sfid, tratio
			child_node = self.sftree.add_child_node(srcFileID, sfid, tratio, synthdef, params, procid=procid, uniqueFlag=uflag)
			if verb: print "add_child_node res: ", child_node.parent_id, ', ', child_node.sfid, ', ', child_node.tratio
			return child_node
	
	def remove_sound_file(self, sfid, verb=False):
		"""
	
		"""
		del self.sftree.nodes[sfid]
	
	def importSoundFileToBuffer(self, path, sfid, verb=False):
		"""
	
		"""
		return NotImplementedError
	
	def map_raw_sound_file(self, path, sfid, frames, verb=False):
		"""
		Replaces mapBySFRelID.
		"""
		self.rawtable[sfid] = (path, frames)
	
	def _activate_raw_metadata(self, sfid, verb=False):
		"""
		Returns memmap associated with this sfid, None if memmap cannot be found.
		"""
		try: 
			pair = self.rawtable[sfid]
		except KeyError(key):
			print "Error, this key (", key, ")does not have raw metadata associated with it.\nCannot activate."
			return None
		mdpath = pair[0]
		if verb: print 'mdpath: ', mdpath
		num_frames = pair[1]
		try:
			rawmaps = self.rawmaps[sfid].T
			if verb: print "RAW MAPS SHAPE: ", rawmaps.shape
			power_vector 		= rawmaps[0]
			mfccs_vector 		= rawmaps[1     : 1+13].T
			chroma_vector 		= rawmaps[1+13	: 1+13+12].T
		except KeyError:
			#print "key errors are good..."
			self.rawmaps[sfid] = rawmaps = np.memmap(mdpath, dtype=np.float32, mode='r', offset=280, shape=(num_frames, self.num_raw_features))
			if verb: print "RAW MAPS SHAPE: ", self.rawmaps[sfid].shape
			power_vector 		= rawmaps.T[0]
			mfccs_vector 		= rawmaps.T[1       : 1+13].T
			chroma_vector 		= rawmaps.T[1+13	: 1+13+12].T
		
		self.powers[sfid]		=	power_vector
		self.mfccs[sfid]		=	mfccs_vector
		self.chromas[sfid]		=	chroma_vector
				
		return self.powers[sfid], self.mfccs[sfid], self.chromas[sfid]
    
	def _deactivate_raw_sound_file(self, sfid, verb=False):
		"""
		Free all raw metadata associated with the given sf id.
		"""
		try:
			del self.rawmaps[sfid]
			del self.powers[sfid]
			del self.mfccs[sfid]
			del self.chromas[sfid]
		
		except KeyError:
			print "Attempt to deactivate memmap or other metadata for key ", sfid, " has failed."
			return None
		return sfid
	
	def analyze_sound_file(self, filename, sfid, tratio=1.0, subdir='', outwav=False, verb=False):
		"""
			Read NRT OSC score file, perform analysis asynchronously via shell, wait, signal completion and clean up.
		
			This function intelligently synthesizes the synthid, efx_synths, efxparams, and fullpath based on the input.
			
			Subdir arg is an empty string ('') if not used.
		"""
		if verb: print 'file name: ', filename
		self.parser.anchor = self.anchor

		#print sfid, ' '	, tratio, ' ', self.rate, ' ', self.sftree.nodes[sfid].duration, ' ', oscpath
		if subdir is None:
			subdir = ''
		try:
			synthid = self.sftree.nodes[sfid].parent_id
			efx_synth = self.sftree.sfmap[sfid][0]
			efx_params = self.sftree.sfmap[sfid][1]
			fullpath = os.path.join(self.anchor, 'snd', subdir, self.sftree.nodes[synthid].sfpath)
		except AttributeError:
			synthid = sfid
			efx_synth = None
			efx_params = None
			fullpath = os.path.join(self.anchor, 'snd', subdir, self.sftree.nodes[sfid].sfpath)

		if verb: print 'fullpath: ', fullpath, '\n synthid: ', synthid, '\n', self.sftree.sfmap[sfid][0], '\n', self.sftree.sfmap[sfid][1]
		
		oscpath = os.path.join(self.anchor, 'osc', (os.path.splitext(os.path.basename(fullpath))[0] + '_' + `tratio` + '_' + self.alist.synthdef_string + '.osc'))
		if verb: print 'create nrt score args: ', fullpath, ' ', oscpath
		
		self.parser.createNRTAnalysisScore(fullpath, 
									tratio=tratio, 
									duration=self.sftree.nodes[sfid].duration, 
									oscDir=oscpath, 
									synthdef=self.sftree.nodes[synthid].synth, 
									efxSynthdefs=efx_synth, 
									params=efx_params)

		if outwav:
			wavfile = ('/Users/kfl/Music/CorpusDB/rawsfids/' + str(sfid) + '.wav')
		else:
			wavfile = ' _ '
		
		cmd = 'scsynth -N ' + oscpath + ' ' + fullpath + wavfile + ' 44100 WAV int16 -o 1'
		if verb: print cmd
		
		args = shlex.split(cmd)
		sppo = subprocess.Popen(args, stdout=None, stderr=None, shell=False, close_fds=True, preexec_fn=resource.setrlimit(resource.RLIMIT_NOFILE, (10000,10000)))
		if verb: print "sppo:: ", sppo
		
		rc = sppo.wait()
		if verb: print 'RC: ', rc
		if rc == 1:
			cwd = os.path.abspath(fullpath)
			fname = string.split(os.path.basename(fullpath), '.')
			cwd = os.path.dirname(cwd)
			mdpath = cwd + "/md/" + fname[0] + '_' + `tratio` + '.md.' + fname[1]
			if verb: print 'MDPATH for mapping: ', mdpath
			num_frames = int(math.ceil(self.sftree.nodes[sfid].duration / self.HOP_SECS / tratio))
			if verb: print 'num frames: ', num_frames
			# map it:
			self.map_raw_sound_file(mdpath, sfid, num_frames)
			## sftrees/sfmap: handled in add_sound_file()!
			## what to do if returncode != 1 ???
		else:
			print 'Analysis was not successful; failed to map raw sound file!!!'
	
	def add_sound_file_unit(self, sfid, onset=0, dur=0, tag=0, verb=False):
		"""
		Add a sound file unit to the proper sftree node.
		Always unsets the mapped flag.
		"""
		if verb: print 'SFID: ', sfid, ' | onset: ', onset, ' | dur: ', dur
		try:
			res = self.sftree.nodes[sfid].add_onset_and_dur_pair(onset, dur)
			if verb: print '$$$$$$$$$$$$$ TAG: ', tag
			self.sftree.nodes[sfid].update_unit_segment_params(len(self.sftree.nodes[sfid].unit_segments)-1, tag=tag)
		except KeyError:
			print 'Error: there is no Node for ', sfid, ' in the sf tree. Add SFU failed'
			return None
		self.sound_file_units_mapped = False
		return sfid
	
	def _get_snd_path(self, fname, verb=False):
		return (self.anchor + '/snd/' + fname)
	
	def update_sound_file_unit(self, sfid, relid=None, onset=None, dur=None, tag=None, verb=False):
		"""
		Change the relid, bounds or...
		"""
		if relid is not None:
			try:
				self.sftree.nodes[sfid].update_unit_segment_params(relid, onset, dur, tag)
				return sfid, relid
			except KeyError:
				print 'Error: there is no entry for ', sfid, ' in the sf map. Update SFU failed.'
				return None
			except IndexError:
				print 'Error: ', relid, ' is a bad relid for sfid ', sfid, '.'
				return None
	
	def remove_sound_file_unit(self, sfid, path=None, relid=None, bounds=None, verb=False):
		"""
		Remove all internal mappings for a given sfid/path.
		"""
		if self.sftree.nodes[sfid].unit_segments[relid] is not None:
			del self.sftree.nodes[sfid].unit_segments[relid]		
	
	def clear_sound_file_units(self, sfid, verb=False):
		"""
		Remove all references to all sound file units.
		"""		
		try:
			self.sftree.nodes[sfid].unit_segments = []
		except KeyError:
			'Error: there is no entry for ', sfid, ' in the sf map. Update SFU failed.'
			return None
		return sfid
		
	def get_raw_metadata(self, sfid, verb=False):
		"""
		Return scalars, vectors, activation layer, and cooked layer in that order. Calls _activate_raw_metadata, if necessary.
		Note that this function is only going to work when there is raw analyzed metadata. To get the segmentsed
		"""
		try:
			return self.powers[sfid], self.mfccs[sfid], self.chromas[sfid]
			####$ ***
		except KeyError:
			return self._activate_raw_metadata(sfid) # now self.rawmaps[sfid] should exist or res == None if not
	
	def get_sorted_units_list(self, sfid, verb=False):
		"""
		
		"""
		return self.sftree.nodes[sfid].sort_segments_list()
	
	####$
	####$ -- redo whole function!
	def segment_units(self, sfid, verb=False):
		"""
		This function takes the list of unit breakpoints, plus the raw metadata, and assembles 'cooked' segments in the corpus segtable.
		
		Note: currently ignores the amplitude scalars (aside from generating stats)...
		
		"""
		segmented = self.get_sorted_units_list(sfid)
		raw_amps, raw_mfccs, raw_chromas = self.get_raw_metadata(sfid)
		amps, reheated = [], []
		
		if verb: print 'raw: ', raw_amps
		amps_stripped = np.nan_to_num(raw_amps)
		if verb: print 'amps_stripped: ', amps_stripped
		mfccs_stripped = np.nan_to_num(raw_mfccs)
		chromas_stripped = np.nan_to_num(raw_chromas)
		
		for relid, sfu in enumerate(segmented):

			offset = int(math.floor(sfu.onset / self.HOP_SECS))
			dur = int(math.floor(sfu.dur / self.HOP_SECS))
			if verb: print '[[', offset, '|', dur, ']]'
			self.sftree.nodes[sfid].add_metadata_for_relid(relid, powers=self.alist.powers.proc_funcs[0](amps_stripped, offset, dur))
			#reheated += [np.mean(mfccs_stripped[offset:(offset+dur)], axis=0, dtype=np.float32)]
			self.sftree.nodes[sfid].add_metadata_for_relid(relid, mfccs=self.alist.proc_funcs[0](mfccs_stripped[offset:(offset+dur)]))
			self.sftree.nodes[sfid].add_metadata_for_relid(relid, mfcc_vars=self.alist.proc_funcs[1](mfccs_stripped[offset:(offset+dur)]))
			self.sftree.nodes[sfid].add_metadata_for_relid(relid, chromas=self.alist.proc_funcs[1](chromas_stripped[offset:(offset+dur)]))
	
	def add_corpus_unit(self, uid, metadata, verb=False):
		"""
		test me
		"""
		# some basic metadata checks? check for key collisions?
		self.cutable[uid] = metadata

	def remove_corpus_unit(self, cid, verb=False):
		"""
		test me
		Remove a units from the corpus units table.	
		"""
		try:
			del self.cutable[cid]
		except KeyError:
			print 'Error: attempting to remove corpus unit that does not exist at index ', cid, '.'
	
	def clear_corpus_units(self, verb=False):
		"""
		test me
		Remove all units from the corpus units table.
		"""
		self.cu_offset = 0
		# for k, unit in enumerate(self.cutable):
		#	self.cutable[k] = None
		self.cutable = dict()
	
	def get_sound_file_unit_metadata(self, sfid, verb=False):
		"""
		test me
		Get the metadata rows for all units associated with a sound file.
		"""
		return sorted([entry for entry in self.cutable if entry[2] == sfid], key = lambda row: row[0])
	
	def map_sound_file_units_to_corpus_units(self, verb=False):
		"""
		Build the corpus unit table from entries found in the sound file unit table.
		"""
		print "map sound file units to corpus units"
		self.clear_corpus_units()
		if verb: print '---------------------------------'
		if verb: print self.sftree.nodes.keys()
		for node in self.sftree.nodes.keys():
			sf_id = self.sftree.nodes[node].sfid
			sf_tratio = self.sftree.nodes[node].tratio
			sf_proc_id = [k for k,v in self.sftree.procmap.iteritems() if v == self.sftree.nodes[node].hashstring][0]
			try:
				parent_id = self.sftree.nodes[node].parent_id
			except AttributeError:
				parent_id = sf_id
			sf_unit_segments = self.sftree.nodes[node].unit_segments
			relid = 0
			
			try:
				for k in self.sftree.nodes[node].unit_powers.keys():
					amp_segment = self.sftree.nodes[node].unit_powers[k]
					mfccs_segment = self.sftree.nodes[node].unit_mfccs[k]
					mfccs_vars_segment = self.sftree.nodes[node].unit_mfcc_vars[k]
					chromas_segment = self.sftree.nodes[node].unit_chromas[k]
					index = self.cu_offset
					
					if verb: print '@ relid/onset: ', relid, '| ', sf_unit_segments[relid].onset
					row = np.array([index, parent_id, sf_id, relid, sf_proc_id, sf_unit_segments[relid].tag, sf_unit_segments[relid].onset, sf_unit_segments[relid].dur, sf_tratio])
					if verb: print 'row: ', row.shape
					if verb: print 'amp segment: ', amp_segment
					if verb: print 'mfccs segment: ', mfccs_segment
					if verb: print 'mfcc vars segment: ', mfcc_vars_segment
					if verb: print 'chromas segment: ', chromas_segment
					
					# if verb: print 'mfccs vars segment: ', mfccs_vars_segment
					self.add_corpus_unit(index, np.concatenate([row, amp_segment, mfccs_segment, mfccs_vars_segment, chromas_segment]))
					# self.add_corpus_unit(index, np.concatenate([row, amp_segment, mfccs_segment, mfccs_vars_segment]))
					relid += 1
					self.cu_offset += 1
			except KeyError:
				print 'KeyError on segments traversal, trying to continue'
				pass
			except:
				print "Unexpected error:", sys.exc_info()[0]
				raise

	# types: 0 = all, 1 = SamplerNodes, 2 = EfxNodes
	def convert_sftree_nodes_to_array(self, type=0, verb=False):
		keys = sorted(list(self.sftree.nodes.keys()))
		nodes = []	
		for k in keys:
			if ((type == 1) and (hasattr(self.sftree.nodes[k], 'sfpath'))):
				nodes += [self.sftree.nodes[k]]
			elif ((type == 2) and (hasattr(self.sftree.nodes[k], 'parent_id'))):
				nodes += [self.sftree.nodes[k]]
			else:
				nodes += [self.sftree.nodes[k]]
		return nodes

	####*****
	#
	# CORPUS RAW ARRAY ACCESS
	#
	
	#	 index (9)           amp (5)         mfccs (24)           mfccs_vars (24)
	#	[0 1 2 3 4 5 6 7 8] [9 10 11 12 13] [14 15 16 17 ... 37] [38 39 40 41 ... 61]
	#
	
	def convert_corpus_to_array(self, type='all', map_flag=False, verb=False):
		"""
		Convert the corpus unit table to a three compacted arrays: power metadata and MFCC metadata.
		"""
		if map_flag: self.map_sound_file_units_to_corpus_units()
		num_descriptors = len(self.cutable[0]) # hard code it?

		try:
			X = self.X
		except AttributeError:
			xlist = []
			for key in sorted(list(self.cutable.keys())):
				xlist.append([self.cutable[key]])
			X = np.array(xlist, dtype='float32')
			X = np.reshape(X, (-1, num_descriptors))
		
		print type
		if type is 'I':			return np.c_[X[:,0], X[:,1:9]]
		elif type is 'p6': 		return np.c_[X[:,0], X[:,9:15]]
		elif type is 'm13':		return np.c_[X[:,0], X[:,15:28]]
		elif type is 'm13var':	return np.c_[X[:,0], X[:,15:41]]
		elif type is 'm24':		return np.c_[X[:,0], X[:,15:39]]
		elif type is 'm24var':	return np.c_[X[:,0], X[:,15:63]]
		elif type is 'c12':		return np.c_[X[:,0], X[:,-12:]] # either 29:, 40:, 42: or 64:
		elif type is 'c12var':	return np.c_[X[:,0], X[:,-24:]] # either 29:, 40:, 42: or 64:
		elif type is 'all':		return np.c_[X[:,0], X]
		else:
			raise ArgumentError
	
	def convert_corpus_to_tagged_array(self, type='all', tag=0.0, map_flag=False, verb=False):
		"""
		Convert the corpus unit table to a three compacted arrays: power metadata and MFCC metadata.
		"""

		# get the info segments and filter those that are tagged
		info = self.convert_corpus_to_array('I', map_flag)
		
		print info.shape
		
		indices = np.argwhere(info[:,5]==tag)
# 		indices = np.reshape(indices, (indices.shape[0],))

		# use the tagged indices to pull out the tagged entries
		filtered_by_type = self.convert_corpus_to_array(type)
		filtered_by_tag = filtered_by_type[indices]
		filtered_by_tag = np.reshape(filtered_by_tag, (indices.shape[0], filtered_by_type.shape[1]))

		# add indices as a column (on the left)
# 		return np.append(indices, filtered_by_tag, axis=1)
		return filtered_by_tag
	
	def cuids_for_sfid(self, seed_sfid, verb=False):
		return [int(self.cutable[entry][0]) for entry in self.cutable.keys() if self.cutable[entry][2] == seed_sfid]
			
	def import_corpus_from_json(self, jsonfilename, appendflag=False, newanchor=None, importflag=False, verb=False):
		"""
		Create a corpus from a json file.
		Append flag??? Should it be removed as a parameter.
		"""
		if appendflag is False:
 			print 'appendflag is FALSE'
			print 'sf_offset: ', self.sf_offset
			self.reset_corpus()
		else:
			print 'appendflag is TRUE'
			print 'sf_offset: ', self.sf_offset
			
		#set up
		jsonpath = os.path.join(self.anchor, 'json', jsonfilename)
		f = open(jsonpath, 'r')
		
		j = jsonpickle.decode(f.read())
		
		print j.keys()
		
		if newanchor is not None:
			self.anchor = newanchor
		# warn user if conflicting anchor path?
		
		current_procmap_offset = self.sftree.procmap_offset
		if verb: print "current_procmap_offset: ", current_procmap_offset
		
		procmap = j['procmap']
		for key in sorted(procmap.keys()):
			procid = self.sftree.check_procmap((int(key)+current_procmap_offset), str(procmap[key]))

		soundfiles = j['soundfiletree']
		for key in sorted([int(x) for x in soundfiles.keys()]):
			sf = soundfiles[str(key)]
			
			procid = [int(k) for k,v in procmap.iteritems() if v == sf['hash']][0]
			if verb: print "k procid result: ", procid
			# print sf
			
			try:
				pid = sf['parentID']
				# print ">>> params: ", sf['params']
				params = [[str(p) if (type(p) == type(u'')) else p for p in sf['params']]]
				# print ">>> params: ", params
				
				sfid = self.add_sound_file(filename=None, 
												sfid=(sf['sfID'] + self.sf_offset),
												srcFileID=(pid + self.sf_offset),
												tratio=sf['tRatio'],
												synthdef=str(sf['synth'][0]),
												params=params,
												procid=procid,
												uflag=sf['uniqueID'])
			except KeyError:
				sfid = self.add_sound_file(filename=str(sf['relpath']), 
											sfid=sf['sfID'] + self.sf_offset, 
											srcFileID=None, 
											tratio=sf['tRatio'],
											procid=procid, 
											uflag=sf['uniqueID'])
						
		corpusunits = j['corpusunits']
		
		if type(corpusunits) == type([]):
			print corpusunits[0]
			print corpusunits[1]
			print corpusunits[2]
			fp = np.memmap(os.path.join(self.anchor, 'json', str(corpusunits[0])), dtype=np.float32, shape=(int(corpusunits[1]),int(corpusunits[2])))
			self.X = fp
			del fp
 			for key in np.array(self.X[:,0], dtype=int).tolist():
 				if verb: print '-----------------------'
				if verb: print type(key)
				if verb: print corpusunits[str(key)]
				cunit = np.array(self.X[key]).tolist()
				if verb: print "cunit: ", cunit
				cunit[0] += self.cu_offset
				if verb: print "cunit[0]: ", cunit[0]
				cunit[1] += current_procmap_offset
				if verb: print "cunit[1]: ", cunit[1]
				cunit[2] += self.sf_offset
				if verb: print "cunit[2]: ", cunit[2]
				self.add_corpus_unit(int(key) + self.cu_offset, cunit)

		else:
			# its a dictionary of cuid->metadata mappings
			# print "proc map offset: ", self.sftree.procmap_offset
			for key in sorted([int(x) for x in list(corpusunits.keys())] ):
				if verb: print '-----------------------'
				if verb: print type(key)
				if verb: print corpusunits[str(key)]
				cunit = corpusunits[str(key)]
				try:
					cunit = [float(x) for x in cunit.strip('[]').split(',')]
				except AttributeError:
					cunit = corpusunits[str(key)]
				if verb: print "cunit: ", cunit
				cunit[0] += self.cu_offset
				if verb: print "cunit[0]: ", cunit[0]
				cunit[1] += current_procmap_offset
				if verb: print "cunit[1]: ", cunit[1]
				cunit[2] += self.sf_offset
				if verb: print "cunit[2]: ", cunit[2]
				self.add_corpus_unit(int(key) + self.cu_offset, cunit)
		
		self.sf_offset = max(self.sftree.nodes.keys()) + 1
		if verb: print 'UPDATE max sfid --> sf_offset: ', self.sf_offset
		self.cu_offset = max(self.cutable.keys()) + 1
		if verb: print 'UPDATE max cutable key --> cu_offset: ', self.cu_offset
		self.sftree.procmap_offset = max(self.sftree.procmap.keys()) + 1

		f.close()
		
	
	def export_corpus_to_json(self, jsonfilename, memmapfilename, verb=False):
		"""
		
		"""
		jsonpath = os.path.join(self.anchor, 'json', jsonfilename)	
		if memmapfilename is not None:
			memmappath = os.path.join(self.anchor, 'json', memmapfilename)
		else:
			memmappath = None
		f = open(jsonpath, 'w')
		# don't forget the descriptors...
		if verb: print ''
		if verb: print self.sftree.procmap
		if verb: print ''
		toplevel = { 'descriptors': self.dtable, 'anchorpath': self.anchor, 'procmap': self.sftree.procmap }
		sf = dict()
		for sfid in self.sftree.nodes.keys():
			sf[sfid] = self.sftree.nodes[sfid].render_json()
		toplevel['soundfiletree'] = sf
		# roll the cutable rows into dictionary
		d = dict()
		if verb: print 'keys: ', self.cutable.keys()
		
		if memmappath is None:
			for cid in sorted(list(self.cutable.keys())):
				if verb: print 'cutable entry: ', type(self.cutable[cid])
				d[str(cid)] = json.dumps(self.cutable[cid].tolist())
			toplevel['corpusunits'] = d
		else:
			converted = self.convert_corpus_to_array('all')
			print "converted shape: ", converted.shape
			fp = np.memmap(memmappath, dtype=np.float32, mode='w+', shape=converted.shape)
			fp[:] = converted
			fp.flush()
			del fp
			toplevel['corpusunits'] = [memmapfilename, converted.shape[0], converted.shape[1]]
			print toplevel['corpusunits']
			

		print toplevel.keys()
		f.write(jsonpickle.encode(toplevel))	
		f.close()
