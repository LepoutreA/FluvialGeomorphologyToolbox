
'''
LocalMovingWindow.py

Author
  Adrien Lepoutre
  Dept of Geography
  McGill University, Montreal, Canada
  adrien.lepoutre@mail.mcgill.ca

Date      July 2013


Purpose
Creates polygons around couples of points associated by a same field attribute name.
This polygon then extracts raster data. Optional additional transects.



Inputs:
    See 'Loading inputs' section below
'''


import csv, arcpy
import sys,os, numpy
from arcpy import env

#Loading inputs
BioPatchesPoints = sys.argv[1]
Transects = sys.argv[2]
Centerline = sys.argv[3]
watermask = sys.argv[4]
PolygonShape = sys.argv[5]
ExtraTransects = sys.argv[6]
rasters_extract = sys.argv[7]
OptionalSpatialJoinObject = sys.argv[8]
StringIdentifier = sys.argv[9]
workspace = sys.argv[10]

env.workspace = workspace
if ExtraTransects <> "#":
    adTransects = int(ExtraTransects)

else:
    adTransects = 0


######################## Part 1: Extract specific transects from the initial biopoints #################

BioPatchesPointsSnapped = "in_memory/BioPatchesPointsSnapped"
arcpy.CopyFeatures_management(BioPatchesPoints,BioPatchesPointsSnapped,"#","0","0","0")

SnapDist = '300 Unknown'
Snap_extra="%s EDGE '%s" %(Centerline,SnapDist)
arcpy.Snap_edit(BioPatchesPointsSnapped,Snap_extra)

# Extract only bio patches inside watermask
BufferBioPatchesPointsSnapped = "in_memory/redPoints"
arcpy.Buffer_analysis(BioPatchesPointsSnapped,BufferBioPatchesPointsSnapped,"10 Meters","FULL","ROUND","NONE","#")
watermask_lyr = "watermask_lyr"
BufferBioPatchesPointsSnapped_lyr ="redPoints_lyr"
arcpy.MakeFeatureLayer_management(watermask,watermask_lyr)
arcpy.MakeFeatureLayer_management(BufferBioPatchesPointsSnapped,BufferBioPatchesPointsSnapped_lyr)
arcpy.SelectLayerByLocation_management(BufferBioPatchesPointsSnapped_lyr,"INTERSECT",watermask_lyr,"#","NEW_SELECTION")
BufPatchesPointsSnappedCut = "CutBuffers.shp"
arcpy.CopyFeatures_management(BufferBioPatchesPointsSnapped_lyr,BufPatchesPointsSnappedCut,"#","0","0","0")
#

# Option for spatial join for large windows, use already created MergedGeometries object
#if OptionalSpatialJoinObject == "#":
#    OptionalSpatialJoinObject = BufPatchesPointsSnappedCut
#   SJP_OPERATION = "CONTAINS"
#else:
OptionalSpatialJoinObject=OptionalSpatialJoinObject
SJP_OPERATION = "CLOSEST"


Transects_lyr = "Transects_lyr"
arcpy.MakeFeatureLayer_management(Transects, Transects_lyr)

BufPatchesPointsSnappedCut_lyr = "BufPatchesPointsSnappedCut_lyr"
arcpy.MakeFeatureLayer_management(BufPatchesPointsSnappedCut, BufPatchesPointsSnappedCut_lyr)

#

######################## Part 2: Use incremental buffer selection to get all necessary transects to have TARGET_FID to build geometries ######################


TransectsPts_lyr ="TransectsPts_lyr"
SelectionTextFile = r"SelectionTextFile.txt"

cursor = arcpy.SearchCursor(BufPatchesPointsSnappedCut)

BufferBioNum = int(arcpy.GetCount_management(BufPatchesPointsSnappedCut).getOutput(0))
features1 =[]
arcpy.AddMessage(BufferBioNum)
for h in range(0, BufferBioNum):

    arcpy.AddMessage(h)
    extra = '"FID"=%s' %(h)
    arcpy.SelectLayerByAttribute_management(BufPatchesPointsSnappedCut_lyr,"NEW_SELECTION",extra)
    arcpy.SelectLayerByLocation_management(Transects_lyr,"INTERSECT",BufPatchesPointsSnappedCut_lyr,"#","NEW_SELECTION")
    out = "in_memory/test1_%d" %h
    arcpy.CopyFeatures_management(Transects_lyr,out,"#","0","0","0")
    features1.append(out)

