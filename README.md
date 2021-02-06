# py-bode
Quick n dirty bode generator for Siglent scopes which lack the feature built-in. Currently AF only because that's all that's useful to me. Probably works on any recent scope from them (and others) that implement SCPI. My SDS1104X-U doesn't explicitly support it, but most instructions seem to work.

Requires network connection between scope and PC. May add support for serial later if I have time/can be bothered/anyone asks.

Also requires a sound card. For some loads, a headphone amp could be useful too.

# Installation

It's just a python script. Only tested on Linux, currently requires packages:
* subprocess
* numpy
* matplotlib
* simpleaudio
* time
* argparse

There is also an implicit dependency on having lxi-tools installed and on PATH.

Should work on any platform, but only tested on Linux.

# Options

`--address`: the IP address of the scope.

`--samples`: the number of logarithmically-spaced samples between 20Hz and 20kHz to take.

`--autoreset`: whether to re-set the scope between each frequency. Not happy with this; it's really slow to keep resetting the scope, but not resetting it can result in either clipping or running into the noise floor very quickly. TODO: set a configurable number of samples between resets.

`--debug`: Print additional debug messages to stdout.


# Usage

Assumes that channel 1 of the scope is connected to the reference, and channel 2 is connected to the output of the DUT. Stereo channels on the soundcard output must me used, one channel for the reference and one for driving the input to the DUT.

Some soundcards may have some non-obvious coupling inside, such that different loading on one channel can affect the output on the other. YMMV.

Response is calculated as the ratio of reference to DUT output. This means we're mostly independent of non-linearity in the response of the soundcard itself.

## Run timing

It takes about 5 seconds per measurement with autoreset disabled. About 10-15s per measurement with it enabled. Large numbers of samples take time. I'd like to speed things up e.g. use sweeps, but that makes synchronisation harder. Ideally, we just trigger the scope on the start of a sweep, capture the whole thing into scope memory, then download the envelopes. This isn't very general, however, as it requires that the scope have enough memory, and tests also shows problems with synchronisation between soundcard and scope.

## Self-test

This is still a TODO. Should be pretty easy to check that we're using the frequency we think we are: SCPI provides the means to access the frequency with which the trigger conditions are met. Therefore, we can output a known target frequency and check that the scope triggers at the right rate (assuming good trigger setup). Would help catch cases that the soundcard is internally processing at a sample rate that differs from that assumed when generating the test waveforms.

## Scope latency

For simplicity, we generate a longer test pulse than we need (20s), then just stop it early. This is lazy (and slow), but sidesteps the issue of introducing transients on loop and having to generate a variable-length loop for each frequency to ensure a nice match on loop. An especially slow scope when autosetting could exceed the implicit timeout on the test output (I have seen old/crap scopes take ages to autoset). The test pulse length can be trivially increased.
