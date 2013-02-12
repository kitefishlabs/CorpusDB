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


import os, sys, string, math, resource
import shlex, subprocess, jsonpickle, json
import numpy as np
import nrtoscparser, sftree

class CorpusDB:
	"""
		
	"""
	def __init__(self, name, sudo_flag='False'):
		self.anchor = name
		self.rate = 44100
		self.HOP_SECS = 0.04
		self.HOP_MS = self.HOP_SECS * 1000
		
		self.reset_corpus()
				
		self.parser = NRTOSCParser2.NRTOSCParser2()
			
		self.sound_file_units_mapped = False
		
		if sudo_flag is True: resource.setrlimit(resource.RLIMIT_NOFILE, (16384, 16384)) #!!!
		os.chdir(self.anchor) # just in case we created this corpus using a link...
	
	def reset_corpus(self):
	
		self.sftree = CorpusSoundFileTree(self, self.anchor)
# 		self.segtable = dict() # segtable's role is now part of the sftree nodes!
		self.cutable = dict()
		# data structures for raw data and corpus data
		self.rawtable = dict()
		self.rawmaps = dict()
		self.powers = dict()
		self.mfccs = dict()
		self.activation_layers = dict()
		self.cooked_layers = dict()
		# corpus-level mappings and helper data structures
		self.sfmap = dict()
		self.sfgmap = dict()
		self.tagmap = dict()
		self.transformations = dict({0: 'thru', 'thru': 0})
		self.synthdefs = dict()
		# information about the corpus's current state
		self.sf_offset = 0
		self.cu_offset = 0
		self.sfg_set = set() # to-do: make this work: the set has to be valid after every change to cutable & segtable
		self.dtable = dict({0: 'unitID', 1: 'sfRelID', 2: 'sfileID', 3: 'sfGrpID',
			4: 'onset', 5: 'duration', 6: 'tRatio', 7: 'uTag'})
	
	def add_sound_file(self, filename=None, sfid=None, srcFileID=None, tratio=1.0, sfGrpID=0, synthdef=None, params=None, subdir=None, reuseFlag=None, importFlag=None, uflag=None):
		"""
		Add a sound file to the corpus. Either a filename or an sfid must be provided.
		"""
		# check for duplicate entries having same sndfile and tratio ???
		#print 'srcfile?: ', srcFileID
		#print 'path?: ', filename
		#print 'sfid?: ', sfid

		if sfid is None:
			#NEED A MUCH BETTER ALGORITHM HERE! search for lowest unused sfid!
			sfid = self.sf_offset
			self.sf_offset = sfid + 1

		if srcFileID is None:

			#pth, grp, tratio
			root_node = self.sftree.add_root_node(filename, sfid, tratio, sfGrpID, snd_subdir=subdir, uniqueFlag=uflag)
			print "add_root_node res: ", root_node.sfpath, ', ', root_node.sfid, ', ', root_node.group, ', ', root_node.tratio
			
