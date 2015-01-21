
'''
PointsInsidePolygon.py

Author
  Adrien Lepoutre
  Dept of Geography
  McGill University, Montreal, Canada
  adrien.lepoutre@mail.mcgill.ca

Date      July 2013


Purpose
Converts a polygon to points.

Inputs:
    See 'Loading inputs' section below
'''


import arcpy,os,sys
from arcpy import env
from arcpy.sa import *

#Loading inputs
wmask = sys.argv[1]
rasters_extract = sys.argv[2]
polygons_extract = sys.argv[3]
BufferExtent = sys.argv[4]
rivername = sys.argv[5]
workspce = sys.argv[6]

env.workspace = workspce

# Create the points, from the mask, that will be used to extract values from other elements
rasterStruct = "in_memory/rasterStructure"
arcpy.PolygonToRaster_conversion(wmask,"FID",rasterStruct,"CELL_CENTER","NONE","1")


pts="%s_output_pts.shp" %rivername
arcpy.RasterToPoint_conversion(rasterStruct,pts,"Value")

# Multivalue extraction for all rasters
arcpy.gp.ExtractMultiValuesToPoints_sa(pts,rasters_extract,"NONE")


#Multivalue extraction for all polygons
polygons_extract_split = polygons_extract.split(';')
arcpy.AddMessage(polygons_extract_split)
extract_list = []
for i in polygons_extract_split:
    arcpy.PolygonToRaster_conversion(i,"Id","in_memory/temp_rast","CELL_CENTER","NONE","1")
    arcpy.gp.Reclassify_sa("in_memory/temp_rast","VALUE","0 10000 1;NODATA 0","temp_reclass","DATA")
    desc1 = arcpy.Describe(i)
    shapefilename1 = desc1.name
    shapefilename1=shapefilename1[:-4]
    
    extraMulti = ' '.join(["temp_reclass",shapefilename1])
    arcpy.gp.ExtractMultiValuesToPoints_sa(pts,extraMulti,"NONE")
    
    



# Optional Part for shore
while BufferExtent != "#":
    
    PolyLine = "in_memory/Wmask_line"
    Buffer_shp = "in_memory/TEST_BUFFER"
    reclass1="in_memory/ShoreBuffer"
    arcpy.PolygonToLine_management(wmask, PolyLine)
    BufferExtent =str(BufferExtent)
    BufferExtra = "%s Unknown" %BufferExtent
    arcpy.Buffer_analysis(PolyLine,Buffer_shp,BufferExtra,"FULL","ROUND","ALL","#")

    buf1="in_memory/BufSrast"
    arcpy.PolygonToRaster_conversion(Buffer_shp,"FID",buf1,"CELL_CENTER","NONE","1")
    arcpy.gp.Reclassify_sa(buf1,"VALUE","0 1;NODATA 0",reclass1,"DATA")


    #desc1 = arcpy.Describe(reclass1)
    #shapefilename1 = desc1.name
    #shapefilename1 = shapefilename1[:-4]

    BufferExtra = ' '.join([reclass1,"Shore_Buffer"])
    arcpy.AddMessage(BufferExtra)
    arcpy.gp.ExtractMultiValuesToPoints_sa(pts,BufferExtra,"NONE")
    break

arcpy.AddXY_management(pts)




#why 51
# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "TEST_BUFFER"
#arcpy.PolygonToRaster_conversion("TEST_BUFFER","FID",output,"CELL_CENTER","NONE","1")
#arcpy.gp.ExtractMultiValuesToPoints_sa("output_pts","test_reclass1 test_reclass1","NONE"))



                     
# Add result to map
import arcpy.mapping
# get the map document 
mxd = arcpy.mapping.MapDocument("CURRENT")  

# get the data frame 
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]  

# create a new layer 
newlayer = arcpy.mapping.Layer(pts)

# add the layer to the map at the bottom of the TOC in data frame 0 
arcpy.mapping.AddLayer(df, newlayer,"TOP")

# Refresh things
arcpy.RefreshActiveView()
arcpy.RefreshTOC()
del mxd, df, newlayer
