class CorpusMetadata: 

	def __init__(self, type, raw_data=None):
		print 'initialize CONTAINER'
		if type is 'mfcc13':
			self.type = 'mfcc13'
			self.numfeatures = 13
		if type is 'mfcc13':
			self.type = 'mfcc24'
			self.numfeatures = 24
		elif type is 'mfcc13':
			self.type = 'mfcc42'
			self.numfeatures = 42
		elif type is 'mfcc13':
			self.type = 'chroma12'
			self.numfeatures = 12
		else:
			return None
		
		if raw_data is None:
			raw_data.numhops = 0
		else:
			self.numhops = raw_data.shape[1]
			if raw_data.shape[0] != self.numfeatures:
				return None

	
class MFCC(CorpusMetadata):

	def __init__(self, type=type, raw_data=raw_data):
		print 'initialize MFCC subclass'