from corpusdb import *
from bregman.suite import *


amendb = CorpusDB("/Users/kfl/dev/git/CorpusDB/corpusdb/examples/1-2_simple_analysis/")
amendb.import_corpus_from_json("test_amen.json")

mfccs_mat = amendb.convert_corpus_to_array('M')
mfccs_mat.shape

imagesc(mfccs_mat.T)

DEPTH = 10

nearby = np.array([], dtype='float32')

for n in range(mfccs_mat.shape[0]):
	indices = np.argsort(distance.euc2(np.atleast_2d(mfccs_mat[n]), mfccs_mat))
	nearby = np.append(nearby, indices[:,:DEPTH])

nearby = np.reshape(nearby, (-1, DEPTH))

nb_hist = np.histogram( nearby.flatten(), nearby.shape[0])
imagesc(nearby.T)
plt.plot(nb_hist[0])

