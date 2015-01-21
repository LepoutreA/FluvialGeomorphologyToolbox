'''
Densify.py

Author
  Dan Patterson
  Dept of Geography and Environmental Studies
  Carleton University, Ottawa, Canada
  Dan_Patterson@carleton.ca

Date      March 2008
Modified  Sept 2011

Purpose
  densifies points forming line segments.  currently requires point input for testing

Properties (right-click on the tool and specify the following)
General
  Name   Densify
  Label  Densify
  Desc   Densifies polyline or polygon files using a step increment to
         add vertices between segments

Source script Densify.py

Requires:  DensifyHelper.py

Parameter list
                                Parameter Properties
           Display Name         Data type        Type      Direction  MultiValue
  argv[1]  Input layer          Feature Layer    Required  Input      No
  argv[2]  step size            Double           Required  Input      No
  argv[3]  Output poly* file    Feature class    Optional  Output     No
  argv[4]  Poly* type           String           Optional  Input      No
           Domain: Polyline, Polygon  Default: Polyline
  argv[5]  Optional point file  Feature class    Optional  Output     No
'''
#--------------------------------------------------------------------
#Main portion
import os, sys, math
import arcpy
import DensifyHelper      #load the helper script after arcpy is created
from arcpy import env

arcpy.OverWriteOutput = 1
desc = arcpy.Describe
#inFC = sys.argv[1]

#inFC = arcpy.GetParameterAsText(0)
#if inFC == '#' or not inFC:
#    inFC = "inFC" # provide a default value if unspecified


inFC=sys.argv[1]
stepBy = float(sys.argv[2])
outType = sys.argv[3]
#outPoint = sys.argv[4]
#arcpy.AddMessage(sys.argv[4])
Depth_Image=sys.argv[4]


if stepBy <= 0.0:
  arcpy.AddMessage("\n" + "A positive non-zero step value is required." + "\n")
  sys.exit()
#
outPoly="#"
if outPoly != "#":
  outPoly = outPoly.replace("\\","/")
  fullName = os.path.split(outPoly)
  outFolder = fullName[0].replace("\\", "/")
shapeClass = desc(inFC).ShapeType

#
if shapeClass.lower().find("poly") < 0:
  arcpy.AddMessage("\n" + "Requires a polyline/polygon file...bailing" + "\n")
  sys.exit()
else:
  arcpy.AddMessage("\n" + "Processing " + inFC + " " + shapeClass)


################################

OrderName = arcpy.GetParameterAsText(4)
if OrderName == '#' or not OrderName:
    OrderName = "OrderName" # provide a default value if unspecified

rivername = arcpy.GetParameterAsText(5)
if rivername == '#' or not rivername:
    rivername = "rivername" # provide a default value if unspecified

workspce = arcpy.GetParameterAsText(6)
if workspce == '#' or not workspce:
    workspce = "workspce" # provide a default value if unspecified

env.workspace = workspce
arcpy.overWriteOutputs = 1
os.chdir(workspce)

arcpy.AddMessage(workspce)


Input_CS=inFC

Input_CS_copy = 'in_memory\\CS_copy'
#arcpy.AddMessage(Input_CS_copy)
outPoint="%s\%s_CS_points.shp" %(workspce,rivername)


arcpy.CopyFeatures_management(Input_CS, Input_CS_copy)

fieldList = arcpy.ListFields(Input_CS_copy)

lst = [e.encode('utf-8') for e in OrderName.strip('[]').split(';')]
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

for field in fieldList:
    g=[e.encode('utf-8') for e in field.name.strip('[]').split(',')]
    allnames=g + allnames

    ftype=[e.encode('utf-8') for e in field.type.strip('[]').split(',')]
    alltypes=ftype + alltypes
  
    alllengths=[field.length]+alllengths
    
    allscales=[field.scale]+allscales
 
    allprecisions=[field.precision]+allprecisions
    

#print allnames
#print alltypes
#print alllengths
#print allscales
#print allprecisions
    
#arcpy.AddMessage(allnames)
#arcpy.AddMessage(alltypes)
#arcpy.AddMessage(alllengths)
#arcpy.AddMessage(allscales)
#arcpy.AddMessage(allprecisions)


a=[x for x in lst if x in allnames]

#SPJ PREPARATION: Extracting all the informations from the shapefiles by first creating a list of the indexes:

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


arcpy.AddMessage("\n" + "Fields:" + str(spjnames) + " will be spatially joined to output.")

##########################