# 			print "reuse flag: ", reuseFlag
# 			if reuseFlag:
# 				fname = string.split(os.path.basename( os.path.abspath(root_node.sfpath) ), '.')
# 				cwd = os.path.dirname( os.path.abspath(root_node.sfpath) )
# 				mdpath = cwd + "/md/" + fname[0] + '_' + `root_node.tratio` + '.md.' + fname[1]
# 				print 'MDPATH for REUSE: ', mdpath
# 				num_frames = math.ceil(self.sftree.nodes[sfid].duration / self.HOP_SECS / root_node.tratio)
# 				#print 'num_frames for REUSE: ', num_frames
# 				self.map_raw_sound_file(mdpath, sfid, num_frames)
			return root_node
			
			# print "import flag: ", importFlag, 
			if importFlag: self.import_sound_file_to_buffer(root_node.sfpath, sfid)
		
		else:
			#print 'ADD CHILD: ', srcFileID, ' | ', sfid, ' | ', tratio, ' | ', sfGrpID, ' | ', synthdef, ' | ', params
			# sfid, grp, tratio
			child_node = self.sftree.add_child_node(srcFileID, sfid, tratio, sfGrpID, synthdef, params, uniqueFlag=uflag)
			print "add_child_node res: ", child_node.parent_id, ', ', child_node.sfid, ', ', child_node.group, ', ', child_node.tratio
			return child_node
		

	def remove_sound_file(self, path):
		"""
	
		"""
		pass
	
	def importSoundFileToBuffer(self, path, sfid):
		"""
	
		"""
		pass
	
	def map_raw_sound_file(self, path, sfid, frames):
		"""
		Replaces mapBySFRelID.
		"""
		self.rawtable[sfid] = (path, frames)
	
	def _activate_raw_metadata(self, sfid):
		"""
		Returns memmap associated with this sfid, None if memmap cannot be found.
		"""
		try: 
			pair = self.rawtable[sfid]
		except KeyError(key):
			print "Error, this key (", key, ")does not have raw metadata associated with it.\nCannot activate."
			return None
		mdpath = pair[0]
		print 'mdpath: ', mdpath
		num_frames = pair[1]
		try:
			power_vector = self.rawmaps[sfid].T[0]
			mfccs_vector = self.rawmaps[sfid].T[2:].T
		except KeyError:
			#print "key errors are good..."
			self.rawmaps[sfid] = np.memmap(mdpath, dtype=np.float32, mode='r', offset=280, shape=(num_frames, 26))
			power_vector = self.rawmaps[sfid].T[0]
			mfccs_vector = self.rawmaps[sfid].T[2:].T
		
		interm = np.ma.masked_outside(mfccs_vector, 0.0, 1.0)
		interm = np.ma.masked_invalid(interm)
		interm = interm.filled(interm.mean())
		
		self.activation_layers[sfid] = [1.0 for x in range(interm.shape[0])] # num rows in memmap
		
		self.cooked_layers[sfid] = [row for i, row in enumerate(interm) if self.activation_layers[sfid][i] > 0.5]
		
		self.powers[sfid] = power_vector
		self.mfccs[sfid] = mfccs_vector
		
		del interm
		
		return self.powers[sfid], self.mfccs[sfid], self.activation_layers[sfid], self.cooked_layers[sfid]
    
	def _deactivate_raw_sound_file(self, sfid):
		"""
		
		"""
		try:
			del self.rawmaps[sfid]
		except KeyError:
			print "Attempt to deactivate memmap for key ", sfid, " has failed."
			return None
		return sfid
		
	def analyze_sound_file(self, filename, sfid, group=0, tratio=1.0, subdir=None):
		"""
		Read NRT OSC score file, perform analysis asynchronously via shell, wait, signal completion and clean up.
		"""
		print 'file name: ', filename
		self.parser.anchor = self.anchor

		if subdir:
			fullpath = os.path.join(self.anchor, 'snd', subdir, filename)
		else:
			fullpath = os.path.join(self.anchor, 'snd', filename)

		# fullpath = os.path.join(self.anchor, 'snd', filename)
		oscpath = os.path.join(self.anchor, 'osc', (os.path.splitext(filename)[0] + '_' + `tratio` + '_power_mfcc24Analyzer.osc'))
		#print 'create nrt score args: ', fullpath, ' ', oscpath
		#print sfid, ' '	, tratio, ' ', self.rate, ' ', self.sftree.nodes[sfid].duration, ' ', oscpath
		
		try:
			synthid = self.sftree.nodes[sfid].parent_id
