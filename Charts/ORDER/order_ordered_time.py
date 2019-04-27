#!/bin/env python2
import plotly.plotly as py
import plotly.graph_objs as go

import re

# importing panda module
import pandas as pd

# csv file names
ordered_0 = "experiments_ORDER_ordered_0.csv"
ordered_1 = "experiments_ORDER_ordered_1.csv"
ordered_2 = "experiments_ORDER_ordered_2.csv"
ordered_3 = "experiments_ORDER_ordered_3.csv"
ordered_4 = "experiments_ORDER_ordered_4.csv"
ordered_5 = "experiments_ORDER_ordered_5.csv"

baseline_0 = "experiments_ORDER_baseline_ordered_0.csv"
baseline_1 = "experiments_ORDER_baseline_ordered_1.csv"
baseline_2 = "experiments_ORDER_baseline_ordered_2.csv"
baseline_3 = "experiments_ORDER_baseline_ordered_3.csv"
baseline_4 = "experiments_ORDER_baseline_ordered_4.csv"
baseline_5 = "experiments_ORDER_baseline_ordered_5.csv"


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


def average_baseline(filename):
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
        x=['0', '1', '2', '3'],
        y=[average_time(ordered_0), average_time(ordered_1), average_time(
            ordered_2), average_time(ordered_3)],
        name='Total time',
        marker=dict(
            color='rgb(55, 83, 109)'
        )
    )

    trace2 = go.Bar(
        x=['0', '1', '2', '3'],
        y=[average_baseline(baseline_0), average_baseline(baseline_1), average_baseline(
            baseline_2), average_baseline(baseline_3)],
        name='Total time Baseline',
        marker=dict(
            color='rgb(255, 118, 100)'
        )
    )

    data = [trace1, trace2]

    layout = go.Layout(
        title='Order operator',
        xaxis=dict(
            title='Number of fixed positions',
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

    py.plot(fig, filename='order_ordered_time')


main()
