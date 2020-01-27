import csv, sys

sys.path = ['/Library/Python/2.7/site-packages'] + sys.path
from plotly import tools
import plotly.offline as py
import plotly.graph_objs as go

inputfile = sys.argv[1]

sample = []
data = {}

with open(inputfile, 'rb') as csvfile:
    reader = csv.DictReader(csvfile)
    
    for row in reader:
        sample.append(len(sample) + 1)

        for k, v in row.items():
            if k not in data:
                data[k] = []
            try:
                data[k].append(float(v))
            except:
                pass

pax = go.Scatter(x=sample, y=data['x'], mode='lines', name='x', marker={'color':'rgb(255,0,0)'})
pay = go.Scatter(x=sample, y=data['y'], mode='lines', name='y', marker={'color':'rgb(0,255,0)'})
paz = go.Scatter(x=sample, y=data['z'], mode='lines', name='z', marker={'color':'rgb(0,0,255)'})

plslp = go.Scatter(x=sample, y=data['wvote-1'], name='sleep', marker={'color':'rgb(0,192,192)'})
plsed = go.Scatter(x=sample, y=data['wvote-3'], name='sedentary', marker={'color':'rgb(192,0,192)'})
plamb = go.Scatter(x=sample, y=data['wvote-2'], name='ambulation', marker={'color':'rgb(192,192,0)'})

pvoted = go.Scatter(x=sample, y=data['vote-count'], name='votes', marker={'color':'rgb(32,32,32)'})
pcount = go.Scatter(x=sample, y=data['sessions'], name='sessions', marker={'color':'rgb(128,128,128)'})

fig1 = go.Figure(data=[pax, pay, paz])
fig2 = go.Figure(data=[plslp, plsed, plamb])
fig3 = go.Figure(data=[pcount, pvoted])
rows = 3

has_gt = False
if 'ground-truth-1' in data and 'ground-truth-2' in data and 'ground-truth-3' in data:
    has_gt = True

if has_gt:
    pgslp = go.Scatter(x=sample, y=data['ground-truth-1'], name='gt-sleep', marker={'color':'rgb(0,192,192)'})
    pgsed = go.Scatter(x=sample, y=data['ground-truth-3'], name='gt-sedentary', marker={'color':'rgb(192,0,192)'})
    pgamb = go.Scatter(x=sample, y=data['ground-truth-2'], name='gt-ambulation', marker={'color':'rgb(192,192,0)'})

    figg = go.Figure(data=[pgslp, pgsed, pgamb])
    rows = 4

fig = tools.make_subplots(rows=rows, cols=1, shared_xaxes=True)
row = 0

row += 1
fig.append_trace(pax, row, 1)
fig.append_trace(pay, row, 1)
fig.append_trace(paz, row, 1)

row += 1
fig.append_trace(plslp, row, 1)
fig.append_trace(plsed, row, 1)
fig.append_trace(plamb, row, 1)

if has_gt:
    row += 1
    fig.append_trace(pgslp, row, 1)
    fig.append_trace(pgsed, row, 1)
    fig.append_trace(pgamb, row, 1)

row += 1
fig.append_trace(pcount, row, 1)
fig.append_trace(pvoted, row, 1)

py.plot(fig, filename=inputfile.replace('.csv', '.html'))
