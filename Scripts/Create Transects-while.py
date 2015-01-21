'''
Create Transects.py

Authors
  Adrien Lepoutre, Gerry Gabrisch(line 221 to 311 borrowed and modified form Gerry Gabrisch 9.3 script)
  Dept of Geography
  McGill University, Montreal, Canada
  adrien.lepoutre@mail.mcgill.ca

Date      July 2013


Purpose
  Create lateral cross-sections at locations of objects along line, using slope at point. Spatial join included.

Inputs:
    See 'Loading inputs' section below

Additional notes: Make sure to activate overwrite in geoprocessing.
'''
# Part I:
# Import system modules

import sys, string, os, arcpy,unicodedata,arcgisscripting,math
from arcpy import env


gp = arcgisscripting.create()

# Loading inputs
dissolved_centerline = sys.argv[1]      # River centerline
ConstructPtsDistance = sys.argv[2]      # Distance at which points shapefiles should be created (string in meters). If this is filled, equidistant points will be created.
objects = sys.argv[3]                   # Objects at which you would like cross-sections to be created. Input can be point, polyline or polygon.
Spj_fields = sys.argv[4]                # Field from objects that you would like to spatially join
#Case_Field = sys.argv[5]                # Optional input for when objects inputs is other than points. This will determine on which case field is theperformed. Integer or string required.
mask = sys.argv[5]                      # Polygon of river used to clip cross sections
#SplitLineatObjDistance = sys.argv[7]    # Max distance separating two objects
distance = sys.argv[6]                  # Max lateral distance between centerline and objects
Fragment_dist = sys.argv[7]            # Fragmentation distance, start by inputing a value equal to half the average distance separating each cross-sections
rivername = sys.argv[8]                # Short string to characterize output. Input no more than 2 characters
workspce = sys.argv[9]                 # Workspace where output should be created.

#arcpy.AddMessage(workspce)
env.workspace = workspce
arcpy.overwriteOutputs = 1
os.chdir(workspce)
                            # Option 1: Construct Points in order to build transects #
if ConstructPtsDistance <> "#":
    arcpy.AddMessage('\n' + 'Construct Points option is true. Equidistant points will be built.')
    


# Construct points code written by StackOverflow user gotanuki accessed on http://gis.stackexchange.com/questions/57338/point-transects-along-a-line on September 9th, 2013
    #arcpy.AddMessage(workspce)   

    inLine = dissolved_centerline
    interval = float(ConstructPtsDistance)
    lineClusTol = float(ConstructPtsDistance)*5
    pts = True
    sr = arcpy.Describe(inLine).spatialReference
    inLineName = arcpy.Describe(inLine).name
    inLineName=inLineName[:-4]
        
    segPts = arcpy.CreateFeatureclass_management(env.workspace, (inLineName + '_pts.shp'), 'POINT','','','',sr)
    inLineName = inLineName
    #arcpy.AddMessage(objects)
    icursor = arcpy.da.InsertCursor(segPts, ('SHAPE@'))
    with arcpy.da.SearchCursor(inLine, ("SHAPE@LENGTH", "SHAPE@")) as cursor:
        for row in cursor:
            length = row[0]
            noIntervals = int(math.floor(length / interval))
            lastSegLength = length - interval * noIntervals
            for x in range(1, noIntervals):
                newPt = row[1].positionAlongLine(interval * x)
                icursor.insertRow((newPt,))
            if lastSegLength < lineClusTol:
                lastPt = row[1].positionAlongLine(interval * noIntervals + lastSegLength)
            else:
                lastPt = row[1].positionAlongLine(interval * noIntervals)
            icursor.insertRow((lastPt,))
    outName="in_memory//lines_segmented"         
    splitLine = arcpy.SplitLineAtPoint_management(inLine, segPts, outName, 1)
    objects=segPts
    object1=objects
    
############
    
else :
    arcpy.AddMessage('\n' + 'Using input objects to create transects.')
                            # Option 2: Building transects from already existing objects #

    # Check what type of objects we are going to create cross-sections from:
    desc = arcpy.Describe(objects)
    geometryType = desc.shapeType

    if geometryType == 'Point' or 'Multipoint':
        arcpy.AddMessage('\n' + 'Input is a point feature class.')
        object1=objects
    
    else :
        arcpy.AddMessage('Input type is not point. Proceeding to execute MEAN CENTER based on FID.')
        object1="obj1.shp"
        Case_Field = "FID"
        #Add field to object1 to copy it'FID'
        #if Case_Field=="FID":
        arcpy.AddField_management(objects, "MeanCtr", "TEXT",25)
        arcpy.CalculateField_management(objects, "MeanCtr", "float(!FID!)", "PYTHON")
        arcpy.MeanCenter_stats(objects, object1, "", "MeanCtr","")
        #else:
            #arcpy.MeanCenter_stats(objects, object1, "", Case_Field,"")

