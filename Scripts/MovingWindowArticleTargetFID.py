'''
MovingWindowTargetFID.py

Author
  Adrien Lepoutre
  Dept of Geography
  McGill University, Montreal, Canada
  adrien.lepoutre@mail.mcgill.ca

Date      December 2013


Purpose
  Create lateral cross-sections at locations of objects along line, using slope at point. Spatial join included.
  This is an additional script for when ArcGIS gives sql FID crash.
  A priori you won t have to use it.
Inputs:
    See 'Loading inputs' section below

Additional notes: Make sure to activate overwrite in geoprocessing.
'''


import sys, string, os, arcpy, math, arcpy.mapping,glob,csv,dbf
from arcpy import env

arcpy.ClearWorkspaceCache_management()


arcpy.overwriteoutput = True

Transects = sys.argv[1]               # Transects that will determine the spacing edges of the Polygon
WaterMask = sys.argv[2]
PolygonShape = sys.argv[3]
       
NumAggregationGeom = sys.argv[4]
AggregationOffset = sys.argv[5]
TruncatedEnd = sys.argv[6]
rasters_extract = sys.argv[7]

#Optional RKM output
#Centerline = sys.argv[8]
#RKM_START_QUADRANT = sys.argv[9] 

rivername = sys.argv[8]
workspace = sys.argv[9]

env.workspace = workspace
os.chdir(workspace)

# Number of transects that the raw geometries are built around.
RelativeSizeMW = 2
#RelativeSizeMW  = float(RelativeSizeMW)

# Offset of geometries in transects.
WindowOffset = 1
#WindowOffset = float(WindowOffset)
arcpy.AddMessage(TruncatedEnd)


NumAggregationGeom = float(NumAggregationGeom)
AggregationOffset = float(AggregationOffset)
Step = int(AggregationOffset)

desc1 = arcpy.Describe(Transects)
arcpy.AddMessage(desc1)
shapefilename1 = desc1.name
arcpy.AddMessage(shapefilename1)
shapefilename1 = shapefilename1[:-4]
shapefilename1 = str(shapefilename1)+ ' ' + '1'


desc2 = arcpy.Describe(WaterMask)
shapefilename2 = desc2.name
shapefilename2 = shapefilename2[:-4]
shapefilename2 =str(shapefilename2) + ' ' + '1'

string1Intersect = str(shapefilename2) + ';'+ str(shapefilename1)

arcpy.AddMessage(shapefilename1)
arcpy.AddMessage(shapefilename2)
arcpy.AddMessage(string1Intersect)

# Start processes
IntersectResults="%s_Intersect.shp" %rivername
arcpy.AddMessage(IntersectResults)
#arcpy.AddMessage(Transects)
arcpy.Intersect_analysis(string1Intersect,IntersectResults,"ALL","#","POINT")


IntersectResultNum = int(arcpy.GetCount_management(IntersectResults).getOutput(0))
arcpy.AddMessage(IntersectResultNum)
arcpy.MakeFeatureLayer_management(IntersectResults,"test_inter1_lyr")

# Create folder to put text files
newpath1 = env.workspace +  "/MovingWindowShapefileOutputs/"
if not os.path.exists(newpath1): os.makedirs(newpath1)

features = []

for i in range(0,int(IntersectResultNum)-2,int(WindowOffset)):
  arcpy.AddMessage(i)
  extra1=[]
  
  for j in range(i,i+int(RelativeSizeMW)):
    arcpy.AddMessage(j)
    Subextra1 =  '"TARGET_FID"=%d' %(j)
    extra1 = [Subextra1] + extra1

  extra2= ' OR '.join(extra1)
  extra2 = extra2 

  arcpy.AddMessage(extra2)
  IntersectResultsLayer="/MovingWindowShapefileOutputs/%s_intersect" %rivername
  arcpy.SelectLayerByAttribute_management("test_inter1_lyr","NEW_SELECTION",extra2)

  outputs="in_memory/test_min1_%d" %i
  arcpy.MinimumBoundingGeometry_management("test_inter1_lyr",outputs,PolygonShape,"ALL","#","NO_MBG_FIELDS")

  features.append(outputs)

arcpy.Merge_management(features, '/MovingWindowShapefileOutputs/MovingWindowOutput.shp')

arcpy.Delete_management("test_inter1_lyr")
# Part 2: Export  from each polygon record to text files
arcpy.ClearWorkspaceCache_management()

