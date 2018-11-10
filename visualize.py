import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def get_mlidf(path): 
	'''Loads a multi-level indexed dataframe from path'''
	df = pd.read_csv(path)
	new_dict = {}
	data_name = df.iloc[0,0]

	for index, row in df.iterrows():
		for year, data_pt in row[3:].iteritems():
			mini_dict = {}
			mini_dict[data_name] = data_pt
			try:
				int(year)
			except ValueError:
				year = int( np.mean( [int(y) for y in year.split('-')] ) )
				year = str(year)
			new_dict[row[2] + ';' + year] = mini_dict

	df = pd.DataFrame.from_dict(new_dict, orient = 'index')
	tuples = [tuple(label.split(';')) for label in df.index]
	mli = pd.MultiIndex.from_tuples(tuples, names = ['subborough', 'year'])
	df = pd.DataFrame(list(df[data_name]), columns = [data_name], index = mli)

	return df

def add_col(df, path):
	'''Returns df with added column from path'''
	df2 = get_mlidf(path)
	return df.join(df2)

def get_percentile_column(df, colname):
	'''Returns a column of the percentile ranking of each datapoint within its year
		example: df['rent_percentile'] = get_percentile_column(df, 'rent') '''
	years = {}

	for index, row in df.iterrows():
		if years.get(index[1]):
			years[index[1]].append(row[colname])
		else:
			years[index[1]] = []
			years[index[1]].append(row[colname])
	rp = []
	from scipy.stats import percentileofscore
	for index, row in df.iterrows():
		year = index[1]
		rp.append(percentileofscore(years[year], row[colname]))
	return rp

def get_gentrifying_sbs(df, cutoff = 5):
	'''Return a list of the gentrified subboroughs given a certain cutoff for percentile growth'''
	gentrified = []
	for sb in set(df.index.get_level_values('subborough')):
		sli = df.loc[sb]
		gentrifying = True if sli.iloc[0]['gross_rent_0_1beds_percentile'] + cutoff < sli.iloc[-1]['gross_rent_0_1beds_percentile'] else False
		if gentrifying:
			gentrified.append(sb)
	return gentrified

def plot_gentrifying(df, cutoff = 5, column = 'gross_rent_0_1beds_percentile', ylabel = 'Percentile of median studio/1B rent'):
	'''Plots change in time of some variable (column) for each subborough, separated by gentrifying and non-gentrifying'''
	gentrifying_sbs = get_gentrifying_sbs(df, cutoff = cutoff)
	for sb in set(df.index.get_level_values('subborough')):
		sli = df.loc[sb]
		gentrifying = True if sb in gentrifying_sbs else False
		col = 'r' if gentrifying else 'k'
		alpha = 0.75 if gentrifying else 0.25
		label = 'Gentrifying' if gentrifying else 'Non-gentrifying'
		beginning_year = pd.Series(sli.index).apply(lambda x: x.split('-')[0])
		plt.plot(beginning_year, sli[column], col + '-', alpha = alpha, label = label)
	plt.xlabel('Year')
	plt.ylabel(ylabel)
	handles, labels = plt.gca().get_legend_handles_labels()
	by_label = dict(zip(labels, handles))
	plt.legend(by_label.values(), by_label.keys(), loc = 1)
	plt.show()
	plt.close()

df = get_mlidf('data/core-set/median_rent/sub-borougharea-medianrentstudiosand1-bedrooms2017.csv')
df['gross_rent_0_1beds_percentile'] = get_percentile_column(df, 'gross_rent_0_1beds')


