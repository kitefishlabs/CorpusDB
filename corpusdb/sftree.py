#

"""
Part of corpusdb, corpus-based processing for SuperCollider + Python.

Overview
========

etc.

"""

__version__ = '1.0'
__author__ = 'Thomas Stoll'
__copyright__ = "Copyright (C) 2012-13, Thomas Stoll, All Rights Reserved"
__license__ = "gpl 3.0 or higher"
__email__ = 'tms@kitefishlabs.com'


import os, sys, time, wave, contextlib


class SFTree:

	def __init__(self, crps, path):
		self.corpus = crps
		self.anchorPath = path
		self.nodes = dict()
		self.sfmap = dict()
		
	def add_root_node(self, filename, sfID, tratio, snd_subdir=None, uniqueFlag=None):
		"""
		
		"""
# 		print "add file: ", filename, "for sfid: ", sfID
		if snd_subdir:
			rel_path = os.path.join(snd_subdir, filename)
			joined_path = os.path.join(self.anchorPath, 'snd', snd_subdir, filename)
		else:
			rel_path = filename
			joined_path = os.path.join(self.anchorPath, 'snd', filename)
# 		print "joined: ", joined_path
		if uniqueFlag:
			flag = uniqueFlag
		else:
			flag = time.time() - 1300000000.0 ## SUN March 13, 2011 ca. 3AM == 1.3 billion seconds since epoch
		
		with contextlib.closing(wave.open(joined_path,'r')) as f:
			frames = f.getnframes()
			rate = f.getframerate()
			dur = frames/float(rate)
			chnls = f.getnchannels()
		
		if chnls == 1: synthdef = 'monoSamplerNRT'
		else: synthdef = 'stereoSamplerNRT'
# 		print 'SD: ', synthdef
		
		try:
			self.nodes[sfID] = SamplerNode(rel_path, synthdef, dur, flag, chnls, tratio, sfID)			
			# secondary mappings
# 			self.corpus.map_id_to_sf(rel_path, sfID)
			self.sfmap[sfID] = [rel_path, dur, tratio, synthdef] # a more compact representation
			return self.nodes[sfID]
		except:
		    print "Unexpected error:", sys.exc_info()[0]
		    raise
		return None
	
		
	def add_child_node(self, parentID, childID, tratio, synthdef, params, uniqueFlag=None):
		"""
	
		"""
		if uniqueFlag:
			flag = uniqueFlag
		else:
			flag = time.time() - 1300000000.0
		
		try:
			parentNode = self.nodes[parentID]
		except KeyError:
			print 'Parent\'s childID is not found. Child node was not added'
			return None
		try:
			self.nodes[childID] = EfxNode(synthdef, params, parentNode.duration, flag, parentNode.channels, parentNode.tratio, childID, parentID)

			# secondary mappings
# 			self.corpus.map_id_to_sf(self.nodes[parentID].sfpath, childID)
			self.sfmap[childID] = [synthdef, params]
			
#			return childID, tratio
			return self.nodes[self.nodes[childID].sfid]

		except:
		    print "Unexpected error:", sys.exc_info()[0]
		    raise
		return None


class Node:
	def __init__(self, synthname, params=None, duration=-1, uniqueID=-1, channels=1, group=0, tratio=1.0, sfID=-1):
		"""
	
		"""
		self.synth = synthname
		self.params = params
		self.duration = duration
		self.unique_id = uniqueID
		self.channels = channels
		self.tratio = tratio
		self.sfid = sfID
		self.unit_segments = [] # create an empty container for unit bounds and tags
		self.unit_amps = dict()
		self.unit_mfccs = dict()
		self.verify_synthname_and_params()


	def verify_synthname_and_params(self):
		"""
	
		"""
		# check that synthname is a string
		# check that it exists in the synthdefs dir for this corpus
		# check that params match expected params
		#	 optionally warn if they do not
		pass
	
	def add_onset_and_dur_pair(self, onset, dur, relid=None):
