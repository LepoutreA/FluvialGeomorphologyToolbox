
'''
Distance along Line (Original) RKM_Article.py

Author
  Adrien Lepoutre
  Dept of Geography
  McGill University, Montreal, Canada
  adrien.lepoutre@mail.mcgill.ca

Date      July 2013


Purpose
  RKM toolbox without mean center option (default is mean center with ?FID?).
  More information is provided on the side of the tool. 

Inputs:
    See 'Loading inputs' section below
'''

import arcpy, os, sys
from arcpy import env
arcpy.overWriteOutputs = 1

# Loading inputs

Centerline = sys.argv[1]            # Polyline of network.
input_objects = sys.argv[2]         # Objects along network.  
Near_Search_Radius = sys.argv[3]    # Maximum distance between an object and the centerline.
RKM_START_QUADRANT = sys.argv[4]    # Initial quadrant network distances should be calculated with respect to.
StringIdentifier = sys.argv[5]      # String to characterize output.
workspce = sys.argv[6]              # Workspace

env.workspace = workspce

desc = arcpy.Describe(input_objects)
spatial_ref = desc.spatialReference

# Create folder to put text files
newpath = env.workspace +  "/RKMTextFilesOutputs/"
if not os.path.exists(newpath): os.makedirs(newpath)

os.chdir(workspce)
#Local variables
#Output_Event_Table_Properties = "FID POINT MEAS"

# Process: Unsplit Line
line_unsplit="in_memory\\lineUnsplit"
arcpy.UnsplitLine_management(Centerline, line_unsplit, "", "")


object1="in_memory\\obj1"

arcpy.AddField_management(input_objects, "MeanCtr", "TEXT",25)
arcpy.CalculateField_management(input_objects, "MeanCtr", "float(!FID!)", "PYTHON")
arcpy.MeanCenter_stats(input_objects, object1, "", "MeanCtr","")



# Snap objects to centerline. Snap paramaters: distance of 100 units and snapping method to "EDGE" of centerline; change these values need be.
#SnapDist="1000 Unknown"
#Snap_extra="%s EDGE '%s" %(Centerline,SnapDist)
#arcpy.Snap_edit(MeanCenterOutput,Snap_extra)


# Instead of snapping to centerline, we perform a "Near" and then create a new event layer with the NEAR_X and NEAR_Y
# This proved itself more robust than the "Snap" tool in certain circumstances

arcpy.Near_analysis(object1, line_unsplit, Near_Search_Radius, "LOCATION", "NO_ANGLE")

# Process: Make XY Event Layer
obj_Layer="in_memory\\obj1.lyr" 
arcpy.MakeXYEventLayer_management(object1, "NEAR_X", "NEAR_Y", obj_Layer, spatial_ref, "")

# Process: Copy Features
object_feat_shp = r"%s_object_feat.shp" %StringIdentifier
arcpy.CopyFeatures_management(obj_Layer, object_feat_shp, "", "0", "0", "0")

# Process: Create Routes
rkm_unsp_r="in_memory\\rkm_unsp_r"
arcpy.CreateRoutes_lr(Centerline, "Id", rkm_unsp_r, "LENGTH", "", "", RKM_START_QUADRANT, "1", "0", "IGNORE", "INDEX")
result_rkm_dbf=r"/RKMTextFilesOutputs/%s_output_RKM.dbf" %StringIdentifier

arcpy.LocateFeaturesAlongRoutes_lr(object_feat_shp,rkm_unsp_r,"Id","10000 Meters",result_rkm_dbf,"RID POINT MEAS","FIRST","DISTANCE","ZERO","FIELDS","M_DIRECTON")

arcpy.Delete_management(obj_Layer)
arcpy.Delete_management(object1)
arcpy.Delete_management(rkm_unsp_r)
arcpy.Delete_management(object_feat_shp)

# Import DBF
# Import final layer to map                          
import arcpy.mapping
# get the map document 
mxd = arcpy.mapping.MapDocument("CURRENT")  

# get the data frame 
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]  

# create a new layer 
dbf_Table = arcpy.mapping.TableView(result_rkm_dbf)

# add the layer to the map at the bottom of the TOC in data frame 0 
#arcpy.mapping.AddLayer(df, newlayer,"TOP")

arcpy.mapping.AddTableView(df,dbf_Table)

# Refresh things
arcpy.RefreshActiveView()
arcpy.RefreshTOC()
del mxd, df, dbf_Table


# Method to export to CSV
#

fc = env.workspace + "\\" + result_rkm_dbf
CSVFile = env.workspace + "/RKMTextFilesOutputs/%s_output_RKM.csv" %StringIdentifier



fields = [f.name for f in arcpy.ListFields(fc) if f.type <> 'Geometry']
with open(CSVFile, 'w') as f:
    f.write(','.join(fields)+'\n') #csv headers
    with arcpy.da.SearchCursor(fc, fields) as cursor:
        for row in cursor:
            f.write(','.join([str(r) for r in row])+'\n')

# Add output to map
mxd = arcpy.mapping.MapDocument("CURRENT")  
dataframe = arcpy.mapping.ListDataFrames(mxd,"*")[0]  
dbf_Table2 = arcpy.mapping.TableView(CSVFile)
arcpy.mapping.AddTableView(dataframe,dbf_Table2)

arcpy.RefreshActiveView()
arcpy.RefreshTOC()
del mxd, dataframe,dbf_Table2

