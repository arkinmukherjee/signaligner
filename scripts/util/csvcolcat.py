import sys

if len(sys.argv) != 3:
    print('usage: %s [csvfile1] [csvfile2]' % sys.argv[0])
    print('  Concatenates the columns of csvfile2 onto the end of the columns of csvfile1.')
    sys.exit(-1)



f1 = open(sys.argv[1]).readlines()
f2 = open(sys.argv[2]).readlines()

if len(f1) != len(f2):
    raise RuntimeError('not the same number of lines')

for l1, l2 in zip(f1, f2):
    print('%s,%s' % (l1.strip('\r\n'), l2.strip('\r\n')))