# 		print '$$$ ', onset, '|', dur, '|(', relid, ')'
		if relid is None: relid = len(self.unit_segments)
		try:
			self.unit_segments[relid].onset = min(max(0, onset), self.duration)
		except IndexError:
			self.unit_segments += [SFU(min(max(0, onset), (self.duration / self.tratio)))]
		self.unit_segments[relid].dur = min(((self.duration / self.tratio) - self.unit_segments[relid].onset), max(0, dur))
		
		return self.unit_segments[relid]
	
	def update_unit_segment_params(self, relid, onset=None, dur=None, tag=None):
		if onset is not None: self.unit_segments[relid].onset = onset
		if dur is not None: self.unit_segments[relid].dur = dur
		if tag is not None: self.unit_segments[relid].tag = tag
		return self.unit_segments[relid]
	
	def calc_remaining_dur(self):
		"""
		Purely a convenience function for cases where non-overlapping segments are assumed!
		"""
		return (self.duration - self.unit_segments[-1].onset)
	
	def sort_segments_list(self):
		"""
		
		"""
		return  [x for x in self.unit_segments] #.sort(key=lambda unit: unit[0])
	
	def add_metadata_for_relid(self, relid, amps=None, mfccs=None):
		if relid is not None and amps is not None: self.unit_amps[relid] = amps
		if relid is not None and mfccs is not None: self.unit_mfccs[relid] = mfccs
		
	
class SamplerNode(Node):
	"""
	SamplerNode(joined_path, synthdef, dur, flag, chnls, tratio, sfID)
	"""
	def __init__(self, sfpath, synthname, duration=-1, uniqueID=-1, channels=1, tratio=1.0, sfID=-1):
		"""
	
		"""
		try:
			Node.__init__(self, synthname, None, duration, uniqueID, channels, tratio, sfID)
		except AttributeError:
			print 'Atrribute Error in superclass init'
		self.sfpath = sfpath
		self.hashstring = str(self.synth) + ("%.5f" % self.tratio)
		self.verify_sf()

	def __repr__(self):
		"""
	
		"""
		return "Sampler Node: %s (duration: %.2f, transp: %.4f)"%(self.sfpath, self.duration, self.tratio)

	def verify_sf(self):
		# check that sfpath is a string
		# check that it exists in the sounds dir (or a subdir) for this corpus
		pass
	
	def render_json(self):
		"""
	
		"""
		return { 'relpath' : self.sfpath,
			'synth' : self.synth,
			'params' : self.params,
			'duration' : self.duration,
			'uniqueID' : self.unique_id,
			'channels' : self.channels,
			'tRatio' : self.tratio,
			'sfID' : self.sfid,
			'hash' : self.hashstring }

class EfxNode(Node):
	"""
	EfxNode(synthdef, params, parentNodeMD['duration'], flag, parentNodeMD['channels'], childID, parentID, parentNodeMD['tratio'])
	"""
	def __init__(self, synthname, params, duration=-1, uniqueID=-1, channels=1, tratio=1.0, childID=-1, parentID=-1):
		"""
	
		"""
		try:
			Node.__init__(self, synthname, params, duration, uniqueID, channels, tratio, childID)
		except AttributeError:
			print 'Atrribute Error in superclass init'
		self.parent_id = parentID
		self.hashstring = str(self.synth[0])
		pdict = dict(zip([str(x) for x in self.params[0][0::2]], self.params[0][1::2]))
		for k in pdict:
			if (k != 'outbus') and (k != 'inbus') and (k != 'dur') and (k != 'envDur') and (k != 'transp'):
				self.hashstring += k
				if type(pdict[k]) == type(1.2):
					self.hashstring += str("%.5f" % pdict[k])
				else:
					self.hashstring += str(pdict[k])
		
	
	def __repr__(self):
		"""
	
		"""
		return "EFX Node: %s (parent id: %i, params: %s)"%(self.synth, self.parent_id, str(self.params))

	def verify_synthname_and_params(self):
		pass
	
	def render_json(self):
		"""
	
		"""
		return { 'parentID': self.parent_id,
			'synth' : self.synth,
			'params' : self.params,
			'duration' : self.duration,
			'uniqueID' : self.unique_id,
			'channels' : self.channels,
			'tRatio' : self.tratio,
			'sfID' : self.sfid,
			'hash' : self.hashstring }

class SynthNode(Node):
	def __init__(self, synthname, params):
		"""
	
		"""
		try:
			Node.__init__(self, synthname, params)
		except AttributeError:
			print 'Atrribute Error in superclass init'

	def __repr__(self):
		"""
	
		"""
		return "Synth Node: %s"%(self.synth)



class SFU():
	def __init__(self, onset=0, dur=0, tag=0):
		self.onset = onset
		self.dur = dur
		self.tag = tag
		
	def __repr__(self): return "Sound File Unit: (%f, %f) tag: %i"%(self.onset, self.dur, self.tag)	
	def __getitem__(self):
		return [self.onset, self.dur, self.tag]
	
	def __eq__(self, other):
		return (self.onset == other.onset) and (self.dur == other.dur) and (self.tag == other.tag)
	def __ne__(self, other):
		return (self.onset != other.onset) or (self.dur != other.dur) or (self.tag != other.tag)

