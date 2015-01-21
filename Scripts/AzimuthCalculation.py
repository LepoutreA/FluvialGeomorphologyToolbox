
'''
Author
  Adrien Lepoutre
  Dept of Geography
  McGill University, Montreal, Canada
  adrien.lepoutre@mail.mcgill.ca

Date      July 2013


Purpose
  Calculates azimuth of polylines.

Inputs:
    See 'Loading variables' section below
'''


import math,arcpy,sys,os

#Loading variables
Polyline_input = sys.argv[1]

arcpy.AddField_management(Polyline_input,"Azimuth","DOUBLE","15","6","#","#","NULLABLE","NON_REQUIRED","#")

expression = "GetAzimuthPolyline( !Shape!)"

codeblock= """def GetAzimuthPolyline(shape):
    if (shape.lastpoint.x - shape.firstpoint.x) == 0  and (shape.lastpoint.y - shape.firstpoint.y) > 0:
        degrees = 0
    elif (shape.lastpoint.x - shape.firstpoint.x) ==  0  and (shape.lastpoint.y - shape.firstpoint.y) < 0:
        degrees = 0
    elif (shape.lastpoint.x - shape.firstpoint.x) > 0  and (shape.lastpoint.y - shape.firstpoint.y) == 0:
        degrees = 90
    elif (shape.lastpoint.x - shape.firstpoint.x) <  0  and (shape.lastpoint.y - shape.firstpoint.y) == 0:
        degrees = 90
    else:
        radian = math.atan((shape.lastpoint.x - shape.firstpoint.x)/(shape.lastpoint.y - shape.firstpoint.y))
        degrees = radian * 180 / math.pi
    if degrees < 0:
        degrees = 180 + degrees
    return degrees"""

arcpy.CalculateField_management(Polyline_input,"Azimuth",expression,("PYTHON_9.3"),codeblock)
