import pandas as pd
import geopandas as gp
import numpy as np
import dill, pyproj, librosa
from shapely.geometry import Point
import os

path = os.path.dirname(os.path.realpath(__file__))

location = open(path+'/records/location.txt','r').read()

location = [float(x) for x in location.split(',')]

wgs84=pyproj.Proj("+init=EPSG:4326")
utm = pyproj.Proj("+init=EPSG:32637")
location = Point(pyproj.transform(wgs84, utm, location[0],location[1]))

predictor = dill.load(open(path+'/predictor.dill','r'))

labels = {'people':0,
          'construction':1,
          'roads':2,
          'railway':3}

files = os.listdir(path+'/records')

seconds = 4
sample_rate=22050
data = []
decibel_data = []

for f in files:
    if f =='.DS_Store' or f.endswith('.txt'):
        continue
    s = np.load(path+'/records/'+f)[0]+0.18
    start = 0
    end = seconds*sample_rate
    while end<=len(s):
        features=[]
        y = s[start:end]
        mfcc = np.mean(librosa.feature.mfcc(y=y, sr=sample_rate, n_mfcc=64).T,axis=0)
        mfcc_1 = np.max(librosa.feature.mfcc(y=y, sr=sample_rate, n_mfcc=64).T,axis=0)
        mfcc_2 = np.min(librosa.feature.mfcc(y=y, sr=sample_rate, n_mfcc=64).T,axis=0)
        mfcc_3 = np.std(librosa.feature.mfcc(y=y, sr=sample_rate, n_mfcc=64).T,axis=0)
        stft = np.abs(librosa.stft(y))
        chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T,axis=0)
        mel = np.mean(librosa.feature.melspectrogram(y, sr=sample_rate).T,axis=0)
        contrast = np.mean(librosa.feature.spectral_contrast(S=stft, sr=sample_rate).T,axis=0)
        tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sample_rate).T,axis=0)
        for x in [mfcc,mfcc_1,mfcc_2,mfcc_3, chroma, mel, contrast, tonnetz]:
            features.extend(x)
        
        data.append(features)
        start += seconds*sample_rate
        end += seconds*sample_rate
        
        decibel_data.append(abs(librosa.logamplitude(y**2,ref=np.median).min()))

predictions = predictor.predict(data).tolist()

dbs={}
for source, label in labels.items():
    sound_level_data = []
    for x in range(len(predictions)):
        if predictions[x]==label:
            sound_level_data.append(decibel_data[x])
    if len(sound_level_data)==0:
        continue
    dbs[source] = np.mean(sound_level_data)
    
def calculate_distance(point,geom):
    if geom.type in ['LineString','MultiLineString']:
        closest_point = geom.interpolate(geom.project(point))
        distance = point.distance(closest_point)
    else:
        closest_point = geom.centroid
        distance = point.distance(closest_point)
    return distance

noise_makers = gp.read_file(path+'/noise_makers.geojson').to_crs(epsg=32637)
noise_makers = noise_makers[noise_makers['geometry'].intersects(location.buffer(600))]
tags_ref = pd.read_csv(path+'/tags.csv',sep=';')[['tag','key','sound_level']]

class_minimum_index = {}

for x in xrange(noise_makers.shape[0]):
    if (noise_makers['tag'].values[x] == 'highway') & ('roads' in dbs):
        geom = noise_makers['geometry'].values[x]
        distance = calculate_distance(location,geom)
        if 'roads' not in class_minimum_index:
            class_minimum_index['roads'] = {'index':x,'distance':distance}
        else:
            if distance<class_minimum_index['roads']['distance']:
                class_minimum_index['roads'] = {'index':x,'distance':distance}
                
    elif (noise_makers['tag'].values[x] == 'railway') & ('railway' in dbs):
        geom = noise_makers['geometry'].values[x]
        distance = calculate_distance(location,geom)
        if 'railway' not in class_minimum_index:
            class_minimum_index['railway'] = {'index':x,'distance':distance}
        else:
            if distance<class_minimum_index['railway']['distance']:
                class_minimum_index['railway'] = {'index':x,'distance':distance}
                
    elif (noise_makers['key'].values[x] == 'construction') & ('construction' in dbs):
        geom = noise_makers['geometry'].values[x]
        distance = calculate_distance(location,geom)
        if 'construction' not in class_minimum_index:
            class_minimum_index['construction'] = {'index':x,'distance':distance}
        else:
            if distance<class_minimum_index['construction']['distance']:
                class_minimum_index['construction'] = {'index':x,'distance':distance}
                
    elif (noise_makers['tag'].values[x] not in ['highway','railway','construction']) & ('people' in dbs):
        geom = noise_makers['geometry'].values[x]
        distance = calculate_distance(location,geom)
        if 'people' not in class_minimum_index:
            class_minimum_index['people'] = {'index':x,'distance':distance}
        else:
            if distance<class_minimum_index['people']['distance']:
                class_minimum_index['people'] = {'index':x,'distance':distance}

for souce, params in class_minimum_index.items():
    tag = noise_makers.iloc[params['index']]['tag']
    key = noise_makers.iloc[params['index']]['key']
    
    l2=dbs[source]
    distance_to_object = class_minimum_index[source]['distance']
    l1 = l2+abs(20*np.log(1.0/distance_to_object))
    for x in range(tags_ref.shape[0]):
        if (tags_ref['tag'].values[x]==tag) & (tags_ref['key'].values[x]==key):
            tags_ref['sound_level'].values[x] = l1

tags_ref.to_csv(path+'/records/new_tags.csv',sep =';',index=False)