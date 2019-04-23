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


def average_pne(filename):
    array = []
    average = 0
    csv = pd.read_csv(filename, delimiter="|")

    time_column = csv.Time_PNE
    for column in time_column:
        m = re.search('(\d+)', column)
        array.append(int(m.group(1)))

    average = sum(array) / len(array)

    return average


def main():

    trace1 = go.Bar(
        x=['3', '4', '5', '6', '7'],
        y=[average_time(length_3), average_time(length_4), average_time(
            length_5), average_time(length_6), average_time(length_7)],
        name='Total time',
        marker=dict(
            color='rgb(55, 83, 109)'
        )
    )

    trace2 = go.Bar(
        x=['3', '4', '5', '6', '7'],
        y=[average_pne(length_3), average_pne(length_4), average_pne(
            length_5), average_pne(length_6), average_pne(length_7)],
        name='PNE time',
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

    py.plot(fig, filename='eo_length_time')


main()
