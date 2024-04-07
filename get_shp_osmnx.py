import osmnx as ox
# refs: https://github.com/cyang-kth/osm_mapmatching
# 要用官网的方法下载
# xian_bounds = [107.353, 33.532, 110.094, 34.9]
# north, south, east, west = xian_bounds[3], xian_bounds[1], xian_bounds[2], xian_bounds[0]
# G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
# ox.io.save_graph_shapefile(G, filepath='./data/Xian OSMnx')
#
# chengdu_bounds = [102.788, 30.086, 105.529, 31.508]
# north, south, east, west = chengdu_bounds[3], chengdu_bounds[1], chengdu_bounds[2], chengdu_bounds[0]
# G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
# ox.io.save_graph_shapefile(G, filepath='./data/Chengdu OSMnx')

import time
from shapely.geometry import Polygon
import os
import numpy as np
import osmnx as ox
from shapely.geometry import shape
import json


def save_graph_shapefile_directional(G, filepath=None, encoding="utf-8"):
    # default filepath if none was provided
    if filepath is None:
        filepath = os.path.join(ox.settings.data_folder, "graph_shapefile")

    # if save folder does not already exist, create it (shapefiles
    # get saved as set of files)
    if not filepath == "" and not os.path.exists(filepath):
        os.makedirs(filepath)
    filepath_nodes = os.path.join(filepath, "nodes.shp")
    filepath_edges = os.path.join(filepath, "edges.shp")

    # convert undirected graph to gdfs and stringify non-numeric columns
    gdf_nodes, gdf_edges = ox.utils_graph.graph_to_gdfs(G)
    gdf_nodes = ox.io._stringify_nonnumeric_cols(gdf_nodes)
    gdf_edges = ox.io._stringify_nonnumeric_cols(gdf_edges)
    # We need an unique ID for each edge
    gdf_edges["fid"] = np.arange(0, gdf_edges.shape[0], dtype='int')
    # save the nodes and edges as separate ESRI shapefiles
    gdf_nodes.to_file(filepath_nodes, encoding=encoding)
    gdf_edges.to_file(filepath_edges, encoding=encoding)

print("osmnx version",ox.__version__)

# Download by a bounding box
xian_bounds = (107.353,110.094,33.532,34.9)
x1,x2,y1,y2 = xian_bounds
boundary_polygon = Polygon([(x1,y1),(x2,y1),(x2,y2),(x1,y2)])
G = ox.graph_from_polygon(boundary_polygon, network_type='drive')
start_time = time.time()
save_graph_shapefile_directional(G, filepath='./data/Xian OSMnx')
print("--- %s seconds ---" % (time.time() - start_time))

chengdu_bounds = (102.788,105.529,30.086,31.508)
x1,x2,y1,y2 = chengdu_bounds
boundary_polygon = Polygon([(x1,y1),(x2,y1),(x2,y2),(x1,y2)])
G = ox.graph_from_polygon(boundary_polygon, network_type='drive')
start_time = time.time()
save_graph_shapefile_directional(G, filepath='./data/Chengdu OSMnx')
print("--- %s seconds ---" % (time.time() - start_time))
