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
	
	# 2. Amp-constraint functions
	def amps_greater_than(self, subset_ids, threshold_unit, fudge=-3):
		
		thresh_amp = 10.0 ** (self.amps[threshold_unit,1] / 20.0)
# 		amp_lower_bound = 10.0 ** ((self.amps[threshold_unit,1] + fudge) / 20.0)
		db_lower_bound = self.amps[threshold_unit,1] + fudge
		# force int32 if not already so for subset_ids
		# ids are relative to all amps:
		subset_amps = self.amps[np.asarray(subset_ids, dtype='int32')]
		print "DB lower bound: ", db_lower_bound
		print "subset_amps: ", subset_amps
		# ids are relative to subset:
		subset_ids = np.reshape(np.argwhere(subset_amps[:,1]>db_lower_bound), (-1,1))
		return subset_ids # np.asarray(subset_amps[subset_ids][:,0], dtype='int32')

	# higher-level access functions?	
	# track storage?
	
	"""
	3. Ranking and reranking functions
	"""
	def rank_units_by_euc_dist(self, target_mfccs, pool_mfccs, depth=1000, varflag=False):
		id_ranking = np.array([], dtype='int32')
		print "shape: ", target_mfccs.shape[0] # [:,0]
		for i in range(target_mfccs.shape[0]):
			# calculate dists:
			if varflag is True:
				diffs_squared = np.square(np.subtract(np.atleast_2d(target_mfccs[i,3:16]), pool_mfccs))
				similarities = np.reshape(np.sum(np.multiply(diffs_squared, self.mfccs_vars[:,3:16]), axis=1), (-1,1))
			else:
				print target_mfccs[i,3:16].shape
				print pool_mfccs[:,3:16].shape
				similarities = np.reshape(distance.euc2(np.atleast_2d(target_mfccs[i,3:16]), pool_mfccs[:,3:16]), (-1,1))
			# sorted dists' indices:
			print "similarities before shape:", similarities.shape
			similarities = np.argsort(similarities, axis=None)[:depth]
			print "similarities shape:", similarities
			id_ranking = np.append(np.atleast_2d(id_ranking), pool_mfccs[similarities][:,0])
			print "pool_mfccs[similarities]: ", pool_mfccs[similarities].shape
			print "\n\nid ranking shape:", id_ranking, "\n\n"
		return np.reshape(id_ranking, (-1, min(depth, id_ranking.shape[0])))
		 
	
	"""
	t_minus_one_mfccs	-	full mfcc row for the target unit
	pool_mfccs			-	numpy array of mfccs representing
	"""
	def rerank_units_by_concat_cost(self, t_minus_one_mfccs, pool_mfccs, limit=-1):
		costs = np.reshape(distance.euc2(np.atleast_2d(t_minus_one_mfccs[:,3:16]), pool_mfccs[:,3:16]), (-1,1))
		costs = np.argsort(costs, axis=None)
		return np.asarray(pool_mfccs[costs][:limit,0], dtype='int32')
	
	"""
	target_id 	-	(int) corpus id of target unit
	pool_ids	-	(numpy array) ids pool units to be (re)ranked; usually whatever is returned from rank_units
	limit		-	(int) optional max number of units to return
	"""
	def rerank_units_by_amp(self, target_id, pool_ids, limit=None):
		
		target_amps = self.amps_for_ids(np.array([target_id], dtype=np.int32))[:,1]
		
		diffs = np.reshape(distance.euc2(np.atleast_2d(target_amps), np.atleast_2d(self.amps_for_ids(pool_ids)[:,1]).T), (-1,1))
		diffs = np.argsort(diffs, axis=None)
		return np.asarray(pool_ids[diffs][:limit], dtype='int32'), diffs
	
	"""
	target_id_t_minus_1 	-	(int) corpus id of target unit at time point t - 1 in a sequence of target units
	target_id_t_plus_1		-	(int) corpus id of target unit at time point t + 1 in a sequence of target units
	pool_ids				-	(numpy array) ids pool units to be (re)ranked; usually whatever is returned from rank_units
	limit					-	(int) optional max number of units to return
	"""
	def rerank_units_by_amp_continuity(self, target_id_t_minus_1, target_id_t_plus_1, pool_ids, limit=None):
		
		target_amp_t_minus_1 = self.amps_for_ids(np.array([target_id_t_minus_1], dtype=np.int32))[:,1][0]
		target_amp_t_plus_1 = self.amps_for_ids(np.array([target_id_t_plus_1], dtype=np.int32))[:,1][0]
		avg_amp = (target_amp_t_minus_1 + target_amp_t_plus_1) / 2.0
		return self.rerank_units_by_amp(avg_amp, pool_ids)[:limit]
	
	"""
	targets		-	list of target indices
	ranked_ids	-	ranked list of candidate unit indices
	limit		-	max number of units to return
	"""
	def filter_units_by_amp_threshold_old(self, target_ids, ranked_ids, db_threshold=-3, limit=25):
# 		self.uni_wrg = UniformWRG(hi=limit)
		ranked_with_amps_gt = []
		try:
			target_ids.shape
		except AttributeError:
			target_ids = np.array([target_ids], dtype=np.int32)
		
		for i in range(target_ids.shape[0]):
			print "> ", target_ids[i]
			ranked_with_amps_gt += np.reshape(ranked_ids[i][self.amps_greater_than(ranked_ids[i], target_ids[i], fudge=db_threshold)], (1,-1))[:,:limit].tolist()
		
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

