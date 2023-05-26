"""
Build the ANN model for the probability of a tile being a mine
"""

# import the libraries
import numpy as np
import pandas as pd
import tensorflow as tf

"""
Part 1 - Data Preprocessing
"""
dir = '../data/'
file_name = 'data_80_45.csv'
datapath = dir + file_name

# import the dataset
dataset = pd.read_csv(datapath)

# !!! IMPORTANT: When the data gets too big, please cut off the data here
# so that the game can load faster
# We will keep the last 6250 rows of data here for this configuration (see the part 2 formula)

# last 6250 rows of data
#dataset = dataset.iloc[-6250:, :]
X = dataset.iloc[:, :-1].values
y = dataset.iloc[:, -1].values

# Encoding categorical data
# Not needed for this dataset

# Splitting the dataset into the Training set and Test set
from sklearn.model_selection import train_test_split
# 80% training set, 20% test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2)

# Feature Scaling
from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
X_train = sc.fit_transform(X_train) # fit the scaler to the training set, then transform the training set
X_test = sc.transform(X_test) # transform the test set

"""
Part 2 - Building the ANN

N(h) = N(s) / (a * (N(i) + N(o))) where
N(h) = number of neurons in the hidden layer
N(s) = number of samples in the training set (in batches)
N(i) = number of neurons in the input layer
N(o) = number of neurons in the output layer
a = an arbitrary scaling factor usually between 2 and 10 (we use 2 here)
"""

# Initializing the ANN
ann = tf.keras.models.Sequential()

# Adding the input layer
# units: number of nodes in the hidden layer
ann.add(tf.keras.layers.Dense(units=12, activation='relu'))

# Adding the hidden layer
ann.add(tf.keras.layers.Dense(units=12, activation='relu'))

# Adding the output layer
# units: number of nodes in the output layer
# activation: sigmoid function for binary output
ann.add(tf.keras.layers.Dense(units=1, activation='sigmoid'))

"""
Part 3 - Training the ANN
"""

# Compiling the ANN
# optimizer: adam is a stochastic gradient descent algorithm
# loss: binary_crossentropy for binary output
ann.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])

# Training the ANN on the Training set
# batch_size: number of samples after which the weights are updated
# epochs: number of iterations
ann.fit(X_train, y_train, batch_size = 32, epochs = 100)

"""
Part 4 - Making the predictions and evaluating the model
"""

# Predicting the Test set results
y_pred = ann.predict(X_test)
y_pred = (y_pred > 0.5) # convert the probability to binary output
#print(np.concatenate((y_pred.reshape(len(y_pred),1), y_test.reshape(len(y_test),1)),1))

# Making the Confusion Matrix
from sklearn.metrics import confusion_matrix, accuracy_score
cm = confusion_matrix(y_test, y_pred)
print(cm)
accuracy_score(y_test, y_pred)

# Save the model
tf.keras.models.save_model(ann, 'ann_model.h5')
