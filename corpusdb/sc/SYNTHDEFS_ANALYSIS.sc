// Quarks.gui


SynthDef(\bus_analyzer_power_mfcc13_mn_nrt, { |inbus=20, savebufNum=0, hop=0.04|
	var in, chain, power, mfccs, driver;
	in = In.ar(inbus, 1);
	chain = FFT(LocalBuf(8192,1), in);

	power =			FFTPower.kr(chain);
	mfccs =			MFCC.kr(chain, numcoeff:13); // or 13|24|42...

	// log the metadata into a buffer and signal sclang to read from the buffer
	driver = Impulse.kr( 1 / hop );
	Logger.kr([power, mfccs].flatten, driver, savebufNum);
	Out.ar(0, in);
}).load(s);

SynthDef(\bus_analyzer_power_mfcc24_mn_nrt, { |inbus=20, savebufNum=0, hop=0.04|
	var in, chain, power, mfccs, driver;
	in = In.ar(inbus, 1);
	chain = FFT(LocalBuf(8192,1), in);

	power =			FFTPower.kr(chain);
	mfccs =			MFCC.kr(chain, numcoeff:24); // or 13|24|42...

	// log the metadata into a buffer and signal sclang to read from the buffer
	driver = Impulse.kr( 1 / hop );
	Logger.kr([power, mfccs].flatten, driver, savebufNum);
	Out.ar(0, in);
}).load(s);

SynthDef(\bus_analyzer_power_mfcc42_mn_nrt, { |inbus=20, savebufNum=0, hop=0.04|
	var in, chain, power, mfccs, driver;
	in = In.ar(inbus, 1);
	chain = FFT(LocalBuf(8192,1), in);

	power =			FFTPower.kr(chain);
	mfccs =			MFCC.kr(chain, numcoeff:42); // or 13|24|42...

	// log the metadata into a buffer and signal sclang to read from the buffer
	driver = Impulse.kr( 1 / hop );
	Logger.kr([power, mfccs].flatten, driver, savebufNum);
	Out.ar(0, in);
}).load(s);


SynthDef(\bus_analyzer_power_chroma12_mn_nrt, { |inbus=20, savebufNum=0, hop=0.04|
	var in, chain, power, chromas, driver;
	in = In.ar(inbus, 1);
	chain = FFT(LocalBuf(8192,1), in);

	power =			FFTPower.kr(chain);
	chromas =		Chromagram.kr(chain, 8192, 12); // semitones

	// log the metadata into a buffer and signal sclang to read from the buffer
	driver = Impulse.kr( 1 / hop );
	Logger.kr([power, chromas].flatten, driver, savebufNum);
	Out.ar(0, in);
}).load(s);

SynthDef(\bus_analyzer_power_mfcc13_chroma12_mn_nrt, { |inbus=20, savebufNum=0, hop=0.04|
	var in, chain, powers, mfccs, chromas, driver;
	in = In.ar(inbus, 1);
	chain = FFT(LocalBuf(8192,1), in);

	powers =		FFTPower.kr(chain);
	mfccs =			MFCC.kr(chain, numcoeff:13); // or 13|24|42...
	chromas =		Chromagram.kr(chain, 8192, 12); // semitones

	// log the metadata into a buffer and signal sclang to read from the buffer
	driver = Impulse.kr( 1 / hop );
	Logger.kr([powers, mfccs, chromas].flatten, driver, savebufNum);
	Out.ar(0, in);
}).load(s);

SynthDef(\bus_analyzer_power_mn_nrt, { |inbus=20, savebufNum=0, hop=0.04|
	var in, chain, powers, driver;
	in = In.ar(inbus, 1);
	chain = FFT(LocalBuf(8192,1), in);

	powers =		FFTPower.kr(chain);

	// log the metadata into a buffer and signal sclang to read from the buffer
	driver = Impulse.kr( 1 / hop );
	Logger.kr([powers].flatten, driver, savebufNum);
	Out.ar(0, in);
}).load(s);

