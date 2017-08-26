import geopandas as gp
import pandas as pd
import os
from shapely.ops import unary_union
from rtree import index
import math
import shapefile as shp

path = os.path.dirname(os.path.realpath(__file__))

export = gp.read_file(path+'/export.geojson')
tags_ref = pd.read_csv(path+'/tags.csv',sep=';')
density_grid = gp.read_file(path+'/density_grid.geojson')
### insert density into function

tags_dict =['highway',
            'amenity',
            'tourism',
            'historic',
            'building:architecture',
            'artwork_type',
            'zoo']
keys = []
tags = []
for x in range(export.shape[0]):
    for tag in tags_dict:
        if tag in export.columns:
            if export[tag].values[x] is not None:
                tags.append(tag)
                keys.append(export[tag].values[x])
                break
export['tag']=tags         
export['key']=keys
export = export[['tag','key','geometry']]

noise_makers = gp.sjoin(export, density_grid, how='left').merge(tags_ref,on=['tag','key'])
noise_makers = noise_makers[['geometry','X','density']]

noise_makers['buffer45'] = 10 ** ((noise_makers['X'] - 45) /20.0) / (1 - noise_makers['density'])
noise_makers['buffer55'] = 10 ** ((noise_makers['X'] - 55) /20.0) / (1 - noise_makers['density'])
noise_makers['buffer65'] = 10 ** ((noise_makers['X'] - 65) /20.0) / (1 - noise_makers['density'])


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
    #buff55 = buff55.difference(buff65)
    values.append(55)
    geoms.append(buff55)
    
    size45 = noise_makers['buffer45'].values[x]
    
    buff45 = geom.buffer(size45)
    #buff45 = buff45.difference(geom.buffer(size55)) 
    values.append(45)
    geoms.append(buff45)

result = gp.GeoDataFrame()
result.geometry = geoms 
result['value'] = values

result.crs = {'init': 'epsg:32637'}
result = result.to_crs(epsg=4326)

#with open(path+'/buffers.geojson','w') as f:
#    f.write(result.to_json())

def level_on_distance_with_density(sound_level, target_level, density):
    r = ((10 ** (sound_level - target_level)) ** (1/20)) / (1 - density)
    return r

def iron_dissolver(data):

    print 'dissolver starts'
    
    data = data[['geometry','value']]

    gdf =gp.GeoDataFrame()
    
    geoms=[]
    values=[]

    for x in range(gdf.shape[0]):
        geom = gdf.geometry.values[x]
        val = gdf['value'].values[x]
        if geom.is_empty == False and geom.is_valid:
            if geom.type=='LineString':
                geoms.append(geom)
                values.append(val)
            else:
                for g in geom:
                    geoms.append(g)
                    values.append(val)
    gdf.geometry = geoms
    gdf['values'] = values

    geoms=[]
    values=[]

    for val in [65,55,45]:
        print 'loop, processing %i'%val
        df = data[data['value']==val]
        print df.shape
        df.geometry = df.buffer(0)
        geom = unary_union(df.geometry.values)
        geoms.append(geom)
        values.append(val)

    gdf.geometry = geoms
    gdf['value'] = values

    gdf.crs = {'init': u'epsg:4326'}

    return gdf

buffer45 = result[result['value']==45]
buffer55 = result[result['value']==55]
buffer65 = result[result['value']==65]

def set_spatial_index(coordinates):
    p = index.Property()
    p.dimension = 2
    ind= index.Index(properties=p)
    for x,y in zip(coordinates.keys(),coordinates.values()):
        ind.add(x,y)
    return ind

def geo_difference(gdf1, gdf2):

    coords={}
    for x in range(gdf2.shape[0]):
        coord = (gdf2.geometry.values[x].centroid.x,gdf2.geometry.values[x].centroid.y)
        id = x
        coords[id] = coord

    ind = set_spatial_index(coords)

    geoms = []
    for x in range(gdf1.shape[0]):
        if x%1000==0:
            print round((x/float(gdf1.shape[0]))*100,2), 'percent done'
        geom1 = gdf1['geometry'].values[x]
        point = (geom1.centroid.x,geom1.centroid.y)
        list_of_nearest = ind.nearest(point, 50)
        for y in list_of_nearest:
            geom2 = gdf2['geometry'].values[y]
            geom1 = geom1.difference(geom2)
        geoms.append(geom1)
    gdf1['geometry'] = geoms

    return gdf1[gdf1['geometry'].notnull()]

def make_fishnet(data):

    data = data.to_crs(epsg=32637)

    minx,miny,maxx,maxy = data.total_bounds
    #print maxx, minx,  maxy, miny
    dx = 1000
    dy = 1000

    nx = int(math.ceil(abs(maxx - minx)/dx))
    ny = int(math.ceil(abs(maxy - miny)/dy))

    w = shp.Writer(shp.POLYGON)
    w.autoBalance = 1
    w.field("ID")
    id=0

    for i in range(ny):
        for j in range(nx):
            id+=1
            #print id
            vertices = []
            parts = []
            vertices.append([min(minx+dx*j,maxx),max(maxy-dy*i,miny)])
            vertices.append([min(minx+dx*(j+1),maxx),max(maxy-dy*i,miny)])
            vertices.append([min(minx+dx*(j+1),maxx),max(maxy-dy*(i+1),miny)])
            vertices.append([min(minx+dx*j,maxx),max(maxy-dy*(i+1),miny)])
            parts.append(vertices)
            w.poly(parts)
            w.record(id)

    w.save(path+'/grid.shp')
    grid = gp.read_file(path+'/grid.shp')
    grid.crs = {'init': u'epsg:32637'}
    grid = grid.to_crs(epsg=4326)
    return grid

grid = make_fishnet(buffer45)

#grid = gp.read_file(path+'/density_grid.geojson')

values = [] 
geoms = []

def grid_intersection(data):
    gdf = gp.GeoDataFrame()
    for x in range(data.shape[0]):
        if x%500==0:
            print round(float(x)/data.shape[0],2),'done'
        geom1  = data.geometry.values[x]
        value = data['value'].values[x]
        for y in range(grid.shape[0]):
            geom2  = grid.geometry.values[y]
            if geom2.intersects(geom1):
                g = geom2.intersection(geom1)
                geoms.append(g)
                values.append(value)
    gdf.geometry = geoms
    gdf['value'] = values
    print 'gdf done'
    return gdf

buffer45 = grid_intersection(buffer45)
buffer55 = grid_intersection(buffer55)
buffer65 = grid_intersection(buffer65)

buffer45.geometry = buffer45.buffer(0.00000001)
buffer55.geometry = buffer55.buffer(0.00000001)
buffer65.geometry = buffer65.buffer(0.00000001)

buffer45 = geo_difference(buffer45, buffer55)
buffer55 = geo_difference(buffer55, buffer65)

gdf = buffer45.append(buffer55).append(buffer65)

gdf.geometry = gdf.buffer(0.00000001)

gdf = iron_dissolver(gdf)

with open(path+'/dissolved.geojson','w') as f:
    f.write(gdf.to_json())