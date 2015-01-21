'''
Polygon to points.py

Author
  Adrien Lepoutre
  Dept of Geography
  McGill University, Montreal, Canada
  adrien.lepoutre@mail.mcgill.ca

Date      July 2013


Purpose
  Create non-equidistant points along polygon.

Inputs:
    See 'Loading inputs' section below
'''
# Import system modules
import sys, string, os, sys, arcpy,unicodedata,arcgisscripting,math
from arcpy import env

#Loading inputs
dissolved_polygon = sys.argv[1]     # Polygon feature class.
Cellsize=sys.argv[2]                # Cell size of feature to raster conversion.    
rivername = sys.argv[3]             # Short string to characterize output. Input no more than 2 characters.
workspce = sys.argv[4]              # Workspace where output should be created.
   
env.workspace = workspce
arcpy.overWriteOutputs = 1
os.chdir(workspce)

diss_polygon_line="in_memory\\diss_poly"
arcpy.FeatureToLine_management(dissolved_polygon,diss_polygon_line,"#","ATTRIBUTES")


Rast_line="in_memory/Rastline1"
arcpy.PolylineToRaster_conversion(diss_polygon_line,"FID",Rast_line,"MAXIMUM_LENGTH","NONE",str(Cellsize))


Rast_Pt="%s_Rastpt.shp" %rivername
arcpy.RasterToPoint_conversion(Rast_line,Rast_Pt,"VALUE")

Cellsize=float(Cellsize)*2
snap_extra="%s EDGE '%s Unknown'" %(dissolved_polygon,Cellsize)
arcpy.AddMessage(snap_extra)
arcpy.Snap_edit(Rast_Pt,snap_extra)

arcpy.AddXY_management(Rast_Pt)

arcpy.AddField_management(Rast_Pt, "y", "DOUBLE",15,6)
arcpy.AddField_management(Rast_Pt, "v", "DOUBLE",15,6)
arcpy.AddField_management(Rast_Pt, "Id", "DOUBLE",15,6)

# Add output to map
import arcpy.mapping
# Get the map document 
mxd = arcpy.mapping.MapDocument("CURRENT")  

# Get the data frame
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]  

# Create a new layer
newlayer = arcpy.mapping.Layer(Rast_Pt)

# Add the layer to the map at the top of the TOC in data frame 0 
arcpy.mapping.AddLayer(df, newlayer,"TOP")

# Refresh 
arcpy.RefreshActiveView()
arcpy.RefreshTOC()
del mxd, df, newlayer


