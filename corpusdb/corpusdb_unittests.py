import unittest

import sc
import corpusdb
from corpusdb import *
import numpy

# test creation of new corpusdb instance


class TestClassCreation(unittest.TestCase):

    def runTest(self):

        anchorpath = '/Users/kfl/dev/sc-0.3.1/testcorpus'
        actual_args = [anchorpath]
        expected = [anchorpath]

        cut = corpusdb.CorpusDB(actual_args[0])
        assert (expected[0] == cut.anchor)


class TestAddSoundFile(unittest.TestCase):

    def runTest(self):

        anchorpath = '/Users/kfl/dev/sc-0.3.1/testcorpus'
        fname = '36047.wav'
        #fname2 = '76444.wav'

        corpus = corpusdb.CorpusDB(anchorpath)
        # def addSoundFile(self, filename, sfid, srcFileID, tratio, sfGrpID=0, synthdef=None, params=None, reuseFlag=None, importFlag=None, uflag=None):
        the_node = corpus.add_sound_file(fname, None, None, 1.0, sfGrpID=0)

        self.assertEqual(the_node.sfid, 0)  # and (func_two_ret == 1)
        root = corpus.sftree.nodes[the_node.sfid]
        print(root)
        print("")
        self.assertEqual(root.sfid, 0)
        self.assertEqual(root.channels, 2)
        self.assertEqual(root.group, 0)
        self.assertEqual(root.tratio, 1.0)
        self.assertEqual(type(root.unique_id), float)
        self.assertEqual(corpus.sfgmap[0], set([0]))


class TestAnalyzeSoundFile(unittest.TestCase):

    def runTest(self):
        anchorpath = '/Users/kfl/dev/sc-0.3.1/testcorpus'
        fname = '36047.wav'

        corpus = corpusdb.CorpusDB(anchorpath)
        the_node = corpus.add_sound_file(fname, None, None, 1.0, sfGrpID=0)

        self.assertEqual(the_node.sfid, 0)

        corpus.analyze_sound_file(fname, the_node.sfid, group=0)
        dont_care = corpus.get_raw_metadata(the_node.sfid)

        self.assertEqual(numpy.shape(corpus.rawmaps[0]), (1262, 26))
        print(corpus.rawmaps[the_node.sfid][:4, :])
        self.assertAlmostEqual(
            corpus.rawmaps[the_node.sfid][3][0], 0.0347038, places=6)

        corpus._deactivate_raw_sound_file(the_node.sfid)
        with self.assertRaises(KeyError) as cm:
            res = corpus.rawmaps[the_node.sfid]
        the_exception = cm.exception
        self.assertEqual(type(the_exception), KeyError)


class TestCorpusUnits(unittest.TestCase):
    def runTest(self):
        pass


class TestSoundFileUnits(unittest.TestCase):
    def runTest(self):
        anchorpath = '/Users/kfl/dev/sc-0.3.1/testcorpus'
        fname = '36047.wav'

        corpus = corpusdb.CorpusDB(anchorpath)
        sfid = corpus.add_sound_file(fname, None, None, 1.0, sfGrpID=0).sfid
        print('$$$$$$$$$$$: ', sfid)
        corpus.analyze_sound_file(fname, sfid, group=0)
        dont_care = corpus.get_raw_metadata(sfid)

        corpus.add_sound_file_unit(
            0, path=None, onset=0.0, dur=1.0)  # ignore sfg for now

        res = corpus._lookup_sfid(anchorpath + '/snd/' + fname)

        self.assertEqual(res, 0)
        self.assertEqual(res, sfid)
        corpus.add_sound_file_unit(sfid=None, path=fname, onset=1.0, dur=0.5)

        print('$$$$$$$$$$$: ', corpus.sftree.nodes[sfid].unit_segments)
        self.assertEqual(corpus.get_sorted_units_list(sfid)
                         [0], corpusdb.SFU(0, 1.0, 0))
        self.assertEqual(corpus.get_sorted_units_list(sfid)
                         [1], corpusdb.SFU(1.0, 0.5, 0))

