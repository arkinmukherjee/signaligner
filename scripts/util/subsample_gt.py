import csv, gzip, math, os, sys

subsample = int(sys.argv[1]) # 80 * 5 = 400; * 24 = 9600
filename = sys.argv[2]

LABELS = ['sleep', 'ambulation', 'sedentary']

def most_frequent(l):
    return max(set(l), key=l.count)

if filename.endswith('.gz'):
    use_open = gzip.open
else:
    use_open = open

print('ground-truth-label,ground-truth-win,ground-truth-1,ground-truth-2,ground-truth-3')

def printrow(smp):
    print('%s,%d,%0.3f,%0.3f,%0.3f' % (most_frequent(smp), LABELS.index(most_frequent(smp)) + 1, smp.count('sleep') / float(len(smp)), smp.count('ambulation') / float(len(smp)), smp.count('sedentary') / float(len(smp))))

sample = []
with use_open(filename, 'rb') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        GT = row['GROUND_TRUTH']
        if GT not in LABELS:
            raise RuntimeError('error')

        sample.append(GT)

        if len(sample) == subsample:
            printrow(sample)
            sample = []

if len(sample) != 0:
    printrow(sample)
    sample = []
