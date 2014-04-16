// \monoSamplerNRT - Sampler Synthdef, goes at head of chain
SynthDef(\sampler_mn_nrt, { |outbus=20, srcbufNum, start=0, dur=1, transp=1|
	var env, chain;
	env = EnvGen.kr(Env.linen(0.01, ((BufDur.kr(srcbufNum) / transp) - 0.02), 0.01, 1), gate: 1, doneAction: 2);
	Out.ar(outbus, Pan2.ar(PlayBuf.ar(1, srcbufNum, BufRateScale.kr(srcbufNum) * transp, startPos: (start * BufSampleRate.kr(srcbufNum))) * env));
}).load(s);

// \monoSampler - slighly different enveloping
SynthDef(\sampler_mn, { |outbus=20, srcbufNum, start=0, dur=1, transp=1, attack=0.01, release=0.01|
	var env, in, chain;
	env = EnvGen.kr(Env.linen(attack, (dur - (attack+release)), release, 1, curve:\sine), gate: 1, doneAction: 2);
	in = PlayBuf.ar(1, srcbufNum, BufRateScale.kr(srcbufNum) * transp, startPos: (start * BufSampleRate.kr(srcbufNum) * transp), loop:1);
	Out.ar(outbus, Pan2.ar(in*env));
}).load(s);


SynthDef(\sampler_st_nrt, { |outbus=20, srcbufNum, start=0, dur=1, transp=1|
	var env, chain;
	env = EnvGen.kr(Env.linen(0.01, ((dur / transp) - 0.02), 0.01, 1), gate: 1, doneAction: 2);
	chain = PlayBuf.ar(2, srcbufNum, BufRateScale.kr(srcbufNum) * transp, startPos: (start * BufSampleRate.kr(srcbufNum))) * env;
	Out.ar(outbus, chain);
}).load(s);

SynthDef(\sampler_st, { |outbus=0, srcbufNum, start=0, dur=1, transp=1, attack=0.01, release=0.01|
	var env, chain;
	env = EnvGen.kr(Env.linen(attack, ((dur / transp) - (attack+release)), release, 1), gate: 1, doneAction: 2);
	chain = PlayBuf.ar(2, srcbufNum, BufRateScale.kr(srcbufNum) * transp, startPos: (start * BufSampleRate.kr(srcbufNum))) * env;
	Out.ar(outbus, chain);
}).load(s);