# SPATIAL JOIN PREPARATION #
objects_copy = 'in_memory/objects_copy'
#arcpy.AddMessage(objects)
arcpy.CopyFeatures_management(objects,objects_copy)

fieldList = arcpy.ListFields(objects_copy)

lst = [e.encode('utf-8') for e in Spj_fields.strip('[]').split(';')]

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

for field in fieldList:
    fnames=[e.encode('utf-8') for e in field.name.strip('[]').split(',')]
    allnames=fnames + allnames

    ftype=[e.encode('utf-8') for e in field.type.strip('[]').split(',')]
    alltypes=ftype + alltypes
  
    alllengths=[field.length]+alllengths
    
    allscales=[field.scale]+allscales
 
    allprecisions=[field.precision]+allprecisions
    
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

#arcpy.AddMessage(index1)

for j in index1:
    spjnames=[allnames[j]]+spjnames
    spjtypes=[alltypes[j]]+spjtypes
    spjlengths=[alllengths[j]]+spjlengths
    spjscales=[allscales[j]]+spjscales
    spjprecisions=[allprecisions[j]]+spjprecisions


arcpy.AddMessage("\n" + "Field(s) " + str(spjnames) + " will be spatially joined to output.")

# Part II:

dist2='%s Unknown' %distance


object1_copy='obj1_snap.shp'
arcpy.CopyFeatures_management(object1, object1_copy)
object1=object1_copy
extra1="%s EDGE '1000" %(dissolved_centerline)
arcpy.AddMessage(extra1)
arcpy.Snap_edit(object1,extra1)


# Fragmenting the line into a very large number of segments
Rast_line="in_memory\\Rastline1"
arcpy.PolylineToRaster_conversion(dissolved_centerline,"FID",Rast_line,"MAXIMUM_LENGTH","NONE",Fragment_dist)

#PROBLEM WITH PERMISSION COMING FROM THIS LINE
Rast_Pt="in_memory\\Rastpt" 
arcpy.RasterToPoint_conversion(Rast_line,Rast_Pt,"VALUE")


snap_extra="%s EDGE '500 Unknown'" %(dissolved_centerline)
arcpy.Snap_edit(Rast_Pt,snap_extra)

frag_centerline="in_memory\\fragline" 

arcpy.SplitLineAtPoint_management(dissolved_centerline,Rast_Pt,frag_centerline,"100 Meters")


#NEW METHOD START HERE
frag_centerline_layer='in_memory\\_fragline_lyr' 
arcpy.MakeFeatureLayer_management(frag_centerline,frag_centerline_layer,"#","#","FID FID VISIBLE NONE;Shape Shape VISIBLE NONE;Id Id VISIBLE NONE")

arcpy.SelectLayerByLocation_management(frag_centerline_layer,"INTERSECT",object1,"0 Meters","NEW_SELECTION")

SepLines="SepLines.shp"
arcpy.CopyFeatures_management(frag_centerline_layer, SepLines)

###############
# Print error message and stop script from running if the # of attributes in SepLinesOrd is different from the number of attributes in our input object shp
numObjects = int(arcpy.GetCount_management(objects).getOutput(0))
numSepLines = int(arcpy.GetCount_management(SepLines).getOutput(0))

arcpy.AddMessage(numObjects)
arcpy.AddMessage(numSepLines)

Fragment_dist=float(Fragment_dist)

