import arcpy,sys,os,collections
from arcpy import env


arcpy.overWriteOutputs = 1

Transects = sys.argv[1]
SmoothLine = sys.argv[2]
Case_field = sys.argv[3]
SpationJoinSelection=sys.argv[4]
rivername = sys.argv[5]
env.workspace = sys.argv[6]
RKM_START_QUADRANT = sys.argv[7]



desc1 = arcpy.Describe(Transects)
arcpy.AddMessage(desc1)
shapefilename1 = desc1.name
arcpy.AddMessage(shapefilename1)
shapefilename1 = shapefilename1[:-4]
shapefilename1 = str(shapefilename1)+ ' ' + '1'


desc2 = arcpy.Describe(SmoothLine)
shapefilename2 = desc2.name
shapefilename2 = shapefilename2[:-4]
shapefilename2 =str(shapefilename2) + ' ' + '1'

string1Intersect = str(shapefilename2) + ';'+ str(shapefilename1)



OutputIntersect = "%s_OutputIntersect.shp" %rivername
arcpy.Intersect_analysis(string1Intersect,OutputIntersect,"ALL","#","POINT")



# Call RKM toolbox and run script
arcpy.ImportToolbox("C:/AdrienWork/Hydronet2/FabWork/ToolBox_Geomorph/ToolBox_Geomorph/Fluvial_Geomorphology.tbx")

arcpy.gp.toolbox = "C:/AdrienWork/Hydronet2/FabWork/ToolBox_Geomorph/ToolBox_Geomorph/Fluvial_Geomorphology.tbx";
arcpy.gp.RKM1(SmoothLine, OutputIntersect, "FID", "15 Meters", RKM_START_QUADRANT, env.workspace, "RIVER")


# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
arcpy.MakeXYEventLayer_management("RIVER_RKM.dbf","xcoord","ycoord","in_memory/Transects_RKM_Layer","PROJCS['WGS_1984_UTM_Zone_18N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-75.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]];-5120900 -9998100 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision","#")



fieldList = arcpy.ListFields(Transects)

lst = [e.encode('utf-8') for e in SpationJoinSelection.strip('[]').split(';')]

# If user selected "FID" or "Shape", delete them from the spj because they cannot be joined
item1="Shape"
item2="FID"
if item1 in lst:  lst.remove(item1)
if item2 in lst:  lst.remove(item2)
#arcpy.AddMessage(lst)

allnames=[]
alltypes=[]
alllengths=[]
allscales=[]
allprecisions=[]
allrows=[]
allrows2=[]
frows=''
f2rows=''

for field1 in fieldList:
    fnames=[e.encode('utf-8') for e in field1.name.strip('[]').split(',')]
    allnames=fnames + allnames

    ftype=[e.encode('utf-8') for e in field1.type.strip('[]').split(',')]
    alltypes=ftype + alltypes
  
    alllengths=[field1.length]+alllengths
    
    allscales=[field1.scale]+allscales
 
    allprecisions=[field1.precision]+allprecisions
    
a=[x for x in lst if x in allnames]


index1=[]
for i in range(0,len(a),1):
    index1=[allnames.index(lst[i])]+index1



spjnames=[]
spjtypes=[]
spjlengths=[]
spjscales=[]
spjprecisions=[]

arcpy.AddMessage(index1)

for j in index1:
    spjnames=[allnames[j]]+spjnames
    spjtypes=[alltypes[j]]+spjtypes
    spjlengths=[alllengths[j]]+spjlengths
    spjscales=[allscales[j]]+spjscales
    spjprecisions=[allprecisions[j]]+spjprecisions

arcpy.AddMessage("\n" + "Field(s) " + str(spjnames) + " will be spatially joined to output.")

################################################
################################################


# Spatial join

SPJ_EXTRA=''
arcpy.AddMessage(spjnames)
for k in range(0,len(spjnames),1):

    spjnamequote='"%s"' % spjnames[k]

    STRING_X1=' '.join([spjnames[k],spjnamequote,'true true false',str(spjlengths[k]),spjtypes[k], str(spjscales[k]),str(spjprecisions[k])])
    STRING_X2=','.join(['First','#',Transects,spjnames[k],'-1','-1;']) 
    STRING_XM=','.join([STRING_X1,STRING_X2])

    SPJ_EXTRA=''.join([SPJ_EXTRA,STRING_XM])

arcpy.AddMessage("\n" + "Spatial join string: " + str(SPJ_EXTRA))

Spj_result='%s_Result_SPJ.shp' %rivername
arcpy.SpatialJoin_analysis(OutputIntersect,Transects,Spj_result,"JOIN_ONE_TO_ONE","KEEP_ALL",SPJ_EXTRA,"CLOSEST","2 Meters","#")










