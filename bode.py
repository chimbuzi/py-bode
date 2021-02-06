import subprocess
import numpy as np
import matplotlib.pyplot as plt
import simpleaudio as sa
import time
import argparse


parser = argparse.ArgumentParser(description='Generate a bode plot')
parser.add_argument('--address', '-a', type=str, help='IP address of scope')
parser.add_argument('--samples', '-s', type=int, help='Number of frequencies to test (logspaced from 20Hz to 20kHz)')
parser.add_argument('--debug', '-d', dest='debug', action='store_true', help='Print additional debug information')
parser.add_argument('--autoreset', dest='autoreset', action='store_true', help='Reset scope before each measurement')
parser.set_defaults(autoreset=False)
parser.set_defaults(debug=False)
args = parser.parse_args()


scope_address = args.address


def debug_print(output_str):
    if args.debug:
        print(output_str)


def scpi_command(command):
    return subprocess.check_output(['lxi', 'scpi', '--address', f'{scope_address}', f'{command}'])


def get_amplitude(channel):
    return_val = str(scpi_command(f'C{channel}:PAVA? AMPL')).rstrip()
    amplitude = return_val.split(',')[-1][0:-2].split('E') # e.g. C1:PAVA AMPL,3.020000E-01V -> [3.020000, -01]
    debug_print(f'Raw amplitude: {amplitude}')
    return (float(amplitude[0]) * (10 ** int(amplitude[1][0:3])))

    
def autoset():
    debug_print(f'Setting scope...')
    scpi_command('ASET')


def play_sine(frequency):
    sample_rate = 44100 #hz
    volume = 1 # between 0 and 1
    debug_print(f'Started generating sine at {frequency}Hz')
    startgen = time.time()
    timeseries = np.linspace(0, 100, 20 * sample_rate, False)
    sine_signal = np.sin(frequency * timeseries * 2 * np.pi)
    audio = np.hstack((sine_signal))
    audio *= 32767/np.max(np.abs(audio))
    audio = audio.astype(np.int16)
    debug_print(f'Generated sine at {frequency}Hz in {time.time() - startgen}s, starting output...')
    play_obj = sa.play_buffer(audio, 1, 2, sample_rate)
    return play_obj


def run_bode(samples):
    startanalysis = time.time()
    response = []
    freqs = np.geomspace(20, 20000, num=samples)
    ix = 0
    
    for freq in freqs:
        startfreq = time.time()
        debug_print(f'Testing frequency {ix + 1} of {samples}')
        play_obj = play_sine(freq)
        debug_print(f'Started outputting sine at {freq}Hz')
        #wait a second to allow play latency and let scope trigger
        time.sleep(1)
        if not ix:
            autoset()
            time.sleep(5) # takes a while to set
        elif args.autoreset:
            debug_print(f'Resetting scope because args.autoreset={args.autoreset}')
            autoset()
            time.sleep(5)
        debug_print('Getting data from scope...')
        dry = get_amplitude(1)
        debug_print(f'Dry amplitude: {dry}')
        wet = get_amplitude(2)
        debug_print(f'Wet amplitude: {wet}')
        print(f'Frequency: {round(freq, 3)}Hz, Dry: {round(dry, 3)}V, Wet: {round(wet, 3)}V')
        response.append(wet/dry)
        play_obj.stop()
        debug_print(f'Stopped output at {freq}Hz')
        debug_print(f'Finished testing frequency {freq}Hz in {time.time() - startfreq}s')
        ix += 1
        
    print(f'Completed analysis in {time.time() - startanalysis}s')
    # generate a plot of the response
    plt.plot(freqs, response)
    plt.ylabel('Relative response')
    plt.xlabel('Frequency / Hz')
    plt.xscale('log')
    plt.show()


if __name__ == '__main__':
    run_bode (args.samples)