arcpy.MakeFeatureLayer_management('/MovingWindowShapefileOutputs/MovingWindowOutput.shp',"MW_lyr")
MWOutputResultNum = int(arcpy.GetCount_management('/MovingWindowShapefileOutputs/MovingWindowOutput.shp').getOutput(0))



## ##############################################################################

# Create the points, from the mask, that will be used to extract values from other elements
rasterStruct = "in_memory/rasterStructure"
arcpy.PolygonToRaster_conversion(WaterMask,"FID",rasterStruct,"CELL_CENTER","NONE","1")

pts="%soutput_pts.shp" %rivername
arcpy.RasterToPoint_conversion(rasterStruct,pts,"Value")
arcpy.AddField_management(pts, "SectionNum", "DOUBLE",15,6)

# Multivalue extraction for all rasters
arcpy.gp.ExtractMultiValuesToPoints_sa(pts,rasters_extract,"NONE")

# Make feature layer out of points
arcpy.MakeFeatureLayer_management(pts,"pts_featureLyr")

arcpy.AddField_management('/MovingWindowShapefileOutputs/MovingWindowOutput.shp', "SectionNum", "TEXT","", "", 50)
arcpy.AddField_management("pts_featureLyr", "SectionNum", "DOUBLE",15,6)

## ############################################################################
# Get fieldnames 
fieldList = arcpy.ListFields(pts)
allfieldnames=[]
for field in fieldList:
    fnames=[e.encode('utf-8') for e in field.name.strip('[]').split(',')]
    allfieldnames = fnames + allfieldnames

item1="Shape"
if item1 in allfieldnames:  allfieldnames.remove(item1)

arcpy.AddMessage(allfieldnames)


# Start extracting points

MWshp_SectionNum = []

# Option to truncate last polygon to the last multiple of the inputted "Number of geometries to Aggregate":
if TruncatedEnd == "true" :
  RoundedMWOutputResultNum = int(NumAggregationGeom * round(float(MWOutputResultNum)/NumAggregationGeom))
  AggregationLoopEnd = int((RoundedMWOutputResultNum - NumAggregationGeom))
  arcpy.AddMessage(" THE ROUNDED VALUE IS: " + str(RoundedMWOutputResultNum))

  SectionNumberList = range(0,len(range(0,RoundedMWOutputResultNum,Step)),1)
  kList=range(0,RoundedMWOutputResultNum,Step)

  
else:
  arcpy.AddMessage("MWOutputResultNum: " + str(MWOutputResultNum))
  AggregationLoopEnd = MWOutputResultNum

  SectionNumberList = range(0,len(range(0,MWOutputResultNum,Step)),1)
  kList=range(0,MWOutputResultNum,Step)

# Create folder to put text files

newpath2 = env.workspace +  "/MovingWindowTextFilesOutputs/"
if not os.path.exists(newpath2): os.makedirs(newpath2)

for kj in SectionNumberList:

  MWshp_SectionNum = MWshp_SectionNum + [kj]
  
  k=kList[kj]
  extra3=[]
  for h in range(k,k+int(RoundedMWOutputResultNum)):
    Subextra3 =  '"FID"=%d' %(h)
    extra3 = [Subextra3] + extra3

  extra3= ' OR '.join(extra3)
  extra3 = extra3


  arcpy.AddMessage(extra3)
  arcpy.SelectLayerByAttribute_management("MW_lyr","NEW_SELECTION",extra3)
  textfile="MovingWindowTextFilesOutputs/MW_output_%04d.txt" %SectionNumberList[kj]
  arcpy.AddMessage(textfile)
  arcpy.SelectLayerByLocation_management("pts_featureLyr","WITHIN","MW_lyr","#","NEW_SELECTION")
  arcpy.AddMessage(SectionNumberList[kj])                        
  arcpy.CalculateField_management("pts_featureLyr","SectionNum",int(SectionNumberList[kj]),"PYTHON_9.3","#")
  arcpy.ExportXYv_stats("pts_featureLyr",allfieldnames,"SPACE",textfile,"ADD_FIELD_NAMES")

arcpy.Delete_management("pts_featureLyr")
arcpy.Delete_management("MW_lyr")

##               Insert if condition of outputting files

## Add output to map
#mxd = arcpy.mapping.MapDocument("CURRENT")  
#dataframe = arcpy.mapping.ListDataFrames(mxd,"*")[0]  
#newlayer1 = arcpy.mapping.Layer('/MovingWindowShapefileOutputs/MovingWindowOutput.shp')
#arcpy.mapping.AddLayer(dataframe, newlayer1,"TOP")

