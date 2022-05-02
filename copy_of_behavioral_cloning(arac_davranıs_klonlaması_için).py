# -*- coding: utf-8 -*-

#Automatically generated by Colaboratory.

!git clone https://github.com/umitgorgul/Track

!ls Track

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import keras
from keras.models import Sequential
from keras.optimizers import Adam
from keras.layers import Convolution2D, MaxPooling2D, Dropout, Flatten, Dense, Conv2D
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from imgaug import augmenters as iaa
import cv2
import pandas as pd
import ntpath
import random

datadir = 'Track'
columns = ['merkez','sol','sag','steering','throttle','reverse','speed']
data = pd.read_csv (os.path.join(datadir, 'driving_log.csv'), names = columns)
pd.set_option('display.max_colwidth', -1)
data.head()

def path_leaf(path):
  head, tail = ntpath.split(path)
  return tail
data['merkez'] = data['merkez'].apply(path_leaf)
data['sol'] = data['sol'].apply(path_leaf)
data['sag'] = data['sag'].apply(path_leaf)
data.head()

num_bins = 25
samples_per_bin = 200
hist, bins = np.histogram(data['steering'], num_bins)
center = (bins[-1]+ bins[1:])*0.5
plt.bar(center, hist, width=0.05)
plt.plot((np.min(data['steering']), np.max(data['steering'])), (samples_per_bin, samples_per_bin))

print('Toplam Sahip Olunan Veri:', len(data))
remove_list = []
remove_list = []
for j in range(num_bins):
  list_ = []
  for i in range(len(data['steering'])):
    if data['steering'][i] >= bins[j] and data['steering'][i] <= bins[j+1]:
      list_.append(i)
  list_ = shuffle(list_)
  list_ = list_[samples_per_bin:]
  remove_list.extend(list_)
 
print('removed:', len(remove_list))
data.drop(data.index[remove_list], inplace=True)
print('remaining:', len(data))
 
hist, _ = np.histogram(data['steering'], (num_bins))
plt.bar(center, hist, width=0.05)
plt.plot((np.min(data['steering']), np.max(data['steering'])), (samples_per_bin, samples_per_bin))

print(data.iloc[1])
def load_img_steering(datadir, df):
  image_path = []
  steering = []
  for i in range(len(data)):
    indexed_data = data.iloc[i]
    merkez, sol, sag = indexed_data[0], indexed_data[1], indexed_data[2]
    image_path.append(os.path.join(datadir, merkez.strip()))
    steering.append(float(indexed_data[3]))
  image_paths = np.asarray(image_path)
  steerings = np.asarray(steering)
  return image_paths, steerings

image_paths, steerings = load_img_steering(datadir + '/IMG', data)

X_train, X_valid, y_train, y_valid = train_test_split(image_paths, steerings, test_size=0.2, random_state=6)
print('Training Örnekleri: {}\nValid Örnekler: {}'.format(len(X_train), len(X_valid)))

fig, axes =  plt.subplots(1, 2, figsize=(12, 4))
axes[0].hist(y_train, bins = num_bins, width=0.05, color='blue')
axes[0].set_title('Training Set')
axes[1].hist(y_valid, bins = num_bins, width=0.05, color='red')
axes[1].set_title('Valid Set')

def img_preprocess(img):
  img = mpimg.imread(img)
  img = img[60:135,:,:]
  img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
  img = cv2.GaussianBlur(img, (3, 3), 0)
  img = cv2.resize(img, (200, 66))
  img = img/255
  return img

image = image_paths[100]
original_image = mpimg.imread(image)
preprocess_image = img_preprocess(image)

fig, axs = plt.subplots(1, 2, figsize=(15, 10))
fig.tight_layout()
axs[0].imshow(original_image)
axs[0].set_title('Orjinal Görsel')
axs[1].imshow(preprocess_image)
axs[1].set_title('İşlenmiş Görsel')

X_train = np.array(list(map(img_preprocess, X_train)))
X_valid = np.array(list(map(img_preprocess, X_valid)))

plt.imshow(X_train[random.randint(0, len(X_train) - 1)])
plt.axis('off')
print(X_train.shape)

def nvidia_model():
 
  model = Sequential()
 
  model.add(Conv2D(24, kernel_size=(5,5), strides=(2,2), input_shape=(66,200,3),activation='relu'))
 
  model.add(Conv2D(36, kernel_size=(5,5), strides=(2,2), activation='elu'))
  model.add(Conv2D(48, kernel_size=(5,5), strides=(2,2), activation='elu'))
  model.add(Conv2D(64, kernel_size=(3,3), activation='elu'))
  model.add(Conv2D(64, kernel_size=(3,3), activation='elu'))

 
 
  model.add(Flatten())
  model.add(Dense(100, activation='elu'))

 
 
  model.add(Dense(50, activation='elu'))
  
  model.add(Dense(10, activation ='elu'))
  model.add(Dense(1))
 
 
  optimizer= Adam(lr=1e-3)
  model.compile(loss='mse', optimizer=optimizer)
 
  return model

model = nvidia_model()
print(model.summary())

history = model.fit(X_train, y_train, epochs=20, batch_size=100, validation_data=(X_valid, y_valid), verbose=1, shuffle=1)

#history = model.fit_generator(batch_generator(X_train, y_train, 100, 1),
#                                  steps_per_epoch=300, 
#                                  epochs=10,
#                                  validation_data=batch_generator(X_valid, y_valid, 100, 0),
#                                  validation_steps=200,
#                                  verbose=1,
#                                  shuffle = 1)

plt.plot(history.history['loss'])
 plt.plot(history.history['val_loss'])
 plt.legend(['training', 'validation'])
 plt.title('Loss')
 plt.xlabel('Epoch')

model.save('model.h5')

from google.colab import files
files.download('model.h5')
