import csv, arcpy
import sys,os
from arcpy import env


Shapefile = sys.argv[1]
StringIdentifier = sys.argv[2]
workspace = sys.argv[3]


workspace = "C:\\AdrienWork\\Hydronet2\\FabWork\\ToolBox_Geomorph\\ToolBox_GeomorphArticle\\SelectionTool\\"

env.workspace = workspace

index1=[]

os.chdir(workspace)

f = open("TestInput1.csv", 'rt')
try:
    reader = csv.reader(f)
    for row in reader:
        print row
        nest = ''.join(row)
        print nest
        index1 += [nest]
finally:
    f.close()

    print index1

#########################################################################
arcpy.CopyFeatures_management(Shapefile,"MWO_copy.shp","#","0","0","0")
arcpy.MakeFeatureLayer_management("MWO_copy.shp","MWO_poly_lyr")


##########################################################################
extra1=[]
for j in index1:
        
    Subextra1 =  '"FID"=%s' %(j)
    extra1 = [Subextra1] + extra1

extra2= ' OR '.join(extra1)   
#arcpy.AddMessage(extra2)

print extra2
    
arcpy.SelectLayerByAttribute_management("MWO_poly_lyr","NEW_SELECTION",extra2)


ExportedSelection = "%s_ExportedSelection.shp" %StringIdentifier
arcpy.CopyFeatures_management("MWO_poly_lyr",ExportedSelection,"#","0" ,"0","0")


#####################################################################
# Add output to map
mxd = arcpy.mapping.MapDocument("CURRENT")  
dataframe = arcpy.mapping.ListDataFrames(mxd,"*")[0]  
MapLayer2 = arcpy.mapping.Layer(ExportedSelection)
arcpy.mapping.AddLayer(dataframe, MapLayer2,"TOP")

arcpy.RefreshActiveView()
arcpy.RefreshTOC()
del MapLayer2, mxd, dataframe

# Delete layer
arcpy.Delete_management("MWO_poly_lyr")

arcpy.ClearWorkspaceCache_management()
###########################################


    

