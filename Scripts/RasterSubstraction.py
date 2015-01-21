'''
RasterSubstraction.py

Author
  Adrien Lepoutre
  Dept of Geography
  McGill University, Montreal, Canada
  adrien.lepoutre@mail.mcgill.ca

Date      July 2013


Purpose
    Substract the value of two raster to create a third raster.
    
Inputs:
    See 'Loading inputs' section below
'''

# Import system modules
import arcpy
from arcpy import env
from arcpy.sa import *

inRaster1 = Raster(sys.argv[1])
inRaster2 =  Raster(sys.argv[2])
PolygonToClip =sys.argv[3]
rivername =sys.argv[4]
env.workspace= sys.argv[5]


# Set environment settings

# Set local variables


if PolygonToClip <> "#":
    ClippedRaster1="in_memory/clippedRaster1"
    ClippedRaster2="in_memory/clippedRaster2"
    arcpy.gp.ExtractByMask_sa(inRaster1,PolygonToClip,ClippedRaster1)
    arcpy.gp.ExtractByMask_sa(inRaster2,PolygonToClip,ClippedRaster2)
    inRaster1 = ClippedRaster1
    inRaster2 = ClippedRaster2



# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# Execute Minus
outMinus = Raster(inRaster1) - Raster(inRaster2)

# Save the output
SubstractedRaster = "%s_SubRaster.tif" %rivername
outMinus.save(SubstractedRaster)


# Add output to map
import arcpy.mapping
# Get the map document 
mxd = arcpy.mapping.MapDocument("CURRENT")  

# Get the data frame
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]  

# Create a new layer
newlayer = arcpy.mapping.Layer(SubstractedRaster)

# Add the layer to the map at the top of the TOC in data frame 0 
arcpy.mapping.AddLayer(df, newlayer,"TOP")

# Refresh 
arcpy.RefreshActiveView()
arcpy.RefreshTOC()
del mxd, df, newlayer