while numObjects != numSepLines:
    if numObjects>numSepLines :
        arcpy.AddMessage("\n"+"Fragmentation distance is too large, reducing value.")
        Fragment_dist = Fragment_dist-(Fragment_dist)/2
        arcpy.AddMessage("Fragmentation distance reduced to: " + str(Fragment_dist))
        
    elif numObjects<numSepLines :
        arcpy.AddMessage("\n"+"Fragmentation distance is too small, increasing value.")
        Fragment_dist = Fragment_dist+(Fragment_dist)/2
        arcpy.AddMessage("Fragmentation distance increased to: " + str(Fragment_dist))
        
    # Fragmenting the line into a very large number of segments
    Rast_line="in_memory\\Rastline1"
    arcpy.PolylineToRaster_conversion(dissolved_centerline,"FID",Rast_line,"MAXIMUM_LENGTH","NONE",Fragment_dist)

    #PROBLEM WITH PERMISSION COMING FROM THIS LINE
    Rast_Pt="in_memory\\Rastpt" 
    arcpy.RasterToPoint_conversion(Rast_line,Rast_Pt,"VALUE")

    #arcpy.Describe(inLine).spatialReference
    snap_extra="%s EDGE '500 Unknown'" %(dissolved_centerline)
    arcpy.Snap_edit(Rast_Pt,snap_extra)

    frag_centerline="in_memory\\fragline" 

    arcpy.SplitLineAtPoint_management(dissolved_centerline,Rast_Pt,frag_centerline,"500 Meters")


    #NEW METHOD START HERE
    frag_centerline_layer='in_memory\\_fragline_lyr' 
    arcpy.MakeFeatureLayer_management(frag_centerline,frag_centerline_layer,"#","#","FID FID VISIBLE NONE;Shape Shape VISIBLE NONE;Id Id VISIBLE NONE")

    arcpy.SelectLayerByLocation_management(frag_centerline_layer,"INTERSECT",object1,"0 Meters","NEW_SELECTION")

    SepLines="in_memory\\SepLines"
    arcpy.CopyFeatures_management(frag_centerline_layer, SepLines)
    #Subextra1 =  '"FID"=%d' %(j)
    # Print error message and stop script from running if the # of attributes in SepLinesOrd is different from the number of attributes in our input object shp
    numObjects = int(arcpy.GetCount_management(objects).getOutput(0))
    numSepLines = int(arcpy.GetCount_management(SepLines).getOutput(0))
    
arcpy.AddMessage("\n"+ "Valid fragmentation distance: "+ str(Fragment_dist))
    


#Add field to object1 to copy it'FID
arcpy.AddField_management(object1, "OrderObj", "DOUBLE",15,6)
arcpy.CalculateField_management(object1, "OrderObj", "float(!FID!)", "PYTHON")


# Proceed to spatial join
SepLinesOrd="in_memory\\SepLOrd" 
extra_order="""OrderObj "OrderObj" true true false 16 Double 6 15 ,First,#,%s,OrderObj,-1,-1""" %object1
arcpy.SpatialJoin_analysis(SepLines,object1,SepLinesOrd,"JOIN_ONE_TO_ONE","KEEP_ALL",extra_order,"INTERSECT","#","#")
    

# Create sorted field that will be used to loop through the cross-sections
o1="OrderObj"
inputlines=SepLinesOrd
distance=float(distance)

# Part III: lines 323 until 410 are based on Gerry Gabrisch's script 'Create Perpendicular Lines at each Segment of Shapefile'
#                                       accessed on Febuary 15, 2013  at http://arcscripts.esri.com/details.asp?dbid=15756

textfile="%s_perpendicularlines.txt" %rivername
test=os.path.join(workspce, textfile)
open(test, "w")

    
#Create a text file and write polylines to the first line.
f = open(test,'a')
thestring = "polyline\n"
f.writelines(thestring)
f.close()


# Create an array with all coordinates of snapped points
PointCoords = []
for row in arcpy.da.SearchCursor(object1, ["SHAPE@XY"]):
    # Print x,y coordinates of each point feature
    #
    x, y = row[0]
    PointCoords +=row[0]
    
# Create search cursor
rows = arcpy.SearchCursor(inputlines,"","","",o1)

#advance the cursor to the first row
row = rows.next()
   
counter = 1
#start the row iteration
while row:
    #print counter
