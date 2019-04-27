#!/bin/env python2
import plotly.plotly as py
import plotly.graph_objs as go

import re

# importing panda module
import pandas as pd

# csv file names
distance_0 = "experiments_NEO_distance_0.csv"
distance_1 = "experiments_NEO_distance_1.csv"
distance_2 = "experiments_NEO_distance_2.csv"
distance_3 = "experiments_NEO_distance_3.csv"


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
        y=[average_fetches(distance_0), average_fetches(distance_1), average_fetches(distance_2), average_fetches(
            distance_3)],
        name='Total time',
        marker=dict(
            color='rgb(55, 83, 109)'
        )
    )

    data = [trace1]

    layout = go.Layout(
        title='Not-equality operator',
        xaxis=dict(
            title='Distance between equality indices',
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

    py.plot(fig, filename='neo_distance_fetches')


main()
