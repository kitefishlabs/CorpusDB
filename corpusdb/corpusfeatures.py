class CorpusMetadata: 

	def _init_specific(self, type, raw_data=None):
		print 'initialize CONTAINER'
		if type is 'mfcc13':
			self.type = 'mfcc13'
			self.synthdef_string = 'power_mfcc13BusAnalyzerNRT'
			self.numfeatures = 13
		if type is 'mfcc24':
			self.type = 'mfcc24'
			self.synthdef_string = 'power_mfcc24BusAnalyzerNRT'
			self.numfeatures = 24
		elif type is 'mfcc42':
			self.type = 'mfcc42'
			self.synthdef_string = 'power_mfcc42BusAnalyzerNRT'
			self.numfeatures = 42
		elif type is 'chroma12':
			self.type = 'chroma12'
			self.synthdef_string = 'power_chroma12BusAnalyzerNRT'
			self.numfeatures = 12
		elif type is 'chroma12':
			self.type = 'power'
			self.synthdef_string = 'power_chroma12BusAnalyzerNRT'
			self.numfeatures = 5
		else:
			return None
		
		print raw_data.shape
		print self.numfeatures
		
		if raw_data is None:
			self.numhops = 0
			self.raw_data = None
			assert(self.raw_data == None)
		else:
			if self.replace_raw_data(raw_data) is not None:
				print 'New num. of hops: ', self.numhops
	
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
	
class MFCC(CorpusMetadata):

	def __init__(self, type='mfcc13', raw_data=None):
		print 'initialize MFCC subclass'
		return self._init_specific(type, raw_data)

class Chroma(CorpusMetadata):

	def __init__(self, type='chroma12', raw_data=None):
		print 'initialize Chroma subclass'
		print raw_data.shape
		self._init_specific(type, raw_data)

class Power(CorpusMetadata):

	def __init__(self, type='power', raw_data=None):
		print 'initialize Power subclass'
		print raw_data.shape
		self._init_specific(type, raw_data)

