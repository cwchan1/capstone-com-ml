import numpy as np
import matplotlib.pyplot as pyplot
import pandas as pd

from sklearn.preprocessing import MinMaxScaler

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout

training_data_raw = pd.read_csv('AAPL.csv')

training_data_raw_plot = pd.read_csv('AAPL.csv', index_col=0, usecols=[0,1], parse_dates=True, squeeze=True)
training_data_raw_plot.plot()

# Processing the csv file
scaler = MinMaxScaler(feature_range = (0,1))

training_data_splice = training_data_raw.iloc[:,1:2].values # Grab only the opening stock values
training_data_scaled = scaler.fit_transform(training_data_splice)

scaled_data = pd.DataFrame(data=training_data_scaled)
scaled_data.plot()
pyplot.show()

features_set = []
labels = []
for i in range(53, 1007):
   features_set.append(training_data_scaled[i-53:i, 0])
   print(training_data_scaled[i,0])
   labels.append(training_data_scaled[i, 0])

features_set, labels = np.array(features_set), np.array(labels)