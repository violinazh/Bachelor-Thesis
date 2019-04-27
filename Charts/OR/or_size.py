#!/bin/env python2
import plotly.plotly as py
import plotly.graph_objs as go

import re

# importing panda module
import pandas as pd

# csv file names
simple_2 = "experiments_OR_simple_2.csv"
simple_3 = "experiments_OR_simple_3.csv"
complex_2 = "experiments_OR_complex_2.csv"

simple_2_baseline = "experiments_OR_simple_2_baseline.csv"
simple_3_baseline = "experiments_OR_simple_3_baseline.csv"
complex_2_baseline = "experiments_OR_complex_2_baseline.csv"


def average_size(filename):
    array = []
    average = 0

    csv = pd.read_csv(filename, delimiter="|")
    time_column = csv.Heap_max_size
    for column in time_column:
        m = re.search('(\d+)', column)
        n = int(m.group(1))
        if n != 0:
            array.append(n)

    average = sum(array) / len(array)

    return average


def main():

    trace1 = go.Bar(
        x=['2 simple operands', '3 simple operands', '2 complex operands'],
        y=[average_size(simple_2), average_size(simple_3), average_size(
            complex_2)],
        name='Heap size',
        marker=dict(
            color='rgb(55, 83, 109)'
        )
    )

    trace2 = go.Bar(
        x=['2 simple operands', '3 simple operands', '2 complex operands'],
        y=[average_size(simple_2_baseline), average_size(simple_3_baseline), average_size(
            complex_2_baseline)],
        name='Heap size Baseline',
        marker=dict(
            color='rgb(255, 118, 100)'
        )
    )

    data = [trace1, trace2]

    layout = go.Layout(
        title='Or operator',
        xaxis=dict(
            title='Or sequence',
            tickfont=dict(
              size=14,
              color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title='Heap size',
            titlefont=dict(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0
    )

    fig = go.Figure(data=data, layout=layout)

    py.plot(fig, filename='or_size')


main()
