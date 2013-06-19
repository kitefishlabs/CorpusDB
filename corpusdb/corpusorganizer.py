import numpy as np

class CorpusOrganizer:

	def __init__(self, corpus):
		self.corpus = corpus
		self.ids = self.corpus.convert_corpus_to_array('I')
		self.amps = self.corpus.convert_corpus_to_array('A')
		self.mfccs = self.corpus.convert_corpus_to_array('M')
	
	def _all_such_that(self, col, criterion, invflag=False):
		if invflag:
			return self.ids[np.argwhere(self.ids[:,col] != criterion),0]
		else:
			return self.ids[np.argwhere(self.ids[:,col] == criterion),0]
	
	def all_transpositions(self, transp, invflag=False):
		return 	self._all_such_that(9, transp, invflag)
	
	def all_children_of(self, parentid, invflag=False):
		return 	self._all_such_that(2, parentid, invflag)
	
	def all_of_sf(self, parentid, invflag=False):
		return 	self._all_such_that(1, parentid, invflag)
	
	def all_of_family(self, id, invflag=False):
		pass
	
	def all_tagged(self, tag, invflag=False):
		return 	self._all_such_that(5, tag, invflag)
	
	def all_same_proc(self, hashstring, invflag=False):
		return 	self._all_such_that(4, hashstring, invflag)
	
	
	
	