Instructions and documentation for Fluvial geomorphology ArcGIS toolbox
Published open-sourceon GitHub on 01/20/2015 in Portland, OR.

Author:

Adrien Lepoutre - Research Assistant, Geography Department, McGill University. Developped from 2013 to 2014 at McGill in the context of HydroNet research. This toolbox was presented at the NWGIS Conference in Lynwood on October 16, 2014. For any questions, contact me at: adrien.lepoutre@mail.mcgill.ca.

Additional credits: 
- Create transects line 211 to 311 were based off of Gerry Galbrisch s 9.2 script. http://arcscripts.esri.com/details.asp?dbid=15756. Link to his tools: ftp://lnnr.lummi-nsn.gov/GIS_Scripts/
- CrossSections to Points script is courtesy of Dan Patterson (Dan_Patterson@carleton.ca) https://geonet.esri.com/blogs/dan_patterson/

Password for embedded scripts: 
kiamika37

Instructions:
Download toolbox and then add to you .mxd file in ArcMap10. Check each .py script to add specific python modules. Short description of the scripts follow. Longer description on right side of tools when opening them.

Scripts descriptions:

 1. AzimuthCalculation
Calculates azimuth of polylines.


2. BioPatchesLengthsCalculator
Uses output from MovingWindow_Article or Local MovingWindow & Centerline to calculate the length of each patch.


3. Create Transects
Create perpendicular transects at either: 
a) each snapped object location along centerline
b) given distances (for which points are created in memory layer)
For more information about this script, see “ToolDescription1” word document.


4. CrossSections to Points
Takes transects and converts them to points. Used for flow calculation. 


5. Extract Patches Values
Extract values of rasters inside specific polygon to text file.


6. LocalMovingWindow
Extracts river reaches polygons according to couples of points (usually created surveyors). This script also extracts text files of the pixel values of the rasters. Option to add transects to polygon. Ignore spatial join object option. Make sure to run it without rasters (runs better) on the mxd. Also you cannot have patches (couples of points) that are ‘entangled’ together so patches cannot overlap. In case this happens, separate the biologists’ patches and run the code twice. You can, on the other hand, have patches that share common transects, that’s ok.  To troubleshoot the code, first check the “SelectedTransects1.shp” output to see if the right transects have been selected (should have a total that is a multiple of 4). Then if there is a problem, check the “CutBuffers.shp” to check where the selection goes wrong.


7. MovingWindow_Article
This is the main moving window tool. Make sure to run it without the rasters on the mxd. Always use ‘forMW’ transects as inputs. This script has a lot of information on the side when running it.
For more information about this script at check powerpoint presentation at adrienlepoutre.com.


8. MovingWindow_ArticleTargetFID
This is the same script as the latter, except that it uses TargetFID instead of FID for all selection operations. In case you run “MovingWindow_Article” and you get an error that says the sql operation is not correct, it means you need to run this tool. Error has to do with layers in memory not erased.


9. PatchesNames
Code to add the names of the point couples (patches) to inputted objects.


10. Points Inside Polygon
Converts a polygon to points.


11. Polygon to Points
Extracts values of rasters inside of a polygon to a text file. Optional buffer. 


12. RasterSubstraction -- RasterSubstraction.py
Substract the value of two raster to create a third raster.


13. Distance along Line (formerly RKM - River Kilometer) -- RKM.py
Classic RKM with mean center option. For more information see the RKM_Article tool side options.


14. Distance along Line (Original) -- RKM_Article.py
RKM toolbox without mean center option (default is mean center with “FID”). More information is provided on the side of the tool. 


15. SelectionTool
Tool to select a number of feature attributes of a given object, according to a text file with numbers organized in a the first column. Each number selects the feature attributes according to the matching FID of the object.


16. ShoreMaker
This tool creates a buffer around the water max and substract is, in order to create a negative buffer, consisting of a shre.


17. TransectsRKM
Calculates the RKM of inputted transects.
