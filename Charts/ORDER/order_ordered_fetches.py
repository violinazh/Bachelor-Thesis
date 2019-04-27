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


def average_fetches(filename):
    array = []
    average = 0

    csv = pd.read_csv(filename, delimiter="|")
    time_column = csv.Heap_fetches
    for column in time_column:
        m = re.search('(\d+)', column)
        n = int(m.group(1))
        if n != 0:
            array.append(n)

    average = sum(array) / len(array)

    return average


def main():

    trace1 = go.Bar(
        x=['0', '1', '2', '3'],
        y=[average_fetches(ordered_0), average_fetches(ordered_1), average_fetches(
            ordered_2), average_fetches(ordered_3)],
        name='Heap fetches',
        marker=dict(
            color='rgb(55, 83, 109)'
        )
    )

    trace2 = go.Bar(
        x=['0', '1', '2', '3'],
        y=[average_fetches(baseline_0), average_fetches(baseline_1), average_fetches(
            baseline_2), average_fetches(baseline_3)],
        name='Heap fetches Baseline',
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
            title='Heap fetches',
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

    py.plot(fig, filename='order_ordered_fetches')


main()
