import numpy as np
from bregman.suite import *
import random, math
import bisect


class UniformRandomGenerator(object):
	"""
	"""
	def __init__(self):
		pass
# 		self.lo = lo
# 		self.hi = hi
		
	def next(self, ulimit=100):
		return int(random.random() * ulimit)

	def __call__(self, ulimit=100): return self.next(ulimit)


class WeightedRandomGenerator(object):
	"""
	"""
	def __init__(self, weights=[(1.0 - float(x / 10000.0)) for x in range(10000)]):
		self.totals = []
		self.weights = weights
		running_total = 0
		self.size = len(weights)

		for w in weights:
			running_total += w
			self.totals.append(running_total)

	def next(self, ulimit=100):
		rnd = random.random() * self.totals[-1]
		return int(bisect.bisect_right(self.totals, rnd) / float(self.size) * ulimit)

	def __call__(self, ulimit=100): return self.next(ulimit)


class CorpusTracker:

	def __init__(self, corpus):
		self.corpus = corpus
		self.ids = self.corpus.convert_corpus_to_array('I')
		self.amps = self.corpus.convert_corpus_to_array('A')
		self.mfccs = self.corpus.convert_corpus_to_array('M')
		self.amps_vars = np.reshape(np.var(self.amps[:,1:], axis=0), (-1,5))
		self.mfccs_vars = np.reshape(np.var(self.mfccs[:,1:], axis=0), (-1,24))
		self.rg = self.select_rg()
	
	# 1. domain or set-based rules
	def _all_such_that(self, col, criterion, invflag=False):
		if invflag:
			return np.asarray(self.ids[np.argwhere(self.ids[:,col] != criterion),0], dtype='int32')
		else:
			return np.asarray(self.ids[np.argwhere(self.ids[:,col] == criterion),0], dtype='int32')
	
	def all_transpositions(self, transp, invflag=False):
		return np.reshape(self._all_such_that(9, transp, invflag), (-1,))
	
	def all_children_of(self, parentid, invflag=False):
		return np.reshape(self._all_such_that(2, parentid, invflag), (-1,))
	
	def all_of_sf(self, sfid, invflag=False):
		return np.reshape(self._all_such_that(3, sfid, invflag), (-1,))
		
	def all_tagged(self, tag, invflag=False):
		return np.reshape(self._all_such_that(6, tag, invflag), (-1,))
	
	def all_same_proc(self, hashstring, invflag=False):
		return np.reshape(self._all_such_that(5, hashstring, invflag), (-1,))
	
	# 1a. access helpers for domain rules
	def ids_for_ids(self, ids):
		return np.reshape(ids, (-1,))
	def amps_for_ids(self, ids):
		return np.reshape(self.amps[np.asarray(ids.reshape((1,-1)), dtype='int32')], (-1,6))
	def mfccs_for_ids(self, ids):
		return np.reshape(self.mfccs[np.asarray(ids.reshape((1,-1)), dtype='int32')], (-1,25))

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
		subset_ids = np.reshape(np.argwhere(subset_amps[:,1]>db_lower_bound), (-1,1))
		return subset_ids # np.asarray(subset_amps[subset_ids][:,0], dtype='int32')

	# higher-level access functions?
	
	# track storage?
	
	def rank_units_by_euc_dist(self, targets_mfccs, pool_mfccs, depth=1000, varflag=False):
		id_ranking = np.array([], dtype='int32')
		for i in range(targets_mfccs[:,0].shape[0]):
			# calculate dists:
			if varflag is True:
				diffs_squared = np.square(np.subtract(np.atleast_2d(targets_mfccs[i,1:]), pool_mfccs[:,1:]))
				similarities = np.reshape(np.sum(np.multiply(diffs_squared, self.mfccs_vars), axis=1), (-1,1))
			else:
				similarities = np.reshape(distance.euc2(np.atleast_2d(targets_mfccs[i,1:]), pool_mfccs[:,1:]), (-1,1))
			# sorted dists' indices:
			similarities = np.argsort(similarities, axis=None)[:depth]			
			id_ranking = np.append(np.atleast_2d(id_ranking), pool_mfccs[similarities][:,0])
		return np.reshape(id_ranking, (-1, depth))

	# [:,1:] ???
	def rerank_units_by_concat_cost(self, t_minus_one_mfccs, prosp_mfccs):
# 		print t_minus_one_mfccs.shape
# 		print prosp_mfccs.shape
		costs = np.reshape(distance.euc2(np.atleast_2d(t_minus_one_mfccs[1:]), prosp_mfccs[:,1:]), (-1,1))
		costs = np.argsort(costs, axis=None)
		costs = np.asarray(costs, dtype='int32')
		return np.asarray(prosp_mfccs[costs][:,0], dtype='int32')
	

	def rerank_units_by_amp(self, target_amp, prosp_amps):
		diffs = np.reshape(distance.euc2(np.atleast_2d(target_amp), np.atleast_2d(prosp_amps[:,1]).T), (-1,1))
		diffs = np.argsort(diffs, axis=None)
		diffs = np.asarray(diffs, dtype='int32')
		return np.asarray(prosp_amps[diffs][:,0], dtype='int32')
	
	def rerank_units_by_amp_continuity(self, target_amp_t_minus_1, prosp_amps, target_amp_t_plus_1):
		avg_amp = (target_amp_t_minus_1 + target_amp_t_plus_1) / 2.0
		return self.rerank_units_by_amp(avg_amp, prosp_amps)

	
	def filter_units_by_amp_threshold(self, targets, ranked_ids, limit=25, db_threshold=-3):
# 		self.uni_wrg = UniformWRG(hi=limit)
		ranked_with_amps_gt = []
		for i in range(targets.shape[0]):
			ranked_with_amps_gt += np.reshape(ranked_ids[0][self.amps_greater_than(ranked_ids[i,:], targets[i], fudge=db_threshold)], (1,-1))[:,:limit].tolist()
		return ranked_with_amps_gt
	
	def select_rg(self, type='urg', size=100):
		if type is 'urg':
			self.rg = UniformRandomGenerator()
		elif type is 'wrg':
			weights = [((1.0-(float(x/float(size))))**2.0) for x in range(size)]
			self.rg = WeightedRandomGenerator(weights)
		return self.rg
	
	def rand_slot_for_depth(self, depth): 
		return self.rg.next(depth)
	
	def iterate_random_substitutions(self, targetlist, filteredlists, num_iters=100):
		tsize = len(targetlist)
		translist = [([x]+filteredlists[i]) for i,x in enumerate(targetlist)]
		statelist = targetlist[:]
		
		for i in range(num_iters):
			uindex = self.rand_slot_for_depth(tsize-1)
# 			print "uindex: ", uindex
# 			print "len: ", len(filteredlists[uindex])
			selindex = self.rand_slot_for_depth(len(filteredlists[uindex]) - 1)
			uchoice = filteredlists[uindex][selindex]
# 			print "uchoice: ", uchoice
			statelist[uindex] = uchoice
		return statelist

