
'''
Extract Values to Polygons.py

Author
  Adrien Lepoutre
  Dept of Geography
  McGill University, Montreal, Canada
  adrien.lepoutre@mail.mcgill.ca

Date      July 2013


Purpose
  Creates points inside polygons and extracts the raster values at each points. Spatial join included.

Inputs:
    See 'Loading inputs' section below
'''


import arcpy,os,sys
from arcpy import env

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

# Loading inputs
Input_patches_polygon = sys.argv[1]     # Polygon shapefiles at which points raster values should be extracted.
Spj_fields=sys.argv[2]                  # Input fields to join to final output. 
Input_image = sys.argv[3]               # Raster from which values will be extracted.
Cellsize_polyrast = sys.argv[4]         # Cellsize that will determine the density of points generated.
workspce = sys.argv[5]                  # Workspace in which output should be created.
rivername = sys.argv[6]                 # String to custumize output.

env.workspace = workspce

# Spatial join preparation
Input_patches_polygon_copy = 'in_memory\\patches_copy' 
fieldList = arcpy.ListFields(Input_patches_polygon)
arcpy.CopyFeatures_management(Input_patches_polygon, Input_patches_polygon_copy)

fieldList = arcpy.ListFields(Input_patches_polygon_copy)

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

arcpy.AddMessage(index1)

for j in index1:
    spjnames=[allnames[j]]+spjnames
    spjtypes=[alltypes[j]]+spjtypes
    spjlengths=[alllengths[j]]+spjlengths
    spjscales=[allscales[j]]+spjscales
    spjprecisions=[allprecisions[j]]+spjprecisions


arcpy.AddMessage("\n" + "Field(s) " + str(spjnames) + " will be spatially joined to output.")

 # Start extracting points

# Process: Polyline to Raster
Poly_rast="in_memory\\prast"
arcpy.PolygonToRaster_conversion(Input_patches_polygon,"FID",Poly_rast,"CELL_CENTER","NONE",Cellsize_polyrast)

Rast_pt="in_memory\\rastpt" 
arcpy.RasterToPoint_conversion(Poly_rast, Rast_pt, "VALUE")

# Create joined strings to load up as input in spj join
SPJ_EXTRA=''
arcpy.AddMessage(spjnames)
for k in range(0,len(spjnames),1):

    spjnamequote='"%s"' % spjnames[k]

    STRING_X1=' '.join([spjnames[k],spjnamequote,'true true false',str(spjlengths[k]),spjtypes[k], str(spjscales[k]),str(spjprecisions[k])])
    STRING_X2=','.join(['First','#',Input_patches_polygon_copy,spjnames[k],'-1','-1;']) 
    STRING_XM=','.join([STRING_X1,STRING_X2])

    SPJ_EXTRA=''.join([SPJ_EXTRA,STRING_XM])

arcpy.AddMessage("\n" + "Spatial join string: " + str(SPJ_EXTRA))


# Spatial join 2
Extract_result_spj="in_memory\\result_spj"
arcpy.SpatialJoin_analysis(Rast_pt,Input_patches_polygon_copy,Extract_result_spj,"JOIN_ONE_TO_ONE","KEEP_ALL",SPJ_EXTRA,"CLOSEST","1 Meters","#")

# Add coordinates to points
arcpy.AddXY_management(Extract_result_spj)

# Process: Extract Values to Points
Extract_final="%s_final_result.shp"  %rivername
arcpy.gp.ExtractValuesToPoints_sa(Extract_result_spj, Input_image, Extract_final, "NONE", "VALUE_ONLY")


# Add result to map
import arcpy.mapping
# get the map document 
mxd = arcpy.mapping.MapDocument("CURRENT")  

# get the data frame 
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]  

# create a new layer 
newlayer = arcpy.mapping.Layer(Extract_final)

# add the layer to the map at the bottom of the TOC in data frame 0 
arcpy.mapping.AddLayer(df, newlayer,"TOP")

# Refresh things
arcpy.RefreshActiveView()
arcpy.RefreshTOC()
del mxd, df, newlayer

