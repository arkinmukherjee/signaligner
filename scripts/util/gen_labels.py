import argparse, os, random, sys
import _root
import _helper

SAMPLE_RATE = 80
LABELS = set(['One', 'Two', 'Three'])
#LABELS = set(['Walking', 'Running', 'Standing', 'Biking', 'Sitting', 'Lying'])

parser = argparse.ArgumentParser(description='Generate random labels.')
parser.add_argument('length_minutes', type=int, help='Length of labels to generate, in minutes.')
parser.add_argument('session_count', type=int, help='Number of sessions to generate labels for.')
parser.add_argument('activity_lengths_str', type=str, help='Comma-separated list of activity lengths, in minutes.')
parser.add_argument('--algo', action='store_true', help='Output in algorithm format.')
args = parser.parse_args()



length_samples = args.length_minutes * 60 * SAMPLE_RATE

random.seed(123456789)

activity_lengths = []
for length in args.activity_lengths_str.split(','):
    spl = length.split(':')
    if len(spl) == 1:
        l = float(spl[0])
        c = 1
    elif len(spl) == 2:
        l = float(spl[0])
        c = int(spl[1])
    else:
        sys.stderr.write('length format error.\n')
        sys.exit(-1)

    for ii in range(c):
        activity_lengths.append(int(l * 60 * SAMPLE_RATE))



output = ''
label_count = 0

if args.algo:
    algo_start_ms = _helper.timeStringToTimeMillisecond('2000-01-01 09:30:05.500', _helper.DATE_FORMAT_YMD)
    output += 'START_TIME,STOP_TIME,PREDICTION\n'

for ss in range(args.session_count):
    if not args.algo:
        output += ('{"session": "R%03d", "source": "Random", "labels":[' % ss)

    sample = 0
    last_label = set()
    while True:
        label_length = activity_lengths[random.randint(0, len(activity_lengths) - 1)]
        label_end = min(length_samples, sample + label_length)

        label = random.sample(LABELS.difference(last_label), 1)[0]
        last_label = set([label])

        if not args.algo:
            output += _helper.activityJSON((sample, label_end, label), sample != 0)
        else:
            start_millisecond = int(sample * 1000 / SAMPLE_RATE) + algo_start_ms
            stop_millisecond = int(label_end * 1000 / SAMPLE_RATE) + algo_start_ms
            output += '%s,%s,%s\n' % (_helper.timeMillisecondToTimeString(start_millisecond), _helper.timeMillisecondToTimeString(stop_millisecond), label)

        sample += label_length
        label_count += 1

        if label_end >= length_samples:
            break

    if not args.algo:
        output += (']}\n')

sys.stdout.write(output)
sys.stderr.write('labels output: %d\n' % label_count)