# Create the geometry object
    feat = row.shape
    #get coordinate values as lists
    startpt = feat.firstPoint
    endpt = feat.lastPoint
    #midpoint = feat.centroid

    startx = startpt.X
    starty = startpt.Y
    endx = endpt.X
    endy = endpt.Y
        
        
    #if the line is horizontal or vertical the slope and negreciprocal will fail so do this instead.
    if starty==endy or startx==endx:
        if starty == endy:
            y1 = starty + distance
            y2 = starty - distance
            x1 = startx
            x2 = startx
    
        if startx == endx:
            y1 = starty
            y2 = starty 
            x1 = startx + distance
            x2 = startx - distance        
        
    else:
        
        # Get slope of the line
        m = ((starty - endy)/(startx - endx))
            
        # Get the negative reciprocal 
        negativereciprocal = -1*((startx - endx)/(starty - endy))
            
        if m > 0:
            #increase x values, find y
            if m >= 1:
                y1 = negativereciprocal*(distance)+ PointCoords[(2*counter)-1]
                y2 = negativereciprocal*(-distance) + PointCoords[(2*counter)-1]
                x1 = PointCoords[(2*counter)-2] + distance
                x2 = PointCoords[(2*counter)-2] - distance
            #increase y find x
            if m < 1:
                y1 = PointCoords[(2*counter)-1] + distance
                y2 = PointCoords[(2*counter)-1] - distance
                x1 = (distance/negativereciprocal) + PointCoords[(2*counter)-2]
                x2 = (-distance/negativereciprocal)+ PointCoords[(2*counter)-2]
                    
        if m < 0:
            #add to x find y
            if m >= -1:
            #add to y find x
                y1 = PointCoords[(2*counter)-1] + distance
                y2 = PointCoords[(2*counter)-1] - distance
                x1 = (distance/negativereciprocal) + PointCoords[(2*counter)-2]
                x2 = (-distance/negativereciprocal)+ PointCoords[(2*counter)-2]
                
            if m < -1:
                y1 = negativereciprocal*(distance)+ PointCoords[(2*counter)-1]
                y2 = negativereciprocal*(-distance) + PointCoords[(2*counter)-1]
                x1 = PointCoords[(2*counter)-2]  + distance
                x2 = PointCoords[(2*counter)-2]  - distance

            
    f = open(test,'a')
    thestring = str(counter) + " 0\n" + "0 "+ str(x1)+" "+str(y1) + "\n" + "1 " + str(x2) + " " + str(y2) +"\n"
    f.writelines(thestring)
    f.close()   
    del x1
    del x2
    del y1
    del y2
        
    counter = counter + 1
        
    row = rows.next()
 
del row
del rows
f = open(test,'a')
thestring = "END"
f.writelines(thestring)
f.close()

# PART2 #

# Process: Create Features From Text File
import arcgisscripting
gp=arcgisscripting.create()

inSep = "."
strms = "in_memory\\m_W" 
# Create feature class from text file using past GIS module argisscripting
gp.CreateFeaturesFromTextFile(textfile,".",strms,"#")
del arcgisscripting



#ORDERING PERPENDICULAR VERTICES USING SPATIAL JOIN ON POINT SHP
outin= "in_memory\\Mid_W_o.shp" 


# Spatial join
# Create joined strings to load up as input in spj join

SPJ_EXTRA=''
arcpy.AddMessage(spjnames)
for k in range(0,len(spjnames),1):

    spjnamequote='"%s"' % spjnames[k]

    STRING_X1=' '.join([spjnames[k],spjnamequote,'true true false',str(spjlengths[k]),spjtypes[k], str(spjscales[k]),str(spjprecisions[k])])
    STRING_X2=','.join(['First','#',objects_copy,spjnames[k],'-1','-1;']) 
    STRING_XM=','.join([STRING_X1,STRING_X2])

    SPJ_EXTRA=''.join([SPJ_EXTRA,STRING_XM])

#arcpy.AddMessage("\n" + "Spatial join string: " + str(SPJ_EXTRA))

CS_shp_spj = 'in_memory\\CS_spj'
arcpy.SpatialJoin_analysis(strms,objects_copy,CS_shp_spj,"JOIN_ONE_TO_ONE","KEEP_ALL",SPJ_EXTRA,"INTERSECT","0 Meters","#")

# End spatial join

# Clip with mask
WidthCut = r"%s_CS.shp" %(rivername)
gp.Clip_analysis(CS_shp_spj,mask,WidthCut)

# Add field and calculate length
gp.AddField_management(WidthCut, "ChanWidth", "DOUBLE",15,6)
gp.CalculateField_management(WidthCut, "ChanWidth", "float(!SHAPE.LENGTH!)", "PYTHON")

# Add output to map
import arcpy.mapping
# Get the map document 
mxd = arcpy.mapping.MapDocument("CURRENT")  

# Get the data frame
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]  

# Create a new layer
newlayer = arcpy.mapping.Layer(WidthCut)

# Add the layer to the map at the top of the TOC in data frame 0 
arcpy.mapping.AddLayer(df, newlayer,"TOP")

# Refresh 
arcpy.RefreshActiveView()
arcpy.RefreshTOC()
del mxd, df, newlayer


#if ConstructPtsDistance == "#":
#    if geometryType <> 'Point':
#        arcpy.Delete_management(object1)
#else:
#    arcpy.Delete_management(segPts)


    
