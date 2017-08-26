import geopandas as gp
import os

path = os.path.dirname(os.path.realpath(__file__))

export = gp.read_file(path+'/export.geojson')

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

with open(path+'/noise_makers.geojson','w') as f:
    f.write(export.to_json())