SelectedTransects = 'SelectedTransects1.shp'    
arcpy.Merge_management(features1, SelectedTransects)


# Make string for intersect

desc1 = arcpy.Describe(Transects)
arcpy.AddMessage(desc1)
shapefilename1 = desc1.name
arcpy.AddMessage(shapefilename1)
shapefilename1 = shapefilename1[:-4]
shapefilename1 =  str(shapefilename1)+ ' ' + '1'


desc2 = arcpy.Describe(watermask)
shapefilename2 = desc2.name
shapefilename2 = shapefilename2[:-4]
shapefilename2 =str(shapefilename2) + ' ' + '1'

string1Intersect = str(shapefilename2) + ';'+ str(shapefilename1)
IntersectResults="Intersect.shp" 
arcpy.Intersect_analysis(string1Intersect,IntersectResults,"ALL","#","POINT")
arcpy.MakeFeatureLayer_management(IntersectResults, TransectsPts_lyr)


# Write TARGET_FID shp column to text file #

#outFile = open(r"SelectionTextFile.txt", "w")
NewIndex = []
#fcSearch = arcpy.da.SearchCursor(SelectedTransects, ["TARGET_FID"])
fcSearch = arcpy.da.SearchCursor(SelectedTransects, ["File_ID"])
#print fcSearch
#count = 0
for fcRow in fcSearch:

    NewIndex += [fcRow[0]]
    print fcRow[0]
    #outFile.write(str(fcRow[0]) + "\n")
#outFile.close()    # This closes the text file
del fcRow, fcSearch


# Correct list for duplicate elements
NewIndex = sorted(NewIndex)
arcpy.AddMessage(NewIndex)
y=[x for x in NewIndex if NewIndex.count(x) > 1]
yInd = [i for i,x in enumerate(NewIndex) if NewIndex.count(x) > 1]
for j in range(0,(len(y)/4)):
    NewIndex[yInd[j]] = NewIndex[yInd[j]]
    NewIndex[yInd[j+1]] = NewIndex[yInd[j+2]]
    NewIndex[yInd[j+2]] = NewIndex[yInd[j]]
    NewIndex[yInd[j+3]] = NewIndex[yInd[j+3]]
print NewIndex


arcpy.AddMessage(NewIndex)

######################## Part 3: Select only specific item in sorted list and create geometries

# Get number of geometries
MWOutputResultNum = int(arcpy.GetCount_management(SelectedTransects).getOutput(0))
arcpy.AddMessage(MWOutputResultNum)
features = []

#Loop to create 2 geometries, one small for spj and one that has the final size
RangeGeom = [0, adTransects]
for k in range(0,len(RangeGeom)):
    adTransects = RangeGeom[k]

    GGoutputs="GG_%d.shp" %adTransects
    arcpy.AddMessage(GGoutputs)

    for i in range(0, MWOutputResultNum-3, 4):
        FirstLimit = int(NewIndex[i]) - adTransects
        LastLimit = (int(NewIndex[i+3])+1) + adTransects
        index2 = range(FirstLimit,LastLimit)
        arcpy.AddMessage(index2)



    
    

# Make loop to select specific windows
        extra1=[]
    
        for j in index2:
        
            Subextra1 =  '"File_ID"=%s' %(j)
            extra1 = [Subextra1] + extra1

        extra2= ' OR '.join(extra1)   
        arcpy.AddMessage(extra2)

        print extra2

        arcpy.SelectLayerByAttribute_management(TransectsPts_lyr,"NEW_SELECTION",extra2)

    #GeometryLocation = ([index1].index(j))/4    #arcpy.AddMessage()
        outputs="in_memory/test_min1_%d_%d" %(i,adTransects)
        arcpy.MakeFeatureLayer_management(TransectsPts_lyr,"test_inter1_lyr")
    #PolygonShape = "CONVEX_HULL"
        arcpy.MinimumBoundingGeometry_management("test_inter1_lyr",outputs,PolygonShape,"ALL","#","NO_MBG_FIELDS")

        features.append(outputs)

    #MergedGeometries = 'MergeGeometries.shp'
    arcpy.Merge_management(features,  GGoutputs)
    GGoutputsSpj = "GG_%d_spj.shp" %(adTransects)
    
    if k == 0:
        extra_spj = """Site "Site" true true false 80 Text 0 0 ,First,#,%s,Site,-1,-1""" %BufPatchesPointsSnappedCut
        OptionalSpatialJoinObject = BufPatchesPointsSnappedCut
        SJP_OPERATION = "CLOSEST"
        #GGoutputsSpj ="test.shp"
        arcpy.SpatialJoin_analysis(GGoutputs,OptionalSpatialJoinObject,GGoutputsSpj,"JOIN_ONE_TO_ONE","KEEP_ALL",extra_spj,SJP_OPERATION,"#","#")
        MergedGeometriesSpjPrevious = GGoutputsSpj
    else:
        MergedGeometriesSpjPrevious = "GG_%d_spj.shp" %RangeGeom[k-1]
        extra_spj = """Site "Site" true true false 80 Text 0 0 ,First,#,%s,Site,-1,-1""" %MergedGeometriesSpjPrevious
        OptionalSpatialJoinObject = MergedGeometriesSpjPrevious

    arcpy.AddMessage(str(GGoutputs))
    arcpy.AddMessage(str(OptionalSpatialJoinObject))
    arcpy.AddMessage(str(GGoutputsSpj))
    #arcpy.AddMessage(str(MergedGeometriesSpjPrevious))
    arcpy.AddMessage(extra_spj)
    
    #arcpy.SpatialJoin_analysis(GGoutputs,OptionalSpatialJoinObject,GGoutputsSpj,"JOIN_ONE_TO_ONE","KEEP_ALL",extra_spj,SJP_OPERATION,"#","#")

    features =[]

