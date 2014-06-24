(
SynthDef(\efx_partialsynth_mn, {|outbus=21, inbus=20, pcut=0.1|
	var chain, in = In.ar(inbus, 1);
	chain = FFT(LocalBuf.new(2048, 1), in);
	// Upper limit should be Nyqust / nBins , e.g. 22050 / 2048 -> 21.532
	// or + and - 21.532
	chain = PV_PartialSynthF(chain, pcut*21.532, 3, 0);
	chain = IFFT(chain);
	Out.ar(outbus, chain);
}).load(s);

SynthDef(\efx_magsmear_mn, { |outbus=21, inbus=20, bins=100|
	var in, chain;
	in = In.ar(inbus, 1);
	chain = FFT(LocalBuf(2048,1), in);
	chain = PV_MagSmear(chain, bins);
	Out.ar(outbus, IFFT(chain));
}).send(s);

SynthDef(\efx_clipdist_mn, { |outbus=21, inbus=20, mult=1.0, clip=1.0|
	Out.ar(outbus, (In.ar(inbus, 1) * mult).clip2(clip));
}).load(s);

SynthDef(\efx_clipdist_st, { |outbus=21, inbus=20, mult=1.0, clip=1.0|
	Out.ar(outbus, (In.ar(inbus, 2) * mult).clip2(clip));
}).load(s);

SynthDef(\efx_thru_mn, { |outbus=21, inbus=20|
	Out.ar(outbus, In.ar(inbus, 1));
}).load(s);

SynthDef(\efx_thru_st, { |outbus=21, inbus=20|
	Out.ar(outbus, In.ar(inbus, 2));
}).load(s);
)