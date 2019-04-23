import plotly.plotly as py
import plotly.graph_objs as go

import re

# importing panda module
import pandas as pd

# csv file name
filename = "experiments_EO2.csv"

array = []
average = 0


def main():
    csv = pd.read_csv(filename, delimiter="|")
    time_column = csv.Time
    for column in time_column:
        m = re.search('(\d+)', column)
        array.append(int(m.group(1)))

    average = sum(array) / len(array)
    print(average)

    data = [go.Bar(
        x=['Queries with length 5'],
        y=[average])]
    py.plot(data, filename='test')


main()
