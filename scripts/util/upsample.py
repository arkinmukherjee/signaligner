import csv, json, math, sys

LABELS = {
    'wvote-1': 'sleep',
    'wvote-2': 'ambulation',
    'wvote-3': 'sedentary'
}



resultfile = sys.argv[1]
rate = int(sys.argv[2])



def rowtoweights(row):
    ret = {}
    for vote, label in LABELS.items():
        ret[label] = float(row[vote])
    return ret

def pick(weights):
    maxweight, maxlabel = None, None
    for label, weight in weights.items():
        if maxweight == None or weight >= maxweight:
            maxweight, maxlabel = weight, label
    return maxlabel

def printheader(order):
    for label in order:
        sys.stdout.write('%s,' % label)
    sys.stdout.write('label\n')

def printrow(order, weights):
    for label in order:
        sys.stdout.write('%5.3f,' % weights[label])
    sys.stdout.write(pick(weights) + '\n')



order = list(LABELS.values())

printheader(order)

with open(resultfile, 'rb') as csvfile:
    reader = csv.DictReader(csvfile)

    prevrow = None
    for row in reader:
        if prevrow == None:
            weights = rowtoweights(row)
            for ii in range(rate / 2):
                printrow(order, weights)
        else:
            weights0 = rowtoweights(prevrow)
            weights1 = rowtoweights(row)
            
            for ii in range(rate):
                t = float(ii + 1) / rate
                weights_interp = {}
                for label in order:
                    weights_interp[label] = (1 - t) * weights0[label] + t * weights1[label]
                printrow(order, weights_interp)
        prevrow = row

    weights = rowtoweights(prevrow)
    for ii in range(rate / 2):
        printrow(order, weights)
