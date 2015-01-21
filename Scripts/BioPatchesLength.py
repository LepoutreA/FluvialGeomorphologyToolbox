
'''
Author
  Adrien Lepoutre
  Dept of Geography
  McGill University, Montreal, Canada
  adrien.lepoutre@mail.mcgill.ca

Date      July 2013


Purpose
  Uses output from MovingWindow_Article or Local MovingWindow & Centerline to calculate the length of each patch.

Inputs:
    See 'Loading variables' section below
'''


import csv, arcpy
import sys,os, numpy
from arcpy import env

#Loading variables
BioPatchesPolygon = sys.argv[1]
Centerline = sys.argv[2]
StringIdentifier =sys.argv[3]
workspace = sys.argv[4]


env.workspace = workspace
BioNum_lyr = "BioNum_lyr"
arcpy.MakeFeatureLayer_management(BioPatchesPolygon, BioNum_lyr)


BioNum = int(arcpy.GetCount_management(BioPatchesPolygon).getOutput(0))
features1 =[]
arcpy.AddMessage(BioNum)
for h in range(0, BioNum):

    arcpy.AddMessage(h)
    extra = '"FID"=%s' %(h)
    arcpy.SelectLayerByAttribute_management(BioNum_lyr,"NEW_SELECTION",extra)
    #arcpy.SelectLayerByLocation_management(Transects_lyr,"INTERSECT",BufPatchesPointsSnappedCut_lyr,"#","NEW_SELECTION")
    out = "in_memory/test1_%d" %h
    arcpy.Clip_analysis(Centerline,BioNum_lyr,out,"#")
    features1.append(out)

ClipOutput = "Clip_Output.shp" 
arcpy.Merge_management(features1, ClipOutput)



# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "LIne_cut"

ClipOutput2 = "in_memory/Clip_Output2"
arcpy.CopyFeatures_management(ClipOutput,ClipOutput2 ,"#","0","0","0")

#DissolveOutput = "Dissolve_Output2.shp"
#arcpy.Dissolve_management(ClipOutput2,DissolveOutput,"FID","#","SINGLE_PART","DISSOLVE_LINES")

extra = """Site "Site" true true false 80 Text 0 0 ,First,#,%s,Site,-1,-1""" %BioPatchesPolygon
OutputSpj = "LengthShapefileSpj.shp"
arcpy.SpatialJoin_analysis(ClipOutput2,BioPatchesPolygon,OutputSpj,"JOIN_ONE_TO_ONE","KEEP_ALL",extra,"CLOSEST","#","#")

arcpy.AddField_management(OutputSpj,"Length","DOUBLE","15","6","#","#","NULLABLE","NON_REQUIRED","#")
arcpy.CalculateField_management(OutputSpj, "Length", "!shape.length!", "PYTHON")



result_dbf = "LengthShapefileSpj.dbf"

# Method to export to CSV
# written by sgrieve accessed oct. 10, 2013 on http://gis.stackexchange.com/questions/42433/how-to-export-only-certain-columns-to-a-csv-file-in-arcgis


fc = env.workspace + "\\" + result_dbf
CSVFile = env.workspace + "/%s_output.csv" %StringIdentifier



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