if k == 0:
    MergedGeometriesSpjPrevious_lyr = "MergedGeometriesSpjPrevious_lyr"
    GGoutputs_lyr = "GGoutputs_lyr"
    arcpy.MakeFeatureLayer_management(GGoutputsSpj,MergedGeometriesSpjPrevious_lyr)
    arcpy.MakeFeatureLayer_management(GGoutputs,GGoutputs_lyr)
    MergedGeometriesSpj = GGoutputsSpj
    
else:
    SpjResultNum = int(arcpy.GetCount_management(GGoutputs).getOutput(0))
    cursor1 = arcpy.SearchCursor(GGoutputs)

    # Preparation for selection spj
    MergedGeometriesSpjPrevious_lyr = "MergedGeometriesSpjPrevious_lyr"
    GGoutputs_lyr = "GGoutputs_lyr"
    arcpy.MakeFeatureLayer_management(MergedGeometriesSpjPrevious,MergedGeometriesSpjPrevious_lyr)
    arcpy.MakeFeatureLayer_management(GGoutputs,GGoutputs_lyr)
    featuresAtt = []

    for row in cursor1:
        print row.getValue("FID")
    
        FIDrowValue1 = row.getValue("FID")

        extra0= '"FID"=%s' %(FIDrowValue1)
        MergedGeometriesSpjPrevious = "GG_%d_spj.shp" %RangeGeom[k-1]
        arcpy.SelectLayerByAttribute_management(MergedGeometriesSpjPrevious_lyr,"NEW_SELECTION",extra0)
        arcpy.SelectLayerByAttribute_management(GGoutputs_lyr,"NEW_SELECTION",extra0)
        GGoutputsSpj="GG_Spj_%3d.shp" %(FIDrowValue1)
        arcpy.SpatialJoin_analysis(GGoutputs_lyr,MergedGeometriesSpjPrevious_lyr,GGoutputsSpj,"JOIN_ONE_TO_ONE","KEEP_ALL",extra_spj,SJP_OPERATION,"#","#")

        featuresAtt.append(GGoutputsSpj)

    MergedGeometriesSpj = "%s_mergedGeomSpj.shp" %(StringIdentifier)
    arcpy.Merge_management(featuresAtt,  MergedGeometriesSpj)
    

########

## Create the points, from the mask, that will be used to extract values from other elements
rasterStruct = "in_memory/rasterStructure"
arcpy.PolygonToRaster_conversion(watermask,"FID",rasterStruct,"CELL_CENTER","NONE","1")

pts="%soutput_pts.shp" %StringIdentifier
arcpy.RasterToPoint_conversion(rasterStruct,pts,"Value")
#arcpy.AddField_management(pts, "PatchNum", "DOUBLE",15,6)
arcpy.AddField_management(pts, "PatchNum", "TEXT","", "", 50)
# Multivalue extraction for all rasters
arcpy.gp.ExtractMultiValuesToPoints_sa(pts,rasters_extract,"NONE")

# Make feature layer out of points
arcpy.MakeFeatureLayer_management(pts,"pts_featureLyr")

#########