OIDField = desc(inFC).OIDFieldName
fc = desc(inFC).CatalogPath.replace("\\","/")
SR = arcpy.CreateSpatialReference_management("#",fc,"#","#","#","#")
#
rows = arcpy.SearchCursor(inFC)
outData = []
outDataArray = []
pnts = []
for row in rows:                    #cycle through the shapes
  OIDval = row.getValue(OIDField)
  aShape = row.shape
  shapeList = [OIDval, aShape]
  theReturned = DensifyHelper.polyToPnts(shapeList) #see helper script
  shapePnts = []
  for i in range(0, len(theReturned)):
    if theReturned[i] == None:   #account for interior rings and parts
      shapePnts.append(None)
    else:
      XY = [theReturned[i][1], theReturned[i][2]]
      shapePnts.append(XY)
  densPnts = DensifyHelper.densifyPoly(shapePnts, stepBy)
  outDataArray.append([densPnts, OIDval])

fieldsToAdd = []
if outPoly != "#":              #create the output, join the data, clean-up
  tempFile = outPoly.replace(".shp","temp.shp")
  DensifyHelper.polyFromPoints (tempFile, outType, SR, outDataArray, fieldsToAdd, arcpy)
  join_tbl = inFC.replace("*.shp", ".dbf")
  arcpy.MakeFeatureLayer_management(tempFile,"temp")
  arcpy.env.qualifiedFieldNames = False
  arcpy.AddJoin_management("temp",OIDField, join_tbl, OIDField)
  arcpy.CopyFeatures_management("temp",outPoly)
  arcpy.AddMessage("\n" + "The file: " + str(outPoly) + " has been created.\n")
  arcpy.Delete_management(tempFile)
if outPoint != "#":
  DensifyHelper.createPointFile(outPoint, "point", SR, outDataArray, fieldsToAdd, arcpy)

#clean up
delList = [row, rows, outData, outDataArray,sys.argv[1],
           sys.argv[2], sys.argv[3], sys.argv[4]]
for i in delList:
  i = None

# Create joined strings to load up as input in spj join

SPJ_EXTRA=''
for k in range(0,len(spjnames),1):

    spjnamequote='"%s"' % spjnames[k]

    STRING_X1=' '.join([spjnames[k],spjnamequote,'true true false',str(spjlengths[k]),spjtypes[k], str(spjscales[k]),str(spjprecisions[k])])
    STRING_X2=','.join(['First','#',Input_CS_copy,spjnames[k],'-1','-1;']) 
    STRING_XM=','.join([STRING_X1,STRING_X2])

    SPJ_EXTRA=''.join([SPJ_EXTRA,STRING_XM])


arcpy.AddMessage("\n" + "Spatial join string: " + str(SPJ_EXTRA))


Point_shp_spj = 'in_memory\\CS_points_spj' 
arcpy.SpatialJoin_analysis(outPoint,Input_CS_copy,Point_shp_spj,"JOIN_ONE_TO_ONE","KEEP_ALL",SPJ_EXTRA,"INTERSECT","0 Meters","#")


Final_pt_shp="%s_CS_points_result.shp" %rivername
arcpy.gp.ExtractValuesToPoints_sa(Point_shp_spj,Depth_Image,Final_pt_shp,"NONE","ALL")


arcpy.AddXY_management(Final_pt_shp)


Final_pt_shp_txt="%s_CS_points_result.txt" %rivername

fieldList = arcpy.ListFields(Final_pt_shp)

allnames2=[]

for field in fieldList:
    g=[e.encode('utf-8') for e in field.name.strip('[]').split(',')]
    allnames2=g + allnames2
  
item1="Shape"
if item1 in  allnames2: allnames2.remove(item1)

allnames2=allnames2[::-1]
g2=';'.join(allnames2)


arcpy.AddMessage(g2)
arcpy.ExportXYv_stats(Final_pt_shp,g2,"SPACE",Final_pt_shp_txt,"ADD_FIELD_NAMES")

# Adding last layer to map
import arcpy.mapping
# get the map document 
mxd = arcpy.mapping.MapDocument("CURRENT")  

# get the data frame 
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]  

# create a new layer 
newlayer = arcpy.mapping.Layer(Final_pt_shp)  

# add the layer to the map at the bottom of the TOC in data frame 0 
arcpy.mapping.AddLayer(df, newlayer,"TOP")

# Refresh things
arcpy.RefreshActiveView()
arcpy.RefreshTOC()
del mxd, df, newlayer
    
del arcpy

