import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('data/core-set/median_rent/sub-borougharea-medianrentstudiosand1-bedrooms2017.csv')

new_dict = {}

for index, row in df.iterrows():
	for years, rent in row[3:].iteritems():
		mini_dict = {}
		mini_dict['median_rent'] = rent
		new_dict[row[2] + ';' + years] = mini_dict

df = pd.DataFrame.from_dict(new_dict, orient = 'index')
tuples = [tuple(label.split(';')) for label in df.index]
mli = pd.MultiIndex.from_tuples(tuples)
df = pd.DataFrame(list(df.median_rent), index = mli)
