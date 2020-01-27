import argparse, math, os, sys
import _root
import _helper

START_DATE = '1/1/2000'
START_TIME = '09:30:05.500'
SAMPLE_RATE = 80

DEFAULT_MAGNITUDE = 1

parser = argparse.ArgumentParser(description='Generate a signal based on sine waves.')
parser.add_argument('length_minutes', type=int, help='Length of data to generate, in minutes.')
parser.add_argument('period_minutes', type=int, help='Period of data to generate, in minutes.')
parser.add_argument('--mag', type=int, help='Magnitude of signal (default %d).' % DEFAULT_MAGNITUDE, default=DEFAULT_MAGNITUDE)
args = parser.parse_args()

print('------------ Generated ActiGraph data date format M/d/yyyy at %d Hz  -----------' % SAMPLE_RATE)
print('Start Time %s' % START_TIME)
print('Start Date %s' % START_DATE)
print('--------------------------------------------------')

print('Accelerometer X,Accelerometer Y,Accelerometer Z')
for ss in range(args.length_minutes * 60):
    for ii in range(SAMPLE_RATE):
        ts = ss + ii / float(SAMPLE_RATE)
        offset = 0.01 * math.sin(2.0 * math.pi * ts)
        xx = args.mag * (0.99 * math.sin(1.0 * 2.0 * math.pi * ts / (args.period_minutes * 60)) + 1.0 * offset)
        yy = args.mag * (0.59 * math.sin(2.0 * 2.0 * math.pi * ts / (args.period_minutes * 60)) + 2.0 * offset)
        zz = args.mag * (0.19 * math.sin(4.0 * 2.0 * math.pi * ts / (args.period_minutes * 60)) + 4.0 * offset)
        print('%0.3f,%0.3f,%0.3f' % (xx, yy, zz))
