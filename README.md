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