## Refresh 
#arcpy.RefreshActiveView()
#arcpy.RefreshTOC()
#del newlayer1,dataframe,mxd

################################################################################################
                                #  part 2: Moving Window Visual#
################################################################################################

# Get the number of geometries
MWOutputResultNum = int(arcpy.GetCount_management("/MovingWindowShapefileOutputs/MovingWindowOutput.shp").getOutput(0))
arcpy.AddMessage(MWOutputResultNum)

#Create feature layer from geometries shapefile
arcpy.CopyFeatures_management("/MovingWindowShapefileOutputs/MovingWindowOutput.shp","MWO_copy.shp","#","0","0","0")
arcpy.MakeFeatureLayer_management("MWO_copy.shp","MWO_poly_lyr")

features = []
alldissolved_items = []

for i in range(0,int(AggregationLoopEnd),Step):

    ii = int(NumAggregationGeom + int(i))
    #arcpy.AddMessage("ii is equal to: " + str(ii))
    extra1=[]
    for j in range(i,ii):
        
        Subextra1 =  '"FID"=%d' %(j)
        extra1 = [Subextra1] + extra1

    extra2= ' OR '.join(extra1)   
    arcpy.AddMessage(extra2)
    
    arcpy.SelectLayerByAttribute_management("MWO_poly_lyr","NEW_SELECTION",extra2)
    selection_outputs = "in_memory/selection_%04d" %(i)
    arcpy.CopyFeatures_management("MWO_poly_lyr",selection_outputs,"#","0","0","0")
    
    #arcpy.AddMessage(arcpy.GetCount_management(selection_outputs).getOutput(0))
    dissolved_item= "in_memory/dissolve_item_%04d" %(i)
    alldissolved_items = alldissolved_items +[dissolved_item]
    arcpy.Dissolve_management(selection_outputs,dissolved_item,"#","#","SINGLE_PART","DISSOLVE_LINES")


## Create list of unicode for all object directories in env.workspace

#arcpy.AddMessage(alldissolved_items)

merge_extra1 = []
merge_extra2= []
for h in alldissolved_items:

    merge_SubExtra1 = '%s' %h
    merge_extra1 = merge_extra1 + [merge_SubExtra1]
    
   
    merge_Subextra2 =  'Id "Id" true true false 6 Long 0 6 ,First,#,%s,' %h
    merge_extra2 = merge_extra2 + [merge_Subextra2]
    

merge_extra1= ';'.join(merge_extra1)
merge_extra2 = "','".join(merge_extra1)


MovingWindowVisualOutput = "/MovingWindowShapefileOutputs/%sAggregatedMovingWindow.shp" %rivername
arcpy.Merge_management(merge_extra1,MovingWindowVisualOutput,merge_extra2)

arcpy.AddField_management(MovingWindowVisualOutput, "SectionNum", "TEXT","", "", 50)
arcpy.CalculateField_management(MovingWindowVisualOutput,"SectionNum","!FID!","PYTHON_9.3","#")


# Add output to map
mxd = arcpy.mapping.MapDocument("CURRENT")  
dataframe = arcpy.mapping.ListDataFrames(mxd,"*")[0]  
MapLayer2 = arcpy.mapping.Layer(MovingWindowVisualOutput)
arcpy.mapping.AddLayer(dataframe, MapLayer2,"TOP")

arcpy.RefreshActiveView()
arcpy.RefreshTOC()
del MapLayer2, mxd, dataframe

# Delete layer
arcpy.Delete_management("MWO_poly_lyr")

arcpy.ClearWorkspaceCache_management()
###############################################################################################

                                    ## PART 3: RKM (change name) ##

###############################################################################################
# RKM if condition
#if Centerline <> "#":
  
#  Near_Search_Radius = 100000   # Maximum distance between two objects.


  # Unsplit Line
#  line_unsplit="in_memory/lineUnsplit"
#  arcpy.UnsplitLine_management(Centerline, line_unsplit, "", "")

#  arcpy.CopyFeatures_management(MovingWindowVisualOutput,"in_memory/MWVO_copy","#","0","0","0")
#  arcpy.MakeFeatureLayer_management("in_memory/MWVO_copy","MWVO_poly_lyr")

  # Create a field on which the mean center can be aggregated. We copy the FID to make a mean center feature per object
