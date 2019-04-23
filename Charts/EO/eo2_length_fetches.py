#!/bin/env python2
import plotly.plotly as py
import plotly.graph_objs as go

import re

# importing panda module
import pandas as pd

# csv file names
length_3 = "experiments_EO_length_3.csv"
length_4 = "experiments_EO_length_4.csv"
length_5 = "experiments_EO_length_5.csv"
length_6 = "experiments_EO_length_6.csv"
length_7 = "experiments_EO_length_7(100).csv"

eo2_length_3 = "experiments_EO2_length_3.csv"
eo2_length_4 = "experiments_EO2_length_4.csv"
eo2_length_5 = "experiments_EO2_length_5.csv"


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
        x=['3', '4', '5', '6', '7'],
        y=[average_fetches(length_3), average_fetches(length_4), average_fetches(
            length_5), average_fetches(length_6), average_fetches(length_7)],
        name='Proposed approach',
        marker=dict(
            color='rgb(55, 83, 109)'
        )
    )

    trace2 = go.Bar(
        x=['3', '4', '5', '6', '7'],
        y=[average_fetches(eo2_length_3), average_fetches(eo2_length_4), average_fetches(
            eo2_length_5), 5000, 20000],
        name='Baseline approach',
        marker=dict(
            color='rgb(255, 118, 100)'
        )
    )

    data = [trace1, trace2]

    layout = go.Layout(
        title='Equality operator',
        xaxis=dict(
            title='Query length',
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

    py.plot(fig, filename='eo2_length_fetches')


main()
