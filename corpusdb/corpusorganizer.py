import numpy as np

class CorpusTracker:

	def __init__(self, corpus):
		self.corpus = corpus
		self.ids = self.corpus.convert_corpus_to_array('I')
		self.amps = self.corpus.convert_corpus_to_array('A')
		self.mfccs = self.corpus.convert_corpus_to_array('M')
	
	
	# domain or set-based rules
	def _all_such_that(self, col, criterion, invflag=False):
		if invflag:
			return np.asarray(self.ids[np.argwhere(self.ids[:,col] != criterion),0], dtype='int32')
		else:
			return np.asarray(self.ids[np.argwhere(self.ids[:,col] == criterion),0], dtype='int32')
	
	def all_transpositions(self, transp, invflag=False):
		return self._all_such_that(9, transp, invflag)
	
	def all_children_of(self, parentid, invflag=False):
		return self._all_such_that(2, parentid, invflag)
	
	def all_of_sf(self, parentid, invflag=False):
		return self._all_such_that(1, parentid, invflag)
	
	def all_of_family(self, id, invflag=False):
		pass
	
	def all_tagged(self, tag, invflag=False):
		return self._all_such_that(5, tag, invflag)
	
	def all_same_proc(self, hashstring, invflag=False):
		return self._all_such_that(4, hashstring, invflag)
	
	# access helpers for domain rules
	def ids_for_ids(self, ids):
		return np.reshape(ids, (-1,))
	def amps_for_ids(self, ids):
		return np.reshape(self.amps[ids], (-1,6))
	def mfccs_for_ids(self, ids):
		return np.reshape(self.mfccs[ids], (-1,25))

	# misc.
	def all_parentids(self):
		return np.unique(np.asarray(self.ids, dtype='int32')[:,2])
	
	# Amp-constraint functions
	
	def amps_greater_than(self, subset_ids, threshold_unit, fudge=-3):
		
		thresh_amp = 10.0 ** (self.amps[threshold_unit,1] / 20.0)
# 		amp_lower_bound = 10.0 ** ((self.amps[threshold_unit,1] + fudge) / 20.0)
		db_lower_bound = self.amps[threshold_unit,1] + fudge
		# force int32 if not already so for subset_ids
		# ids are relative to all amps:
		subset_amps = self.amps[np.asarray(subset_ids, dtype='int32')]
		# ids are relative to subset:
		subset_ids = np.reshape(np.argwhere(subset_amps[:,1]>db_lower_bound), (-1,))
		return np.reshape(np.asarray(subset_amps[subset_ids][:,0], dtype='int32'), (-1))

	# higher-level access functions
	
# 	def  