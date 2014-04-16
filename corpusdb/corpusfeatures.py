import math
import numpy as np

class CorpusMetadata: 

	def _init_specific(self, type, raw_data=None):
		print 'initialize CONTAINER'
		# first is a dummy entry
		if type is 'index9':
			self.type = 'index'
			self.synthdef_string = None
			self.numfeatures = 9
		elif type is 'mfcc13':
			self.type = 'mfcc'
			self.synthdef_string = 'bus_analyzer_power_mfcc13_mn_nrt'
			self.numfeatures = 13
		elif type is 'mfcc24':
			self.type = 'mfcc'
			self.synthdef_string = 'bus_analyzer_power_mfcc24_mn_nrt'
			self.numfeatures = 24
		elif type is 'mfcc42':
			self.type = 'mfcc'
			self.synthdef_string = 'bus_analyzer_power_mfcc42_mn_nrt'
			self.numfeatures = 42
		elif type is 'chroma12':
			self.type = 'chroma'
			self.synthdef_string = 'bus_analyzer_power_chroma12_mn_nrt'
			self.numfeatures = 12
		elif type is 'mfcc13_chroma12':
			self.type = 'mfcc_chroma'
			self.synthdef_string = 'bus_analyzer_power_mfcc13_chroma12_mn_nrt'
			self.numfeatures = 25
		# power ONLY
		elif type is 'power6':
			self.type = 'power'
			self.synthdef_string = 'bus_analyzer_power_mn_nrt'
			self.numfeatures = 5
		else:
			print "Could not form CorpusMetadata of type: ", str(type)
			return None
		
		if raw_data is not None: print raw_data.shape
		print self.numfeatures
		
		if raw_data is None:
			self.numhops = 0
			self.raw_data = None
			assert(self.raw_data == None)
		else:
			if self.replace_raw_data(raw_data) is not None:
				print 'New num. of hops: ', self.numhops
		self.proc_funcs = []
	
	def replace_raw_data(self, raw_data):
		if raw_data.shape[0] == self.numfeatures:
			self.raw_data = raw_data
			self.numhops = self.raw_data.shape[1]
			return (self.numfeatures, self.numhops)
		else:
			print 'fail - Features shape mismatch!'
			return None
	
	# def append_
	# def prepend_
	# def insert_
	# def delete_
	# ...etc...
	
	def calculate_means(self, raw_data):
		"""
		Assume that raw_data_shape[1] >= 1.
		"""
		return np.mean(raw_data, axis=0)

	def calculate_vars(self, raw_data):
		"""
		Assume that raw_data_shape[1] >= 1.
		"""
		return np.var(raw_data, axis=0)
	
	def calculate_stats(self, raw_data, offset=0, dur=-1, verb=True):
		"""
		[MEAN, VAR, MAX, LVAL, RVAL, SLOPE]
		offset and dur are in frames
		Assume that raw_data.shape[1] == 1.
		"""
 		if verb: print "offset: ", offset
 		if verb: print "dur: ", dur
 		if verb: print raw_data.shape
		if dur == -1:
			chopped = raw_data[offset:(offset+dur)]
		else:
			chopped = raw_data[offset:(offset+dur)]
 		if verb: print np.mean(chopped)
 		if verb: print np.var(chopped)
 		if verb: print np.mean(chopped[:2])
 		if verb: print np.mean(chopped[-2:])
		mn = np.mean(chopped)
		var = np.var(chopped)
		max = np.max(chopped).tolist()
		l_val = np.mean(chopped[:2])
		r_val = np.mean(chopped[-2:])
		slope = (r_val - l_val) / float(dur)
 		if verb: print [mn, var, max, l_val, r_val, slope]
 		####$ WHY * 20.0 ???
		return [math.log10(mn), var, max, l_val, r_val, slope]
		# return [math.log10(x) if x > 0.000001 else -120 for x in [mn, max, l_val, r_val]] + [slope]

class Indexes(CorpusMetadata):
	
	def __init__(self, type='index9', raw_data=None):
		print 'initialize Index subclass...'
		self._init_specific(type, raw_data)
		self.indexmap = dict({
			0: 'unitID',
			1: 'parentID', 
			2: 'sfileID', 
			3: 'sfRelID', 
			4: 'procID', 
			5: 'tag',
			6: 'onset', 
			7: 'duration', 
			8: 'tRatio'})
		self.rawwidth = 0
		self.width = 9

class Powers(CorpusMetadata):
	"""
		Only for stand-alone usage.
	"""
	def __init__(self, type='power6', stat_flag=True, raw_data=None):
		print 'initialize Power subclass...'
		if raw_data is not None: print raw_data.shape
		self.indexes = Indexes()
		self._init_specific(type, raw_data)
		if stat_flag:
			self.proc_funcs = [self.calculate_stats]
		print '##: ', self.numfeatures
		self.rawwidth = 1
		self.width = 5
		self.indexmap = None

class MFCCs(CorpusMetadata):

	def __init__(self, type='mfcc13', var_flag=False, raw_data=None):
		print 'initialize MFCC subclass...'
		if raw_data is not None: print raw_data.shape
		self.powers = Powers()
		self._init_specific(type, raw_data)
		self.rawwidth = self.numfeatures
		if var_flag:
			self.proc_funcs = [self.calculate_means, self.calculate_vars]
			self.width = self.numfeatures * 2
		else:
			self.proc_funcs = [self.calculate_means]
			self.width = self.numfeatures
		# self.powers.rawwidth == 1
		# self.powers.width == 5
		self.indexmap = None

class Chromas(CorpusMetadata):

	def __init__(self, type='chroma12', var_flag=False, raw_data=None):
		print 'initialize Chroma subclass...'
		if raw_data is not None: print raw_data.shape
		self.powers = Powers()
		self._init_specific(type, raw_data)
		self.rawwidth = self.numfeatures
		if var_flag:
			self.proc_funcs = [self.calculate_means, self.calculate_vars]
			self.width = self.numfeatures * 2
		else:
			self.proc_funcs = [self.calculate_means]
			self.width = self.numfeatures
		self.width = self.powers.numfeatures + self.numfeatures
		# self.powers.rawwidth == 1
		# self.powers.width == 5
		self.indexmap = None

class MFCC_Chromas(CorpusMetadata):

	def __init__(self, type='mfcc13_chroma12', var_flag=False, raw_data=None):
		print 'initialize MFCC+Chroma (combo) subclass...'
		if raw_data is not None: print raw_data.shape
		self.powers = Powers()
		self._init_specific(type, raw_data)
		self.indexmap = None
		self.rawwidth = self.numfeatures
		if var_flag:
			self.proc_funcs = [self.calculate_means, self.calculate_vars]
			self.width = self.numfeatures * 2 # == 50
		else:
			self.proc_funcs = [self.calculate_means]
			self.width = self.numfeatures # == 25
		# self.powers.rawwidth == 1
		# self.powers.width == 5
		self.indexmap = None