#  arcpy.AddField_management(MovingWindowVisualOutput, "MeanCtr", "TEXT",25)
#  arcpy.CalculateField_management(MovingWindowVisualOutput, "MeanCtr", "float(!FID!)", "PYTHON")
#  MeanCenterOutput = '/MovingWindowShapefileOutputs/%sRKMOutput.shp' %rivername
#  arcpy.MeanCenter_stats(MovingWindowVisualOutput,MeanCenterOutput,"#","MeanCtr","#")


  ## Add to map
#  mxd = arcpy.mapping.MapDocument("CURRENT")  
#  dataframe = arcpy.mapping.ListDataFrames(mxd,"*")[0]  
#  MCO_Layer = arcpy.mapping.Layer(MeanCenterOutput)
#  arcpy.mapping.AddLayer(dataframe, MCO_Layer,"TOP")

#  arcpy.RefreshActiveView()
#  arcpy.RefreshTOC()
#  del MCO_Layer, mxd, dataframe




  # Snap objects to centerline. Snap paramaters: distance of 100 units and snapping method to "EDGE" of centerline; change these values need be.
#  SnapDist="100 Unknown"
#  Snap_extra="%s EDGE '%s" %(Centerline,SnapDist)
#  arcpy.Snap_edit(MeanCenterOutput,Snap_extra)


########################################RKM toolbox#######################################
#   desc = arcpy.Describe(MovingWindowVisualOutput)
#  spatial_ref = desc.spatialReference

  # Process: Near
#  arcpy.Near_analysis(MeanCenterOutput, line_unsplit, Near_Search_Radius, "LOCATION", "NO_ANGLE")

  # Process: Make XY Event Layer
#  obj_Layer = "in_memory\\obj1.lyr"
#  arcpy.MakeXYEventLayer_management(MeanCenterOutput, "NEAR_X", "NEAR_Y", obj_Layer, "", "")

  # Process: Copy Features
#  object_feat_shp="/MovingWindowShapefileOutputs/%sobject_feat.shp" %rivername
#  arcpy.CopyFeatures_management(obj_Layer, object_feat_shp, "", "0", "0", "0")


  # Process: Create Routes
#  rkm_unsp_r = "in_memory/rkm_unsp_r"

#  arcpy.CreateRoutes_lr(Centerline, "Id", rkm_unsp_r, "LENGTH", "", "", RKM_START_QUADRANT, "1", "0", "IGNORE", "INDEX")
#  result_rkm_dbf = "%soutput_RKM.dbf" %rivername


#  arcpy.LocateFeaturesAlongRoutes_lr(object_feat_shp,rkm_unsp_r,"Id","100000 Meters",result_rkm_dbf,"RID POINT MEAS","FIRST","DISTANCE","ZERO","FIELDS","M_DIRECTON")

  ## Import final layer to map                          
#  mxd = arcpy.mapping.MapDocument("CURRENT")  
#  dataframe = arcpy.mapping.ListDataFrames(mxd,"*")[0]  
#  dbf_Table = arcpy.mapping.TableView(result_rkm_dbf)
#  arcpy.mapping.AddTableView(dataframe,dbf_Table)

  ## Refresh things
#  arcpy.RefreshActiveView()
#  arcpy.RefreshTOC()
#  del mxd,dataframe,dbf_Table
##########################################################################################

# Method to export to CSV
# written by sgrieve accessed oct. 10, 2013 on http://gis.stackexchange.com/questions/42433/how-to-export-only-certain-columns-to-a-csv-file-in-arcgis


#  fc = env.workspace + "\\" + result_rkm_dbf
#  CSVFile = env.workspace + "\%soutput_RKM.csv" %rivername

  #arcpy.AddMessage(CSVFile)

#  fields = [f.name for f in arcpy.ListFields(fc) if f.type <> 'Geometry']
#  with open(CSVFile, 'w') as f:
#      f.write(','.join(fields)+'\n') #csv headers
#      with arcpy.da.SearchCursor(fc, fields) as cursor:
#          for row in cursor:
#              f.write(','.join([str(r) for r in row])+'\n')

# Add output to map
#  mxd = arcpy.mapping.MapDocument("CURRENT")  
#  dataframe = arcpy.mapping.ListDataFrames(mxd,"*")[0]  
#  dbf_Table2 = arcpy.mapping.TableView(CSVFile)
#  arcpy.mapping.AddTableView(dataframe,dbf_Table2)

#  arcpy.RefreshActiveView()
#  arcpy.RefreshTOC()
#  del mxd, dataframe,dbf_Table2

# To delete

#  arcpy.Delete_management(object_feat_shp)

#arcpy.Delete_management("MWO_copy.shp")

