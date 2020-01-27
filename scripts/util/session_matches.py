import json, math, sys

if len(sys.argv) != 2:
    print('usage: %s [playlog]' % sys.argv[0])
    print('  Takes a playlog and prints a csv of match info.')
    sys.exit(-1)

playlogfile = sys.argv[1]



LEVEL_FIRST = 'tut_label'
LEVEL_NEXT = {
    'tut_label':['tut_splitthree'],
    'tut_splitthree':['tut_intervals_one'],
    'tut_intervals_one':['tut_intervals_two'],
    'tut_intervals_two':['LV_00', 'LV_01', 'LV_02', 'LV_03', 'LV_04', 'LV_05', 'LV_06'],
    'LV_00':[],
    'LV_01':[],
    'LV_02':[],
    'LV_03':[],
    'LV_04':[],
    'LV_05':[],
    'LV_06':[]
}



print(','.join(['Timestamp', 'Player ID', 'Level', 'Score']))

sessions = {}
sessions_times = {}
sessions_completed = set()
sessions_lost = set()

with open(playlogfile, 'rb') as playlog:
    for line in playlog:
        event = json.loads(line)

        event_type = event['type']
        event_session = event['session']
        event_time = event['time']
        event_level = event['level']

        if event_session in ['EHWEAFBVRO']:
            continue

        if not event_level in list(LEVEL_NEXT.keys()):
            raise RuntimeError('unrecognized level "' + event_level + '".')

        if event_session not in sessions:
            if event_level != LEVEL_FIRST:
                raise RuntimeError('session not starting in first level.')
                
            sessions[event_session] = event_level

        if event_level == sessions[event_session]:
            pass
        elif event_level in LEVEL_NEXT[sessions[event_session]]:
            # player must have completed previous level to get to the one they are on
            if (event_session, sessions[event_session]) not in sessions_completed:
                sessions_completed.add((event_session, sessions[event_session]))
                if (event_session, sessions[event_session]) in sessions_lost:
                    print(','.join([str(event_time - 1), event_session, sessions[event_session], '0.5']))
                else:
                    print(','.join([str(event_time - 1), event_session, sessions[event_session], '1']))
        else:
            raise RuntimeError('went back or skipped a level.')

        sessions[event_session] = event_level
        sessions_times[event_session] = event_time

        if event_type == 'check':
            if event['data']['errs']:
                sessions_lost.add((event_session, event_level))
                #print ','.join([str(event_time), event_session, event_level, '0'])
                pass
            else:
                if (event_session, event_level) in sessions_completed:
                    raise RuntimeError('level completed twice.')
                sessions_completed.add((event_session, event_level))
                if (event_session, event_level) in sessions_lost:
                    print(','.join([str(event_time), event_session, event_level, '0.5']))
                else:
                    print(','.join([str(event_time), event_session, event_level, '1']))

# if the player didn't finish the level they are on, they lost it
for session, level in sessions.items():
    if (session, level) not in sessions_completed:
        print(','.join([str(sessions_times[session] + 1), session, level, '0']))
