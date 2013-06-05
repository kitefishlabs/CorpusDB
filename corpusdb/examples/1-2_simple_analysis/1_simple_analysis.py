import os, os.path, glob
import corpusdb
import numpy as np
from bregman.suite import *



# Set up a CorpusDB object
anchorpath = os.path.expanduser('~/dev/git/CorpusDB/corpusdb/examples/1_simple_analysis')
corpus = corpusdb.CorpusDB(anchorpath)

# create the full path and add the sound file
f = os.path.join(anchorpath, 'snd', '24940__vexst__amen.wav')
node = corpus.add_sound_file(filename=os.path.basename(f), tratio=1)

# there are default values: for parent nodes (nodes without children are parent nodes) srcFileID is None and for now, sound file group IDs will default to 0
# node = corpus.add_sound_file(filename=os.path.basename(f), srcFileID=None, tratio=1, sfGrpID=0)

# a Node object is returned, in this case a Sampler Node, which has a sound file ID
sfid = node.sfid

# pass the full path, the ID, and the transposition ratio to the analysis function
corpus.analyze_sound_file(os.path.basename(f), sfid, tratio=1)
# then access the raw metadata
powers, mfccs = corpus.get_raw_metadata(sfid)


def findCutPoints(rawmfccs, rawpowers, plotflag=False):
	diff = np.diff(rawmfccs, axis=0)
	sums = np.sum(np.abs(diff), axis=1)
	cnvlv = np.convolve(sums,np.hanning(9))
	if plotflag: plt.plot(cnvlv)
	minima = np.r_[True, cnvlv[1:] < cnvlv[:-1]] & np.r_[cnvlv[:-1] < cnvlv[1:], True]
	min_indices = np.where(minima)[0]

	# this will give you an array of indices, and you'll want to make sure some heuristic conditions are met:
	#
	#    0 should be a member
	#	 you don't need to filter out indices that are too close (your kernel did that already)
	#	 you may want to routinely chop any indices too close to the end (say, w/i 25%)
	#	 or, just cut off the last one, since we can probably trust that that one corresponds to the fade out
	#	 you may also want to adjust the minima-finding step (above) to not pick up "flat" local minima
	
# 	return min_indices[0][:-1] # just hack off the last one
	print min_indices[0]
	if (min_indices[0] > 2):
		min_indices = np.insert(min_indices, 0, 0)
	return min_indices

cut_list = findCutPoints(mfccs, powers)

for i, frame in enumerate(cut_list[:-1]):
	corpus.add_sound_file_unit(sfid, onset=(frame*0.04), dur=((cut_list[i+1]-frame)*0.04))

corpus.segment_units(sfid)

corpus.map_sound_file_units_to_corpus_units()
corpus.export_corpus_to_json('test_amen.json')