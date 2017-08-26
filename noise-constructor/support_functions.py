from shapely.ops import unary_union
from rtree import index
import geopandas as gp

def grid_intersection(data,grid,values,geoms):
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

def set_spatial_index(coordinates):
    p = index.Property()
    p.dimension = 2
    ind= index.Index(properties=p)
    for x,y in zip(coordinates.keys(),coordinates.values()):
        ind.add(x,y)
    return ind

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
    gdf['value'] = values

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