# 			print "=== ", synthid
			efx_synth = self.sftree.trackbacks[sfid][0]
			efx_params = self.sftree.trackbacks[sfid][1]
		except AttributeError:
			synthid = sfid
			efx_synth = None
			efx_params = None
		# print "### ", synthid, '\n', self.sftree.trackbacks[sfid][0], '\n', self.sftree.trackbacks[sfid][1]
		self.parser.createNRTScore(fullpath, 
									sfid=sfid, 
									tratio=tratio, 
									srate=self.rate, 
									duration=self.sftree.nodes[sfid].duration, 
									oscDir=oscpath, 
									synthdef=self.sftree.nodes[synthid].synth, 
									efxSynthdefs=efx_synth, 
									params=efx_params)

		cmd = 'scsynth -N ' + oscpath + ' _ _ 44100 WAVE float32 -o 1'
		args = shlex.split(cmd)
		p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, close_fds=True)
		
		print 'PID: ', p.pid
		rc = p.wait()
				
		print 'RC: ', rc
		if rc == 1:
			cwd = os.path.abspath(fullpath)
			fname = string.split(os.path.basename(fullpath), '.')
			cwd = os.path.dirname(cwd)
			mdpath = cwd + "/md/" + fname[0] + '_' + `tratio` + '.md.' + fname[1]
			#print 'MDPATH for mapping: ', mdpath
			num_frames = int(math.ceil(self.sftree.nodes[sfid].duration / self.HOP_SECS / tratio))
			#print 'num frames: ', num_frames
			# map it:
			self.map_raw_sound_file(mdpath, sfid, num_frames)
			## sftrees/trackbacks: handled in add_sound_file()!
			## what to do if returncode != 1 ???
		else:
			print 'Analysis was not successful; failed to map raw sound file!!!'
	
	
	def map_id_to_sf(self, path, sfid=None, sfgroup=0):
		"""
		Map an integer index to a sound file path. Also adds mapping from the group id ->.
		"""
		if sfid is not None:
			id = sfid
		else:
			self.sf_offset += 1
			id = self.sf_offset
		#print "sfgmap val: ", self.sfgmap[sfgroup]
		try:
			#self.sfgmap[sfgroup]
			self.sfgmap[sfgroup].add(id)
		except KeyError:
			self.sfgmap[sfgroup] = set([id])
		try: # (self.sfmap[sfid] is not None) and (self.sfmap[path] is not None):
			self.sfmap[sfid] = path
			self.sfmap[path] = sfid
		except KeyError:
			print 'This sfid <-> path mapping has already been made.'
			return None
	
	
	def add_sound_file_unit(self, sfid, path=None, onset=0, dur=0, tag=0):
		"""
		In add_sound_file_unit, sfg arg is not used...
		"""
		if sfid is None and path is not None:
			sfid = self._lookup_sfid(self._get_snd_path(path))
		print 'SFID: ', sfid, ' | onset: ', onset, ' | dur: ', dur
		try:
			res = self.sftree.nodes[sfid].add_onset_and_dur_pair(onset, dur)
			print '$$$$$$$$$$$$$ TAG: ', tag
			self.sftree.nodes[sfid].update_unit_segment_params(len(self.sftree.nodes[sfid].unit_segments)-1, tag=tag)
		except KeyError:
			print 'Error: there is no Node for ', sfid, ' in the sf tree. Add SFU failed'
			return None
		self.sound_file_units_mapped = False
		return sfid
	
	def _get_snd_path(self, fname):
		return (self.anchor + '/snd/' + fname)
	
	def update_sound_file_unit(self, sfid, path=None, relid=None, onset=None, dur=None, tag=None):
		"""
		Change the relid, bounds, or group.
		"""
		if sfid is None and path is not None:
			sfid = self._lookup_sfid(self._get_snd_path(path)	)
		if relid is not None:
			try:
				self.sftree.nodes[sfid].update_unit_segment_params(relid, onset, dur, tag)
				return sfid, relid
			except KeyError:
				'Error: there is no entry for ', sfid, ' in the sf map. Update SFU failed.'
				return None
			except IndexError:
				'Error: ', relid, ' is a bad relid for sfid ', sfid, '.'
				return None
	
	def remove_sound_file_unit(self, sfid, path=None, relid=None, bounds=None):
		"""
		Remove all internal mappings for a given sfid/path.
		"""
		if self.sftree.nodes[sfid].unit_segments[relid] is not None:
			del self.sftree.nodes[sfid].unit_segments[relid]		
	
	def clear_sound_file_units(self, sfid, path=None):
		"""
		Remove all references to all sound file units.
		"""
		
		if sfid is None and path is not None:
			sfid = self._lookup_sfid(path)
		try:
			self.sftree.nodes[sfid].unit_segments = []
			#self.segtable[sfid]['umd'] = []
		except KeyError:
			'Error: there is no entry for ', sfid, ' in the sf map. Update SFU failed.'
			return None
		return sfid
		
	def get_raw_metadata(self, sfid):
		"""
		Return scalars, vectors, activation layer, and cooked layer in that order. Calls _activate_raw_metadata, if necessary.
		Note that this function is only going to work when there is raw analyzed metadata. To get the segmentsed
		"""
		try:
			return self.powers[sfid], self.mfccs[sfid], self.activation_layers[sfid], self.cooked_layers[sfid]
		except KeyError:
			return self._activate_raw_metadata(sfid) # now self.rawmaps[sfid] should exist or res == None if not
	
	def get_sorted_units_list(self, sfid):
		"""
		
		"""
		return self.sftree.nodes[sfid].sort_segments_list()
	
	def segment_units(self, sfid):
		"""
		With all due respect to Mr. Levi-Strauss...
		
		This function takes the list of unit breakpoints, plus the raw metadata, and assembles 'cooked' segments in the corpus segtable.
		
		Note: currently ignores the amplitude scalars...
		
		"""
		segmented = self.get_sorted_units_list(sfid)
		raw_amps, raw_mfccs, activation, cooked = self._activate_raw_metadata(sfid)
		amps , reheated = [], [], []
		
# 		print 'raw: ', raw_amps
		amps_stripped = np.nan_to_num(raw_amps)
