'''
Patches names.py

Author
  Adrien Lepoutre
  Dept of Geography
  McGill University, Montreal, Canada
  adrien.lepoutre@mail.mcgill.ca

Date      July 2013


Purpose
  Add the names of the point couples (patches) to inputted objects.


Inputs:
    See 'Loading inputs' section below




import arcpy,sys,os,collections
from arcpy import env


Input_pts=sys.argv[1]
Case_field=sys.argv[2]
Patches_shp=sys.argv[3]
Search_radius=sys.argv[4]
rivername=sys.argv[5]
workspce=sys.argv[6]

env.workspace = workspce
arcpy.overWriteOutputs = 1
os.chdir(workspce)

#
Input_pts_copy = '%s_pts_copy.shp' %rivername
arcpy.CopyFeatures_management(Input_pts, Input_pts_copy)

fieldList = arcpy.ListFields(Input_pts_copy)

lst = [e.encode('utf-8') for e in Case_field.strip('[]').split(';')]

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

# Extracting all the informations from the shapefiles by first creating a list of the indexes:

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
#


OutputMeanCenter='%s_out_mcenter.shp' %rivername
arcpy.MeanCenter_stats(Input_pts,OutputMeanCenter,"#",Case_field,"#")

# Spatial join
# Create joined strings to load up as input in spj join

SPJ_EXTRA=''
arcpy.AddMessage(spjnames)
for k in range(0,len(spjnames),1):

    spjnamequote='"%s"' % spjnames[k]

    STRING_X1=' '.join([spjnames[k],spjnamequote,'true true false',str(spjlengths[k]),spjtypes[k], str(spjscales[k]),str(spjprecisions[k])])
    STRING_X2=','.join(['First','#',Input_pts_copy,spjnames[k],'-1','-1;']) 
    STRING_XM=','.join([STRING_X1,STRING_X2])

    SPJ_EXTRA=''.join([SPJ_EXTRA,STRING_XM])

arcpy.AddMessage("\n" + "Spatial join string: " + str(SPJ_EXTRA))

Spj_result='%s_patches_names.shp' %rivername
arcpy.SpatialJoin_analysis(Patches_shp,OutputMeanCenter,Spj_result,"JOIN_ONE_TO_ONE","KEEP_ALL",SPJ_EXTRA,"CLOSEST",Search_radius,"#")


#arcpy.SpatialJoin_analysis("New_Shapefile(2)","New_Shapefile_mcenter","C:/Users/alepou.CAMPUS.000/ToolBox_Geomorph/test-shp/New_Shapefile_spj.shp","JOIN_ONE_TO_ONE","KEEP_COMMON",result,"CLOSEST","50 Meters","#"
rows = arcpy.SearchCursor(Spj_result)

for row in rows:
    frows=row.getValue(Case_field)
    frows=[e.encode('utf-8') for e in frows.strip('[]').split(',')]
    #arcpy.AddMessage(frows))
    allrows=frows + allrows

#arcpy.AddMessage(allrows)
#arcpy.AddMessage(type(allrows))

# Check list of rows in title field
rows2 = arcpy.SearchCursor(Input_pts)

for row2 in rows2:
    frows2=row2.getValue(Case_field)
    frows2=[e.encode('utf-8') for e in frows2.strip('[]').split(',')]
    #arcpy.AddMessage(frows2))
    allrows2=frows2 + allrows2

#arcpy.AddMessage(allrows2)
#arcpy.AddMessage(type(allrows2))


spj_names=set(allrows)
initial_names=set(allrows2)

arcpy.AddMessage(spj_names)
arcpy.AddMessage(initial_names)

if collections.Counter(spj_names) == collections.Counter(initial_names):
    arcpy.AddMessage("\n"+"Spatially joined Case_field has same length as initial field: result should be good but check for cross-associations.")
else:
    arcpy.AddMessage("\n"+"Spj field and Case_field lengths are not equal: spatial method incorrect.")




# Import final layer to map                          
import arcpy.mapping
# get the map document 
mxd = arcpy.mapping.MapDocument("CURRENT")  

# get the data frame 
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]  

# create a new layer 
newlayer = arcpy.mapping.Layer(Spj_result)

# add the layer to the map at the bottom of the TOC in data frame 0 
arcpy.mapping.AddLayer(df, newlayer,"TOP")

# Refresh things
arcpy.RefreshActiveView()
arcpy.RefreshTOC()
del mxd, df, newlayer

