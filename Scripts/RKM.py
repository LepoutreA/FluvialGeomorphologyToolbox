
'''Distance Along Line (formerly RKM)
RKM.py

Author
  Adrien Lepoutre
  Dept of Geography
  McGill University, Montreal, Canada
  adrien.lepoutre@mail.mcgill.ca

Date      July 2013


Purpose
  Calculates cumulative distance of objects along line.

Inputs:
    See 'Loading variables' section below
'''

import arcpy, os, sys
from arcpy import env
arcpy.overWriteOutputs = 1

# Load variables

Centerline = sys.argv[1]            # Polyline of network.
river_objects = sys.argv[2]         # Objects along network.  
Case_Field = sys.argv[3]            # Field used for mean center. 
Near_Search_Radius = sys.argv[4]    # Maximum distance between two objects.
RKM_START_QUADRANT = sys.argv[5]    # Initial quadrant network distances should be calculated with respect to.
workspce = sys.argv[6]              # Workspace
rivername = sys.argv[7]             # String to characterize output.

env.workspace = workspce

desc = arcpy.Describe(river_objects)
spatial_ref = desc.spatialReference


os.chdir(workspce)
#Local variables
Output_Event_Table_Properties = "FID POINT MEAS"

# Process: Unsplit Line
line_unsplit="in_memory\\lineUnsplit"
arcpy.UnsplitLine_management(Centerline, line_unsplit, "", "")


object1="in_memory\\obj2"
#Add field to object1 to copy if Case_field='FID'
if Case_Field=="FID":
    arcpy.AddField_management(river_objects, "MeanCtr", "TEXT",25)
    arcpy.CalculateField_management(river_objects, "MeanCtr", "float(!FID!)", "PYTHON")
    arcpy.MeanCenter_stats(river_objects, object1, "", "MeanCtr","")
else:
    arcpy.MeanCenter_stats(river_objects, object1, "", Case_Field,"")


# Process: Near
arcpy.Near_analysis(object1, line_unsplit, Near_Search_Radius, "LOCATION", "NO_ANGLE")

# Process: Make XY Event Layer
obj_Layer="in_memory\\obj1.lyr" 
arcpy.MakeXYEventLayer_management(object1, "NEAR_X", "NEAR_Y", obj_Layer, spatial_ref, "")

# Process: Copy Features
object_feat_shp=r"%s_object_feat.shp" %rivername
arcpy.CopyFeatures_management(obj_Layer, object_feat_shp, "", "0", "0", "0")

# Process: Create Routes
rkm_unsp_r_="in_memory\\rkm_unsp_r1"
arcpy.CreateRoutes_lr(Centerline, "Id", rkm_unsp_r_, "LENGTH", "", "", RKM_START_QUADRANT, "1", "0", "IGNORE", "INDEX")
result_rkm=r"%s_RKM.dbf" %rivername

arcpy.LocateFeaturesAlongRoutes_lr(object_feat_shp,rkm_unsp_r_,"Id","10000 Meters",result_rkm,"RID POINT MEAS","FIRST","DISTANCE","ZERO","FIELDS","M_DIRECTON")

arcpy.Delete_management(obj_Layer)
arcpy.Delete_management(object1)
arcpy.Delete_management(rkm_unsp_r_)


# Import final layer to map                          
import arcpy.mapping
# get the map document 
mxd = arcpy.mapping.MapDocument("CURRENT")  

# get the data frame 
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]  

# create a new layer 
dbf_Table = arcpy.mapping.TableView(result_rkm)

# add the layer to the map at the bottom of the TOC in data frame 0 
#arcpy.mapping.AddLayer(df, newlayer,"TOP")

arcpy.mapping.AddTableView(df,dbf_Table)

# Refresh things
arcpy.RefreshActiveView()
arcpy.RefreshTOC()
del mxd, df, dbf_Table