#Spatial join sites to merged geometries
#MergedGeometriesSpj = "MergeGeometriesSpj.shp"
#extra_spj = """Site "Site" true true false 80 Text 0 0 ,First,#,%s,Site,-1,-1""" %BioPatchesPoints
#BufPatchesPointsSnappedCutSpj = "BufPatchesPointsSnappedCutSpj.shp"
#arcpy.SpatialJoin_analysis(BufPatchesPointsSnappedCut,BufferBioPatchesPointsSnapped,BufPatchesPointsSnappedCutSpj,"JOIN_ONE_TO_ONE","KEEP_ALL",extra_spj,"CLOSEST","#","#")
#extra_spj = """Site "Site" true true false 80 Text 0 0 ,First,#,%s,Site,-1,-1""" %OptionalSpatialJoinObject
#arcpy.SpatialJoin_analysis(MergedGeometries,OptionalSpatialJoinObject,MergedGeometriesSpj,"JOIN_ONE_TO_ONE","KEEP_ALL",extra_spj,SJP_OPERATION,"#","#")




#SepLinesOrd="in_memory\\SepLOrd" 
#extra_order="""OrderObj "OrderObj" true true false 16 Double 6 15 ,First,#,%s,OrderObj,-1,-1""" %object1
#arcpy.SpatialJoin_analysis(SepLines,object1,SepLinesOrd,"JOIN_ONE_TO_ONE","KEEP_ALL",extra_order,"INTERSECT","#","#")
    




## Get fieldnames 
fieldList = arcpy.ListFields(pts)
allfieldnames=[]
for field in fieldList:
    fnames=[e.encode('utf-8') for e in field.name.strip('[]').split(',')]
    allfieldnames = fnames + allfieldnames

item1="Shape"
if item1 in allfieldnames:  allfieldnames.remove(item1)


arcpy.AddMessage(allfieldnames)


# Extract text file
# Create folder to put text files

#LocalSectionNumberList = range(0,len(range(0,MergedGeometriesSpj)),1)

newpath2 = env.workspace +  "/LocalMovingWindowTextFilesOutputs/"
if not os.path.exists(newpath2): os.makedirs(newpath2)

MergedGeometriesSpj_lyr = "MergedGeometriesSpj_lyr"
arcpy.MakeFeatureLayer_management(MergedGeometriesSpj,MergedGeometriesSpj_lyr)


cursor = arcpy.SearchCursor(MergedGeometriesSpj)
for row in cursor:
    print row.getValue("FID")
    
    FIDrowValue = row.getValue("FID")
    SiterowValue = row.getValue("Site")
    NewIndex += [FIDrowValue]

    textfile="LocalMovingWindowTextFilesOutputs/LMW_output_%04d_%s.txt" %(FIDrowValue,SiterowValue)
    arcpy.AddMessage(textfile)
    #FIDrowValue = [FIDrowValue]
    Subextra5= '"FID"=%s' %(FIDrowValue)
    #Subextra1 =  '"TARGET_FID"=%s' %(j)
    #Subbextra1 = [Subbextra1]
    arcpy.SelectLayerByAttribute_management(MergedGeometriesSpj_lyr,"NEW_SELECTION",Subextra5)
    arcpy.SelectLayerByLocation_management("pts_featureLyr","WITHIN",MergedGeometriesSpj_lyr,"#","NEW_SELECTION")

    SiterowValueStr= '"' + str(SiterowValue) + '"'
    arcpy.AddMessage(str(SiterowValue))
    #test ="'Hello_World'"
    #arcpy.AddMessage(test)
    arcpy.CalculateField_management("pts_featureLyr","PatchNum",SiterowValueStr,"PYTHON","")
    arcpy.ExportXYv_stats("pts_featureLyr",allfieldnames,"SPACE",textfile,"ADD_FIELD_NAMES")

arcpy.Delete_management("pts_featureLyr")
#arcpy.Delete_management("pts_featureLyr")
arcpy.Delete_management(MergedGeometriesSpj_lyr)



# Add output to map
mxd = arcpy.mapping.MapDocument("CURRENT")  
dataframe = arcpy.mapping.ListDataFrames(mxd,"*")[0]  
MapLayer2 = arcpy.mapping.Layer(MergedGeometriesSpj)
arcpy.mapping.AddLayer(dataframe, MapLayer2,"TOP")

arcpy.RefreshActiveView()
arcpy.RefreshTOC()
del MapLayer2, mxd, dataframe

# Delete layer
#arcpy.Delete_management("MWO_poly_lyr")

#arcpy.ClearWorkspaceCache_management()

    

