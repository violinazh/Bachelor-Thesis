import plotly.plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as FF

import re

import pandas as pd
import numpy as np

# csv file name
filename = "experiments_NEO_distance_1.csv"

array = []
average = 0


def main():
    csv = pd.read_csv(filename, delimiter="|")
    time_column = csv.Heap_fetches
    for column in time_column:
        m = re.search('(\d+)', column)
        array.append(int(m.group(1)))

    average = sum(array) / len(array)
    print(average)

    trace = go.Scatter(x=np.arange(
        1000), y=csv['Heap_fetches'], name='Heap fetches')
    layout = go.Layout(title='Distance 1 distribution',
                       plot_bgcolor='rgb(230, 230,230)',
                       showlegend=True)
    fig = go.Figure(data=[trace], layout=layout)

    py.iplot(fig, filename='test')


main()
