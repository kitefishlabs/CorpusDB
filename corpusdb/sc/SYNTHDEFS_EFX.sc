(
SynthDef(\efx_thru_mn, { |outbus=21, inbus=20, dummy=0|
	Out.ar(outbus, In.ar(inbus, 1));
}).load(s);

/*SynthDef(\efx_thru_st, { |outbus=21, inbus=20|
	Out.ar(outbus, In.ar(inbus, 2));
}).load(s);*/

SynthDef(\efx_gain_mn, { |outbus=21, inbus=20, gain=1|
	Out.ar(outbus, In.ar(inbus, 1) * gain);
}).load(s);

// PV efx

SynthDef(\efx_pvpartialsynth_mn, {|outbus=21, inbus=20, pcut=0.1, gain=1|
	var chain, in = In.ar(inbus, 1);
	chain = FFT(LocalBuf.new(2048, 1), in);
	// Upper limit should be Nyqust / nBins , e.g. 22050 / 2048 -> 21.532
	// or + and - 21.532
	chain = PV_PartialSynthF(chain, pcut*21.532, 3, 0);
	chain = IFFT(chain);
	Out.ar(outbus, (chain * gain));
}).load(s);

SynthDef(\efx_pvmagsmear_mn, { |outbus=21, inbus=20, bins=100, gain=1|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = FFT(LocalBuf(2048,1), in);
	chain = PV_MagSmear(chain, bins);
	Out.ar(outbus, IFFT(chain) * gain);
}).send(s);

SynthDef(\efx_pvbrickwall_mn, { |outbus=21, inbus=20, wipe=0, gain=1|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = FFT(LocalBuf(2048,1), in);
	chain = PV_BrickWall(chain, wipe);
	Out.ar(outbus, IFFT(chain) * gain);
}).send(s);

SynthDef(\efx_pvmagabove_mn, { |outbus=21, inbus=20, thresh=0, gain=1|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = FFT(LocalBuf(2048,1), in);
	chain = PV_MagAbove(chain, thresh);
	Out.ar(outbus, IFFT(chain) * gain);
}).send(s);

SynthDef(\efx_pvmagbelow_mn, { |outbus=21, inbus=20, thresh=0, gain=1|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = FFT(LocalBuf(2048,1), in);
	chain = PV_MagBelow(chain, thresh);
	Out.ar(outbus, IFFT(chain) * gain);
}).send(s);

SynthDef(\efx_pvmagclip_mn, { |outbus=21, inbus=20, thresh=0, gain=1|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = FFT(LocalBuf(2048,1), in);
	chain = PV_MagClip(chain, thresh);
	Out.ar(outbus, IFFT(chain) * gain);
}).send(s);

SynthDef(\efx_pvphaseshift_mn, { |outbus=21, inbus=20, shift=0, gain=1|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = FFT(LocalBuf(2048,1), in);
	chain = PV_PhaseShift(chain, shift);
	Out.ar(outbus, IFFT(chain) * gain);
}).send(s);

SynthDef(\efx_pvphaseshifti_mn, { |outbus=21, inbus=20, shift=0, gain=1|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = FFT(LocalBuf(2048,1), in);
	chain = PV_PhaseShift(chain, shift, 1);
	Out.ar(outbus, IFFT(chain) * gain);
}).send(s);




// Frequency shifting and granular efx
SynthDef(\efx_freqshift_mn, { |outbus=21, inbus=20, freq=0, phase=0, gain=1|
	Out.ar(outbus, (FreqShift.ar(In.ar(inbus, 1), freq, phase)) * gain);
}).load(s);

SynthDef(\efx_pitchshift_mn, { |outbus=21, inbus=20, windowsize=0.1, pitchratio=1, pitchdisp=0, timedisp=0, gain=1|
	Out.ar(outbus, (PitchShift.ar(In.ar(inbus, 1), windowsize, pitchratio, pitchdisp, timedisp.min(windowsize))) * gain);
}).load(s);

SynthDef(\efx_monograin_mn, { |outbus=21, inbus=20, windowsize=0.1, grainrate=10, winrandperc=0.5, gain=1|
	Out.ar(outbus, (MonoGrain.ar(In.ar(inbus, 1), windowsize, grainrate, winrandperc)) * gain);
}).load(s);

SynthDef(\efx_comb_mn, { |outbus=21, inbus=20, delay=0.2, decay=1.0, gain=1|
	Out.ar(outbus, (CombC.ar(In.ar(inbus, 1), 2, delay, decay)) * gain);
}).load(s);





SynthDef(\efx_clipdist_mn, { |outbus=21, inbus=20, mult=1.0, clip=1.0, gain=1|
	Out.ar(outbus, (In.ar(inbus, 1) * mult).clip2(clip) * gain);
}).load(s);

/*SynthDef(\efx_clipdist_st, { |outbus=21, inbus=20, mult=1.0, clip=1.0, gain=1|
	Out.ar(outbus, (In.ar(inbus, 2) * mult).clip2(clip) * gain);
}).load(s);*/

SynthDef(\efx_softclipdist_mn, { |outbus=21, inbus=20, mult=1.0, sclip=1.0, gain=1|
	Out.ar(outbus, (In.ar(inbus, 1) * mult).softclip(sclip) * gain);
}).load(s);

SynthDef(\efx_decimatordist_mn, { |outbus=21, inbus=20, rate=44100, bits=24, gain=1|
	Out.ar(outbus, Decimator.ar(In.ar(inbus, 1), rate, bits) * gain);
}).load(s);

SynthDef(\efx_smoothdecimatordist_mn, { |outbus=21, inbus=20, rate=44100, smooth=0.5, gain=1|
	Out.ar(outbus, SmoothDecimator.ar(In.ar(inbus, 1), rate, smooth) * gain);
}).load(s);

SynthDef(\efx_crossoverdist_mn, { |outbus=21, inbus=20, amp=0.5, smooth=0.5, gain=1|
	Out.ar(outbus, CrossoverDistortion.ar(In.ar(inbus, 1), amp, smooth) * gain);
}).load(s);

SynthDef(\efx_sineshaperdist_mn, { |outbus=21, inbus=20, amp=0.5, smooth=0.5, gain=1|
	Out.ar(outbus, SineShaper.ar(In.ar(inbus, 1), amp, smooth) * gain);
}).load(s);

// FUN FILTERS!

SynthDef(\efx_ringz_mn, { |outbus=21, inbus=20, freq=1000, decay=1.0, gain=0|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = Ringz.ar(in, freq, decay);
	Out.ar(outbus, (chain * gain));
}).load(s);

SynthDef(\efx_resonz_mn, { |outbus=21, inbus=20, freq=1000, bwr=1.0, gain=0|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = Resonz.ar(in, freq, bwr);
	Out.ar(outbus, (chain * gain));
}).load(s);

SynthDef(\efx_formlet_mn, { |outbus=21, inbus=20, freq=1000, atk=0.005, decay=0.005, gain=0|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = Formlet.ar(in, freq, atk, decay);
	Out.ar(outbus, (chain * gain));
}).load(s);

// SVF

SynthDef(\efx_bmoog_mn, { |outbus=21, inbus=20, freq=1000, qval=0.2, mode=0, gain=0|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = BMoog.ar(in, freq, qval, mode);
	Out.ar(outbus, (chain * gain));
}).load(s);

// MoogFF


// BORING FILTERS

SynthDef(\efx_lopass_mn, { |outbus=21, inbus=20, center=20000, gain=0|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = LPF.ar(in, center);
	Out.ar(outbus, (chain * gain));
}).load(s);

SynthDef(\efx_hipass_mn, { |outbus=21, inbus=20, center=40, gain=0|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = HPF.ar(in, center);
	Out.ar(outbus, (chain * gain));
}).load(s);

SynthDef(\efx_blowpass_mn, { |outbus=21, inbus=20, center=10000, rq=1, gain=0|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = BLowPass.ar(in, center, rq);
	Out.ar(outbus, (chain * gain));
}).load(s);

SynthDef(\efx_blowpass4_mn, { |outbus=21, inbus=20, center=10000, rq=1, gain=0|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = BLowPass4.ar(in, center, rq);
	Out.ar(outbus, (chain * gain));
}).load(s);

SynthDef(\efx_bhipass_mn, { |outbus=21, inbus=20, center=40, rq=1, gain=0|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = BHiPass.ar(in, center, rq);
	Out.ar(outbus, (chain * gain));
}).load(s);

SynthDef(\efx_bhipass4_mn, { |outbus=21, inbus=20, center=40, rq=1, gain=0|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = BHiPass4.ar(in, center, rq);
	Out.ar(outbus, (chain * gain));
}).load(s);

SynthDef(\efx_bpeakeq_mn, { |outbus=21, inbus=20, center=1000, rq=1, db=0, gain=0|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = BPeakEQ.ar(in, center, rq, db);
	Out.ar(outbus, (chain * gain));
}).load(s);

SynthDef(\efx_blowshelf_mn, { |outbus=21, inbus=20, center=10000, rs=1, db=0, gain=0|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = BLowShelf.ar(in, center, rs, db);
	Out.ar(outbus, (chain * gain));
}).load(s);

SynthDef(\efx_bhishelf_mn, { |outbus=21, inbus=20, center=40, rs=1, db=0, gain=0|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = BHiShelf.ar(in, center, rs, db);
	Out.ar(outbus, (chain * gain));
}).load(s);

SynthDef(\efx_bbandstop_mn, { |outbus=21, inbus=20, center=1000, bw=1, gain=0|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = BBandStop.ar(in, center, bw);
	Out.ar(outbus, (chain * gain));
}).load(s);

SynthDef(\efx_ballpass_mn, { |outbus=21, inbus=20, center=10000, rq=1, gain=0|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = BAllPass.ar(in, center, rq);
	Out.ar(outbus, (chain * gain));
}).load(s);

)










// Feedback?!,

// MembraneHexagon/Circle?, PV_RectComb|2, PV_SpectralEnhance, MonoGrain