# 		print 'amps_stripped: ', amps_stripped
		mfccs_stripped = np.nan_to_num(raw_mfccs)
		
		for relid, sfu in enumerate(segmented):

			offset = int(math.floor(sfu.onset / self.HOP_SECS))
			dur = int(math.floor(sfu.dur / self.HOP_SECS))
			#print '[[', offset, '|', dur, ']]'
			#amps += [self.analyze_scalar(amps_stripped, offset, dur)]
			self.sftree.nodes[sfid].add_metadata_for_relid(relid, amps=self.analyze_scalar(amps_stripped, offset, dur))
			#reheated += [np.mean(mfccs_stripped[offset:(offset+dur)], axis=0, dtype=np.float32)]
			self.sftree.nodes[sfid].add_metadata_for_relid(relid, mfccs=np.mean(mfccs_stripped[offset:(offset+dur)], axis=0, dtype=np.float32))
		
	# [MEAN, MAX, LVAL, RVAL, SLOPE]
	def analyze_scalar(self, raw_stripped, offset, dur):
		chopped = np.array(raw_stripped[offset:(offset+dur)], dtype=np.float32)
		mean = np.mean(chopped, dtype=np.float32)
		max = np.max(chopped)
		l_val = np.mean(chopped[:5], dtype=np.float32)
		r_val = np.mean(chopped[-5:], dtype=np.float32)
		slope = (r_val - l_val) / float(dur)
		return [mean, max, l_val, r_val, slope]

	# test me
	def add_corpus_unit(self, uid, metadata):
		"""
	
		"""
		# some basic metadata checks? check for key collisions?
		self.cutable[uid] = metadata

	# test me
	def remove_corpus_unit(self, cid):
		"""
		Remove a units from the corpus units table.	
		"""
		try:
			del self.cutable[cid]
		except KeyError:
			print 'Error: attempting to remove corpus unit that does not exist at index ', cid, '.'
	
	# test me
	def clear_corpus_units(self):
		"""
		Remove all units from the corpus units table.
		"""
		for k, unit in enumerate(self.cutable):
			self.cutable[k] = None
	
	# test me
	def _lookup_sfid(self, path):
		"""
		Look up id by querying path in sfmap table.
		"""
		try:
			sfid = self.sfmap[path]
		except KeyError:
			print 'Error: there is no entry for ', path, ' in the sf map. Update SFU failed.'
			return None
		return sfid

	# test me
	def get_sound_file_unit_metadata(self, sfid, path=None):
		"""
		Get the metadata rows for all units associated with a sound file.
		"""
		if sfid is None and path is not None:
			sfid = self._lookup_sfid(path)
		return sorted([entry for entry in self.cutable if entry[2] == sfid], key = lambda row: row[0])
	
	def map_sound_file_units_to_corpus_units(self):
		"""
		Build the corpus unit table from entries found in the sound file unit table.
		"""
		print "map sound file units to corpus units"
		self.clear_corpus_units()
# 		print '---------------------------------'
		print self.sftree.nodes.keys()
		for node in self.sftree.nodes.keys():
			sf_id = self.sftree.nodes[node].sfid
			sf_grp = self.sftree.nodes[node].group
			sf_tratio = self.sftree.nodes[node].tratio
# 			print sf_id, '|', sf_grp, '|', sf_tratio
			sf_unit_segments = self.sftree.nodes[node].unit_segments
			relid = 0
			
			
			try:
				for k in self.sftree.nodes[node].unit_amps.keys():
					amp_segment = self.sftree.nodes[node].unit_amps[k]
					mfccs_segment = self.sftree.nodes[node].unit_mfccs[k]
					index = self.cu_offset
					
					
					# GROUP!!!!
# 					print '@ relid: ', sf_unit_segments[relid].onset
					row = np.array([index, relid, sf_id, sf_grp, sf_unit_segments[relid].onset, sf_unit_segments[relid].dur, sf_tratio, sf_unit_segments[relid].tag])
