import arcpy,os
from arcpy import env

arcpy.ClearWorkspaceCache_management()
arcpy.overwriteoutput = True

Wmask = sys.argv[1]
BufferDist = sys.argv[2]
StringIdentifier = sys.argv[3]
OutputDirectory = sys.argv[4]

env.workspace = OutputDirectory
os.chdir(OutputDirectory)
BufferDist = float(BufferDist)

BufferDist = "%d Meters" %BufferDist
Buf1 = "in_memory/buf1"
arcpy.Buffer_analysis(Wmask,Buf1,BufferDist,"FULL","ROUND","NONE","#")

BufShore = "in_memory/shore"
arcpy.Erase_analysis(Wmask,Buf1,BufShore,"#")

BufShore_rast = "in_memory/shore_rast"
arcpy.FeatureToRaster_conversion(BufShore,"FID",BufShore_rast,"1")

BufShore_rast_reclass = "%s_shore" %StringIdentifier
arcpy.gp.Reclassify_sa(BufShore_rast,"VALUE","0 1",BufShore_rast_reclass,"DATA")
