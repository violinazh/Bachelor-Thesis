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


def average_time(filename):
    array = []
    average = 0
    array_2 = []
    average_2 = 0
    csv = pd.read_csv(filename, delimiter="|")
    time_column = csv.Time
    for column in time_column:
        m = re.search('(\d+)', column)
        array.append(int(m.group(1)))

    average = sum(array) / len(array)

    time_column_2 = csv.Time_KNN
    for column in time_column_2:
        m = re.search('(\d+)', column)
        n = int(m.group(1))
        if n != 0:
            array_2.append(n)

    average_2 = sum(array_2) / len(array_2)

    return average - average_2


def average_time_baseline(filename):

    array = []
    average = 0
    array_2 = []
    average_2 = 0
    csv = pd.read_csv(filename, delimiter="|")
    time_column = csv.Time
    for column in time_column:
        m = re.search('(\d+)', column)
        array.append(int(m.group(1)))

    average = sum(array) / len(array)

    time_column_2 = csv.Time_KNN
    for column in time_column_2:
        m = re.search('(\d+)', column)
        n = int(m.group(1))
        if n != 0:
            array_2.append(n/1000000)

    average_2 = sum(array_2) / len(array_2)

    return average - average_2


def main():

    trace1 = go.Bar(
        x=['2 simple operands', '3 simple operands', '2 complex operands'],
        y=[average_time_baseline(simple_2_baseline), average_time_baseline(simple_3_baseline), average_time_baseline(
            complex_2_baseline)],
        name='Time',
        marker=dict(
            color='rgb(55, 83, 109)'
        )
    )

    trace2 = go.Bar(
        x=['2 simple operands', '3 simple operands', '2 complex operands'],
        y=[average_time(simple_2), average_time(simple_3), average_time(
            complex_2)],
        name='Time Baseline',
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
            title='Processing time (ms)',
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

    py.plot(fig, filename='or_time')


main()
