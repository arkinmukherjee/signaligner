import json, math, sys

if len(sys.argv) < 3 or len(sys.argv) > 4:
    print('usage: %s [playlog] [level name] <signal index>' % sys.argv[0])
    print('  Takes a playlog, a level name, and optionally an index of a signal.')
    print('  Prints a csv of info about sample votes.')
    print('  If signal index is given, only prints for the given signal.')
    sys.exit(-1)

playlogfile = sys.argv[1]
levelname = sys.argv[2]
if len(sys.argv) > 3:
    only_signal = int(sys.argv[3])
else:
    only_signal = None



POSSIBLE_LABELS = 3
IGNORE_ANY_ERRORS = True



levelfile = 'levels/' + levelname + '.js'

check_events = []
with open(playlogfile, 'rb') as playlog:
    for line in playlog:
        event = json.loads(line)
        if event['type'] == 'check' and event['level'] == levelname:
            check_events.append(event)

with open(levelfile, 'rb') as level:
    levelstring = level.read().replace('let CONFIG =', '')
    levelconfig = json.loads(levelstring)
    leveldata = levelconfig['data']

levelheaders = []
levelheaders.append('x')
levelheaders.append('y')
levelheaders.append('z')
levelheaders.append('check-gt')

levelheaders.append('vote-count')
levelheaders.append('vote-weight')
levelheaders.append('wvote-win')
for ll in range(POSSIBLE_LABELS):
    levelheaders.append('wvote-' + str(ll + 1))

start_labels = -1
for ss in range(len(leveldata)):
    for ii in range(len(leveldata[ss])):
        start_labels = len(leveldata[ss][ii])

        # average max/min for signal xyz itself
        leveldata[ss][ii][0] = 0.5 * (leveldata[ss][ii][0][0] + leveldata[ss][ii][0][1])
        leveldata[ss][ii][1] = 0.5 * (leveldata[ss][ii][1][0] + leveldata[ss][ii][1][1])
        leveldata[ss][ii][2] = 0.5 * (leveldata[ss][ii][2][0] + leveldata[ss][ii][2][1])

        leveldata[ss][ii].append(0)
        leveldata[ss][ii].append(0)
        leveldata[ss][ii].append(0)
        for ll in range(POSSIBLE_LABELS):
            leveldata[ss][ii].append(0)

votes_count = start_labels
votes_weight = votes_count + 1
votes_pick = votes_weight + 1
start_labels = votes_pick + 1

def argmax(l):
    ret = 0
    for ii in range(len(l)):
        if l[ii] >= l[ret]:
            ret = ii
    return ret

sessions = set()
for check_event in check_events:
    sessions.add(check_event['session'])
    errs = check_event['data']['errs']

    if IGNORE_ANY_ERRORS and errs:
        continue

    for ss in range(len(leveldata)):
        blocks = check_event['data']['blocks'][ss]
        votes = check_event['data']['blockVotes'][ss]
        
        sofar = 0.0
        max_index = 0
        for block, vote in zip(blocks, votes):
            size = block["size"]

            if len(vote) != 1:
                raise RuntimeError('more than one vote for block')

            weight = 1.0

            for xx in range(int(size + 0.5)):
                cur_index = int(sofar + xx)
                max_index = max(max_index, cur_index)

                if cur_index >= len(leveldata[ss]):
                    raise RuntimeError('sample index out of bounds')

                leveldata[ss][cur_index][votes_count] += 1
                for vv in vote:
                    leveldata[ss][cur_index][votes_weight] += weight
                    leveldata[ss][cur_index][start_labels + (vv - 1)] += weight

            sofar += size

        if max_index + 1 != len(leveldata[ss]):
            raise RuntimeError('not enough sample indices')

for ss in range(len(leveldata)):
    for ii in range(len(leveldata[ss])):
        if leveldata[ss][ii][votes_weight] > 0:
            for ll in range(POSSIBLE_LABELS):
                leveldata[ss][ii][start_labels + ll] /= float(leveldata[ss][ii][votes_weight])
        leveldata[ss][ii][votes_pick] = 1 + argmax(leveldata[ss][ii][start_labels:start_labels+POSSIBLE_LABELS])

out = ''
for hh in levelheaders:
    out += (hh + ',')
out += 'sessions'
print(out)

for ss in range(len(leveldata)):
    if only_signal != None:
        if ss != only_signal:
            continue

    for ii in range(len(leveldata[ss])):
        pt = leveldata[ss][ii]
        out = ''
        for pp in pt:
            if type(pp) == type(0):
                out += '%d,' % pp
            else:
                out += '%0.3f,' % pp
        out += '%d' % len(sessions)
        print(out)

    #if ss + 1 != len(leveldata):
    #    for ii in xrange(10):
    #        print
