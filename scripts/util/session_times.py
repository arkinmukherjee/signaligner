import json, math, sys

if len(sys.argv) != 2:
    print('usage: %s [playlog]' % sys.argv[0])
    print('  Takes a playlog and prints a csv of session time and level info.')
    sys.exit(-1)

playlogfile = sys.argv[1]



LEVELS = [
    'tut_label',
    'tut_splitthree',
    'tut_intervals_one',
    'tut_intervals_two',
    'LV_00',
    'LV_01',
    'LV_02',
    'LV_03',
    'LV_04',
    'LV_05',
    'LV_06'
]

LEVEL_ORDER = {
    'tut_label':1,
    'tut_splitthree':2,
    'tut_intervals_one':3,
    'tut_intervals_two':4,
    'LV_00':5,
    'LV_01':5,
    'LV_02':5,
    'LV_03':5,
    'LV_04':5,
    'LV_05':5,
    'LV_06':5
}



sessions = {}
with open(playlogfile, 'rb') as playlog:
    for line in playlog:
        event = json.loads(line)

        event_level = event['level']
        if not event_level in LEVELS:
            raise RuntimeError('unrecognized level "' + event['level'] + '".')

        session = event['session']
        ts = float(event['time'])
        if session not in sessions:
            sessions[session] = {
                'times': [],
                'count_attempted': set(),
                'count_completed': set(),
                'max_attempted': 0,
                'max_completed': 0
                }
            for level in LEVELS:
                sessions[session]['times-' + level] = []

        ord = LEVEL_ORDER[event_level]

        sessions[session]['count_attempted'].add(event['level'])
        if event['type'] == 'check':
            if event['data']['errs'] == False:
                sessions[session]['count_completed'].add(event['level'])

        sessions[session]['max_attempted'] = max(sessions[session]['max_attempted'], ord)
        sessions[session]['max_completed'] = max(sessions[session]['max_completed'], ord - 1)
        if event['type'] == 'check':
            if event['data']['errs'] == False:
                sessions[session]['max_completed'] = max(sessions[session]['max_completed'], ord)

        sessions[session]['times'].append(ts)
        sessions[session]['times-' + event_level].append(ts)

sys.stdout.write('%s,%s,%s,%s,%s,%s' % ('session', 'count_attempted', 'count_completed', 'max_attempted', 'max_completed', 'seconds-total'))
for level in LEVELS:
    sys.stdout.write(',%s' % ('seconds-' + level))
sys.stdout.write('\n')

for session, info in sessions.items():
    count_attempted = len(info['count_attempted'])
    count_completed = len(info['count_completed'])

    max_attempted = info['max_attempted']
    max_completed = info['max_completed']

    seconds = (max(info['times']) - min(info['times'])) / 1000.0

    sys.stdout.write('%s,%d,%d,%d,%d,%0.1f' % (session, count_attempted, count_completed, max_attempted, max_completed, seconds))
    for level in LEVELS:
        times = info['times-' + level]
        if len(times) == 0:
            sys.stdout.write(',')
        else:
            seconds = (max(times) - min(times)) / 1000.0
            sys.stdout.write(',%0.1f' % seconds)
    sys.stdout.write('\n')
