import os, glob,arcpy
from arcpy import env
arcpy.overWriteOutput = 1


RawTransects = sys.argv[1]
wmask = sys.argv[2]
test = sys.argv[3]
rivername = sys.argv[4]
env.workspace = sys.argv[5]

#Operations on polygon
#arcpy.Delete_management("in_memory/Mask_Union")

arcpy.Union_analysis(wmask,"in_memory/Mask_Union2","ALL","#","NO_GAPS")

arcpy.Dissolve_management("in_memory/Mask_Union2","Mask_U_d.shp","#","#","SINGLE_PART","DISSOLVE_LINES")


arcpy.FeatureVerticesToPoints_management(RawTransects,"verti_points.shp","BOTH_ENDS")

SubExtra = "%s Unknown" %test
arcpy.AddMessage(test)

extraSnap = "Mask_U_d.shp"+ " EDGE '%s'" %SubExtra


#"Kiamika_WaterMask_erase2 EDGE '25 Unknown'"
arcpy.AddMessage(extraSnap)

arcpy.Snap_edit("verti_points.shp",extraSnap)

arcpy.PointsToLine_management("verti_points.shp","transects.shp","TARGET_FID","#","NO_CLOSE")

OutputTransects = "%s_transects.shp" %rivername

arcpy.Clip_analysis("transects.shp",wmask,OutputTransects,"#")

# Add output to map
import arcpy.mapping
# Get the map document 
mxd = arcpy.mapping.MapDocument("CURRENT")  

# Get the data frame
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]  

# Create a new layer
newlayer = arcpy.mapping.Layer(OutputTransects)

# Add the layer to the map at the top of the TOC in data frame 0 
arcpy.mapping.AddLayer(df, newlayer,"TOP")

# Refresh 
arcpy.RefreshActiveView()
arcpy.RefreshTOC()
del mxd, df, newlayer


