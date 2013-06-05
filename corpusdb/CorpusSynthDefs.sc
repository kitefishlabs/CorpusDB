// power_mfcc24BusAnalyzerNRT - analysis Synthdef for modular analysis, goes at tail of chain
(
// hop = 40 msec == 0.04 seconds == 1 / 25 fps == 25 Hz analysis frequency
SynthDef(\power_mfcc24BusAnalyzerNRT, { |inbus=20, savebufNum=0, hop=0.04|
	var in, chain, power, mfccs, driver, array;
	in = In.ar(inbus, 1);
	chain = FFT(LocalBuf(4096,1), in);

	power =			FFTPower.kr(chain);          // empirical multiplier
	mfccs =			MFCC.kr(chain, numcoeff:24); // or 13|24|42...

	// log the metadata into a buffer and signal sclang to read from the buffer
	driver = Impulse.kr( 1 / hop );
	Logger.kr([power, mfccs].flatten, driver, savebufNum);
	Out.ar(0, in);
}).load(s);

// \monoSamplerNRT - Sampler Synthdef, goes at head of chain
SynthDef(\monoSamplerNRT, { |outbus=20, srcbufNum, start=0, dur=1, transp=1|
	var env, chain;
	env = EnvGen.kr(Env.linen(0.01, ((BufDur.kr(srcbufNum) / transp) - 0.02), 0.01, 1), gate: 1, doneAction: 2);
	Out.ar(outbus, Pan2.ar(PlayBuf.ar(1, srcbufNum, BufRateScale.kr(srcbufNum) * transp, startPos: (start * BufSampleRate.kr(srcbufNum))) * env));
}).load(s);

// \monoSampler - slighly different enveloping
SynthDef(\monoSampler, { |outbus=20, srcbufNum, start=0, dur=1, transp=1, attack=0.01, release=0.01|
	var env, in, chain;
	env = EnvGen.kr(Env.linen(attack, (dur - (attack+release)), release, 1, curve:\sine), gate: 1, doneAction: 2);
	in = PlayBuf.ar(1, srcbufNum, BufRateScale.kr(srcbufNum) * transp, startPos: (start * BufSampleRate.kr(srcbufNum) * transp), loop:1);
	Out.ar(outbus, Pan2.ar(in*env));
}).load(s);
)


// processing Synthdefs - inserted in between Sampler and Analyzer
SynthDef(\clipDistM, { |outbus=20, inbus=21, mult=1.0, clip=1.0|
	Out.ar(outbus, Pan2.ar(In.ar(inbus, 1) * mult).clip2(clip), );
}).load(s);

SynthDef(\xoverM, { |outbus=20, inbus=21, amp=0.6, smooth=0.5, dur=1, transp=1, attack=0.01, release=0.1|
	var env = EnvGen.kr(Env.linen(attack, ((dur / transp) - (attack+release)), release, 1), gate: 1, doneAction: 2);
	Out.ar(outbus, Pan2.ar(CrossoverDistortion.ar(In.ar(inbus, 1), amp, smooth) * env));
}).load(s);

SynthDef(\combM, { |outbus=20, inbus=21, delay=0.2, decay=2.0, dur=1, transp=1, attack=0.01, release=0.1|
	var env = EnvGen.kr(Env.linen(attack, ((dur / transp) - (attack+release)), release, 1), gate: 1, doneAction: 2);
	Out.ar(outbus, Pan2.ar(CombC.ar(In.ar(inbus, 1), 1.0, delay, decay) * env));
}).load(s);

SynthDef(\magSmear, { |outbus=0, inbus=20, bins=10, amp=0.5, dur=1, transp=1, attack=0.01, release=0.1|
	var env, chain = FFT(LocalBuf(8192), In.ar(inbus,1));
	env = EnvGen.kr(Env.linen(attack, ((dur / transp) - (attack+release)), release, 1), gate: 1, doneAction: 2);
	chain = PV_MagSmear(chain, bins);
	Out.ar(outbus, Pan2.ar(amp * env * IFFT(chain).dup));
}).load(s);

SynthDef(\partialSynth, {|outbus=0, inbus=20, onset=0, start=0, envDur=1, dur=1, transp=1, attack=0.01, release=0.1|
	var env, chain, in = In.ar(inbus, 1);
	env = EnvGen.kr(Env.linen(attack, ((dur / transp) - (attack+release)), release, 1), gate: 1, doneAction: 2);
	chain = FFT(LocalBuf.new(2048, 1), in);
	// resynthesize according to MouseX. If 0, only sound with VERY stable changes of frequecy
	// will be returned. Upper limit should be Nyqust / nBins , e.g. 22050 / 2048 -> 21.532
	// or + and - 21.532
	chain = PV_PartialSynthF(chain, XLine.kr(start, 21, envDur), 3, 1);
	chain = IFFT(chain);
	Out.ar(outbus, Pan2.ar(chain * env));
}).load(s);
)

// EXTRAS - examples from earlier implementations of project

// \mfccBufferAnalyzerNRT - all-in-one design, not used in modular CorpusDB

SynthDef(\mfccBufferAnalyzerNRT, { |srcbufNum, start=0, dur=1, savebufNum, srate, transp=1, hop=1024|
	var env, in, chain, power, mfcc, driver, array;
	env = EnvGen.kr(Env.linen(0.01, ((dur / transp) - 0.02), 0.01, 1), gate: 1, doneAction: 2);
	in = PlayBuf.ar(1, srcbufNum, BufRateScale.kr(srcbufNum) * transp, startPos: start) * env;
	chain = FFT(LocalBuf(8192,1), in);

	power =			FFTPower.kr(chain);          // empirical multiplier
	mfcc =			MFCC.kr(chain,24);

	// log the metadata into a buffer and signal sclang to read from the buffer
	driver = Impulse.kr( srate / hop );
	Logger.kr(
		[power, mfcc].flatten,
		driver,
		savebufNum
	);
	//Poll.kr(driver, power.ampdb, ":::");
	Out.ar(0, in);
}).load(s);

// hop = 40 msec == 0.04 seconds == 1 / 25 fps == 25 Hz analysis frequency
SynthDef(\power_centroid_mfcc24BusAnalyzerNRT, { |inbus=20, savebufNum=0, hop=0.04|
	var in, chain, power, centroid, mfccs, driver, array;
	in = In.ar(inbus, 1);
	chain = FFT(LocalBuf(8192,1), in);

	power =			FFTPower.kr(chain);          // empirical multiplier
	centroid = 		SpecCentroid.kr(chain);
	mfccs =			MFCC.kr(chain, numcoeff:24); // or 13|24|42...

	// log the metadata into a buffer and signal sclang to read from the buffer
	driver = Impulse.kr( 1 / hop );
	Logger.kr([power, centroid, mfccs].flatten, driver, savebufNum);
	Out.ar(0, in);
}).load(s);
