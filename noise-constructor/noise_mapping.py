import geopandas as gp
import pandas as pd
import os
from support_functions import grid_intersection, geo_difference, iron_dissolver

path = os.path.dirname(os.path.realpath(__file__))

noise_makers = gp.read_file(path+'/noise_makers.geojson')
tags_ref = pd.read_csv(path+'/tags.csv',sep=';')
density_grid = gp.read_file(path+'/density_grid.geojson')

noise_makers = gp.sjoin(noise_makers, density_grid, how='left').merge(tags_ref,on=['tag','key'])
noise_makers = noise_makers[['geometry','sound_level','density']]

noise_makers['buffer45'] = 10 ** ((noise_makers['sound_level'] - 45) /20.0) / (1 - noise_makers['density'])
noise_makers['buffer55'] = 10 ** ((noise_makers['sound_level'] - 55) /20.0) / (1 - noise_makers['density'])
noise_makers['buffer65'] = 10 ** ((noise_makers['sound_level'] - 65) /20.0) / (1 - noise_makers['density'])


noise_makers = noise_makers.to_crs(epsg=32637)

values = [] 
geoms = [] 

for x in range(len(noise_makers)):
    
    geom = noise_makers['geometry'].values[x] 
    
    size65 = noise_makers['buffer65'].values[x]
    
    buff65 = geom.buffer(size65) 
    values.append(65) 
    geoms.append(buff65)

    size55 = noise_makers['buffer55'].values[x]
    
    buff55 = geom.buffer(size55)
    values.append(55)
    geoms.append(buff55)
    
    size45 = noise_makers['buffer45'].values[x]
    
    buff45 = geom.buffer(size45)
    values.append(45)
    geoms.append(buff45)

result = gp.GeoDataFrame()
result.geometry = geoms 
result['value'] = values

result.crs = {'init': 'epsg:32637'}
result = result.to_crs(epsg=4326)

buffer45 = result[result['value']==45]
buffer55 = result[result['value']==55]
buffer65 = result[result['value']==65]

grid = gp.read_file(path+'/density_grid.geojson')

values = [] 
geoms = []

buffer45 = grid_intersection(buffer45,grid,values, geoms)
buffer55 = grid_intersection(buffer55,grid,values, geoms)
buffer65 = grid_intersection(buffer65,grid,values, geoms)

buffer45.geometry = buffer45.buffer(0.00000001)
buffer55.geometry = buffer55.buffer(0.00000001)
buffer65.geometry = buffer65.buffer(0.00000001)

buffer45 = geo_difference(buffer45, buffer55)
buffer55 = geo_difference(buffer55, buffer65)

gdf = buffer45.append(buffer55).append(buffer65)

gdf.geometry = gdf.buffer(0.00000001)

gdf = iron_dissolver(gdf)

gdf = gdf.sort_values('value')[['geometry','value']]

with open(path+'/dissolved.geojson','w') as f:
    f.write(gdf.to_json())