#  					print 'row: ', row.shape
#  					print 'amp segment: ', amp_segment
#  					print 'mfccs segment: ', mfccs_segment
					self.add_corpus_unit(index, np.concatenate([row, amp_segment, mfccs_segment]))
					relid += 1
					self.cu_offset += 1
			except KeyError:
				print 'KeyError on segments traversal, trying to continue'
				pass
			except:
				print "Unexpected error:", sys.exc_info()[0]
				raise


	####*****
	#
	# CORPUS RAW ARRAY ACCESS
	#
	
	#	 index (8)         amp (5)        mfccs (24)	
	#	[0 1 2 3 4 5 6 7] [8 9 10 11 12] [13 14 15 16 17 ... 36]
	#
	
	def convert_corpus_to_array(self, type='all', map_flag=False):
		"""
		Convert the corpus unit table to a three compacted arrays: power metadata and MFCC metadata.
		"""
		if map_flag: self.map_sound_file_units_to_corpus_units()
		num_descriptors = len(self.cutable[0]) # hard code it?

		xlist = []
		for key in sorted(list(self.cutable.keys())):
			xlist.append([self.cutable[key]])
		X = np.array(xlist, dtype='float32')
		X = np.reshape(X, (-1, num_descriptors))
		
		if type is 'I':		return X[:,:8]
		elif type is 'A': 	return X[:,8:13]
		elif type is 'M':	return X[:,13:]
		elif type is 'all':	return X
		else:				raise ArgumentError

	def convert_corpus_to_tagged_array(self, type='all', tag=0.0, map_flag=False):
		"""
		Convert the corpus unit table to a three compacted arrays: power metadata and MFCC metadata.
		"""

		# get the info segments and filter those that are tagged
		info = self.convert_corpus_to_array('I', map_flag)
		
		indices = np.argwhere(info[:,7]==tag)
# 		indices = np.reshape(indices, (indices.shape[0],))

		# use the tagged indices to pull out the tagged entries
		filtered_by_type = self.convert_corpus_to_array(type)
		filtered_by_tag = filtered_by_type[indices]
		filtered_by_tag = np.reshape(filtered_by_tag, (indices.shape[0], filtered_by_type.shape[1]))

		# add indices as a column (on the left)
		return np.append(filtered_by_tag, indices, axis=1)
		
	
	def cuids_for_sfid(self, seed_sfid):
		return [int(self.cutable[entry][0]) for entry in self.cutable.keys() if self.cutable[entry][2] == seed_sfid]
			
	def import_corpus_from_json(self, jsonpath, appendflag=False, importflag=False):
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
		f = open(jsonpath, 'r')
		j = json.load(f)
		
		soundfiles = j['soundfiletree']
		for key in soundfiles:
			sf = soundfiles[key]
			# print sf
			try:
				pkey = sf['parent_id']
			except KeyError:
				sfid = self.add_sound_file(filename=sf['path'], 
											sfid=sf['sfID'] + self.sf_offset, 
											srcFileID=None, 
											tratio=sf['tratio'], 
											sfGrpID=sf['group'], 
# 											reuseFlag=True, 
# 											importFlag=importFlag, 
											uflag=sf['unique_id'])
		for key in soundfiles:
			sf = soundfiles[key]
			#print key, ' | ', sf['parent_id']
			#print type(key), ' || ', type(sf['parent_id'])
			try:
				pid = sf['parent_id']
				
				# params_with_dur = sf['params'] + ['dur', sf[ sf['parent_id'] ]]

				#print key, ' | ', soundfiles[key]['sfid'], ' | ', soundfiles[key]['parent_id']
				sfid = self.add_sound_file(filename=None, 
												sfid=sf['sfid'] + self.sf_offset, 
												srcFileID=pid + self.sf_offset, 
												tratio=sf['tratio'], 
												sfGrpID=sf['group'],
												synthdef=sf['synth'], 
												params=sf['params'],
												uflag=sf['unique_id'])
			except KeyError:
				pass
				#print 'Uh-oh'
				
		corpusunits = j['corpusunits']
		for key in corpusunits:
			# print '-----------------------'
			# print int(key)
			# print json.loads(corpusunits[key])
			cunit = json.loads(corpusunits[key])
			cunit[0] += self.cu_offset
			cunit[2] += self.sf_offset
			self.add_corpus_unit(int(key) + self.cu_offset, cunit)
		
		self.sf_offset = max(self.sftree.nodes.keys()) + 1
		print 'UPDATE max sfid --> sf_offset: ', self.sf_offset
		self.cu_offset = max(self.cutable.keys()) + 1
		print 'UPDATE max cutable key --> cu_offset: ', self.cu_offset
		
		f.close()
		
	
	def export_corpus_to_json(self, jsonpath):
		"""
		
		"""
		
		f = open(jsonpath, 'w')
		# don't forget the descriptors...
		toplevel = { 'descriptors': self.dtable }
		sf = dict()
		for sfid in self.sftree.nodes.keys():
			sf[sfid] = self.sftree.nodes[sfid].render_json()
		toplevel['soundfiletree'] = sf
		# roll the cutable rows into dictionary
		d = dict()
# 		print 'keys: ', self.cutable.keys()
		for cid in self.cutable.keys():
# 			print 'cutable entry: ', type(self.cutable[cid])
			d[cid] = json.dumps(self.cutable[cid].tolist())
		toplevel['corpusunits'] = d
		
		f.write(jsonpickle.encode(toplevel))	
		f.close()
	
