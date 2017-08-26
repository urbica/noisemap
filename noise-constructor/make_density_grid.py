import geopandas as gp
import os, math
import shapefile as shp

path = os.path.dirname(os.path.realpath(__file__))

def make_fishnet(bbox):

    #data = data.to_crs(epsg=32637)
    
    minx,miny,maxx,maxy = bbox
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
    return grid

houses = gp.read_file(path+'houses.shp')
houses = houses.to_crs(epsg=32637)
houses = houses[['geometry']]
print 'houses ready'

houses['area'] = houses.area

#grid = gp.read_file(path+'/grid.shp')
bounds = gp.read_file(path+'/export.geojson').to_crs(epsg=32637).total_bounds
grid = make_fishnet(bounds)
#grid = grid.to_crs(epsg=32637)
print 'grid ready'
print grid.crs, houses.crs
data = gp.sjoin(grid, houses)
data = data.groupby('ID').sum().reset_index(0)
print 'sjoin ready'

grid = grid.merge(data, on='ID')
grid = grid.to_crs(epsg=4326)
grid['area']= grid['area'].fillna(0)
grid['density'] = grid['area']/(1000*1000)
grid = grid[['ID','density','geometry']]
print 'merge ready'

with open(path+'/density_grid.geojson','w') as f:
	f.write(grid.to_json())