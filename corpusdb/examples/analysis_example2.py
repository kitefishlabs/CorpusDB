import os, os.path, glob
import corpusdb
import numpy as np
from bregman.suite import *


# def findCutPoints2(sfID, crps):
# 	cooked = crps.cooked_layers[sfID]
# 	size = cooked




anchorpath = '/Users/kfl/comp/supercollider/7.untitled'
sndpath = os.path.join(anchorpath, 'snd')
corpus = corpusdb.CorpusDB(anchorpath)

f = os.path.join(sndpath, '2.wav')
tval = 1
node = corpus.add_sound_file(filename=os.path.basename(f), srcFileID=None, tratio=tval, sfGrpID=0)

sfid = node.sfid
print '2. sfid: ', sfid

corpus.analyze_sound_file(os.path.basename(f), sfid, tratio=tval)
powers, mfcccs, al, cl = corpus.get_raw_metadata(sfid)

sfdur = (corpus.sftree.nodes[sfid].duration / tval)
cut_list = findCutPoints2(sfid, mfcccs)