# 		corpus.update_sound_file_unit(sfid, relid=0, oldbounds=[0,1000], newbounds=[250,750])
# 		self.assertEqual(corpus.segtable[sfid]['trios'][0], [250,750,0])
# 		corpus.update_sound_file_unit(sfid=None, path=fname, oldbounds=[250,750], newbounds=[0,500])
# 		self.assertEqual(corpus.segtable[sfid]['trios'][0], [0,500,0])
#
# 		#corpus.updateSoundFileUnit(sfid, relid=1, sfg=22)
# 		#self.assertEqual(corpus.segtable[sfid]['pair'][1], 22)

        # after removing an sfu, access should result in an indexerror(at least if it is the last in the list)
        corpus.remove_sound_file_unit(sfid, relid=1)
        with self.assertRaises(IndexError) as cm:
            res = corpus.sftree.nodes[sfid].unit_segments[1]
        the_exception = cm.exception
        self.assertEqual(type(the_exception), IndexError)

        corpus.clear_sound_file_units(sfid)
        self.assertEqual(corpus.sftree.nodes[sfid].unit_segments, [])


class TestWriteJSONAndReadBack(unittest.TestCase):
    def runTest(self):
        pass


class TestParentAndChildNodes(unittest.TestCase):

    def runTest(self):
        anchorpath = '/Users/kfl/dev/sc-0.3.1/testcorpus'
        fname = '36047.wav'

        corpus = corpusdb.CorpusDB(anchorpath)
        sfidA = corpus.add_sound_file(fname, None, None, 1.0, sfGrpID=0).sfid
        print(sfidA)
        sfidB = corpus.add_sound_file(None, None, sfidA, 1.0, sfGrpID=0, synthdef=[
                                      'clipDistS'], params=[['inBus', 44, 'outBus', 46, 'mult', 5.0, 'clip', 1.0]]).sfid

        self.assertEqual(corpus.sftree.trackbacks[sfidA], [
                         '/Users/kfl/dev/sc-0.3.1/testcorpus/snd/36047.wav', 50.47734693877551, 1.0, 'stereoSamplerNRT'])

        self.assertEqual(corpus.sftree.trackbacks[sfidB][0], ['clipDistS'])
        print('-------------')
        print(corpus.sftree.trackbacks[sfidB][1])
        # cannot test bus assignments, b/c that is determined at synthdef runtime
        self.assertEqual(corpus.sftree.trackbacks[sfidB][1][0][4:], [
                         'mult', 5.0, 'clip', 1.0])

        corpus.analyze_sound_file(fname, sfidA, group=0)
        corpus.analyze_sound_file(fname, sfidB, group=0)
        dont_care = corpus.get_raw_metadata(sfidA)
        dont_care = corpus.get_raw_metadata(sfidB)

        corpus.add_sound_file_unit(sfidA, None, 0.0, 1.0)
        corpus.add_sound_file_unit(sfidB, None, 0.0, 1.0)


if __name__ == "__main__":

    print("===== Test Class (CorpusDB) Creation =====")
    testcase = TestClassCreation()
    runner = unittest.TextTestRunner()
    runner.run(testcase)
    print("===== Test Sound File Addition (@ Root) =====" 	)
    testcase = TestAddSoundFile()
    runner = unittest.TextTestRunner()
    runner.run(testcase)
    print("===== Test Sound File Analysis =====" 	)
    testcase = TestAnalyzeSoundFile()
    runner = unittest.TextTestRunner()
    runner.run(testcase)
    print("===== Test SoundFile Units Manipulation =====" 	)
    testcase = TestSoundFileUnits()
    runner = unittest.TextTestRunner()
    runner.run(testcase)
    print("===== Test Parent and Child Node Creation =====" 	)
    testcase = TestParentAndChildNodes()
    runner = unittest.TextTestRunner()
    runner.run(testcase)
#	print ("===== Test Corpus Units Manipulation =====" 	)
#	testcase = TestCorpusUnits()
#	runner = unittest.TextTestRunner()
#	runner.run(testcase)
#	print ("===== Test Write JSON File and Read JSON File Back =====" 	)
#	testcase = TestWriteJSONAndReadBack()
#	runner = unittest.TextTestRunner()
#	runner.run(testcase)
