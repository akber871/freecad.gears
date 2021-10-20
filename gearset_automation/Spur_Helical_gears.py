"""
Script to generate Spur and Helical gears in FreeCAD using gear module from https://github.com/looooo/freecad.gears

"""

import FreeCAD
import Part
import freecad.gears.commands as fcgear
from FreeCAD import Vector
from FreeCAD import Base
import math
#import Import

DOC = FreeCAD.newDocument()
DOC_NAME = "Gears"


def clear_doc():
	"""
	Clear the active document deleting all the objects
	"""
	for obj in DOC.Objects:
	    DOC.removeObject(obj.Name)


def setview():
	"""Rearrange View"""
	FreeCAD.Gui.SendMsgToActiveView("ViewFit")
	FreeCAD.Gui.activeDocument().activeView().viewAxometric()

if DOC is None:
	FreeCAD.newDocument(DOC_NAME)
	FreeCAD.setActiveDocument(DOC_NAME)
	DOC = FreeCAD.activeDocument()

else:

	clear_doc()

# EPS= tolerance to use to cut the parts
EPS = 0.10
EPS_C = EPS * -0.5

def involuteGear(teeth, helix_angle, height, module):
	"""
	Generates a simple cylindrical involute gear (Spur or helical) based on the provided gear parameters.
	"""
	
	body = DOC.addObject('PartDesign::Body','Body')
	gear = fcgear.CreateInvoluteGear.create()       # Gear module from external workbench
	gear.teeth = teeth
	gear.beta = helix_angle
	gear.height = height
	gear.module = module
	gear.double_helix = False
	
	gear_height = gear.height
	gear_radius = (gear.teeth * gear.module)/2	

	shaft_height = gear_height * 1.4	
	cylinder1_radius = gear_radius/1.5
	cylinder2_radius = cylinder1_radius/1.4	

	cylinder1 = Part.makeCylinder(cylinder1_radius, shaft_height)
	cylinder2 = Part.makeCylinder(cylinder2_radius, shaft_height)
	
	# Create a hollow cylinderical  gear shaft
	cylinder3 = cylinder1.cut(cylinder2)

	# Now the next task is to fuse the cylinder into the gear
	cylinder_obj = FreeCAD.ActiveDocument.addObject("Part::Feature","GearShaft")
	cylinder_obj.Shape = cylinder3

	gear_obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Gear")
	gear_obj.Shape = gear.Shape

	DOC.recompute()

	# Cut a hole for the gear shaft
	new_gear = gear.Shape.cut(cylinder1)

	#print(gear_obj.Shape)
	#print(new_gear.Shape)
	#print(cylinder1)

	# Color assignment for object shapes 
	#gear.ViewObject.ShapeColor = (0.9, 0.2, 0.6)		# gear color			
	#cylinder_obj.ViewObject.ShapeColor = (0.9, 0.2, 0.6)    # shaft color
	
	# At the moment, the above object colors cannot be exported via Step file through script. This feature 
	# is only available through the graphical user interface.

	involute_gear =new_gear.fuse(cylinder_obj.Shape)

	#DOC.recompute()

	return involute_gear, gear_radius, shaft_height


def main():

	# gear parameters 
	teeth = [12, 30]     # Number of teeth
	helix_angle = [0, 20]         # Spur gear = 0 degree, Helical = 20 degree
	height = [	20, 60]        # gear height
	module = 3.5        # Gear module size, default
	
	# placement variables - Each gears will be rotated at the origin for creating different pose
	placementX = 0
	placementY = 0
	placementZ = 0
	rot_angle = 0
	
	i = 1
	
	# Looping throught the parameters to generate a gear set
	# Rotations are only flat or upright so that the gear rests on the ground properly
	for h in height: 
		for t in teeth:
			for b in helix_angle:
				gear, gear_radius, shaft_height = involuteGear(t, b, h, module)
				
				rot = FreeCAD.Rotation(FreeCAD.Vector(1,0,0), rot_angle)                  # rotation about an axis 
				centre = FreeCAD.Vector(placementX, placementY, placementZ)       # central point of gear
				pos = gear.Placement.Base                                                                                # position point of gear
				newplace = FreeCAD.Placement(pos,rot,centre)                                        # make a new Placement object
				gear.Placement = newplace                                                                               # spin the gear
				                                                           
				if rot_angle in [90, 270, 450, 630]:
					gear.Placement.Base = (placementX, placementY,  gear_radius)
				elif rot_angle in [180, 540]: 
					gear.Placement.Base = (placementX, placementY,  shaft_height)
				else:
					gear.Placement.Base = (placementX, placementY,  0)
				
				#gear = gear.Shape
				
				if b == 0:  
					gear.exportStep("/home/akber/gearsets/new_gearset/stp_files/Gear_Spur_"+ str(t)+"Teeth_"+str(h)+"mm.stp")         # Spur gears 
					#gear.exportStl("/home/akber/gearsets/new_gearset/stl_files/Gear_Spur_"+ str(t)+"Teeth_"+str(h)+"mm.stl")          
				else:
					gear.exportStep("/home/akber/gearsets/new_gearset/stp_files/Gear_Helical_"+ str(t)+"Teeth_"+str(h)+"mm.stp")     # Helical gears
					#gear.exportStl("/home/akber/gearsets/new_gearset/stl_files/Gear_Helical_"+ str(t)+"Teeth_"+str(h)+"mm.stl")
				
				i += 1                                                                        
				
				#placementX += 20
				#placementY += 20
				rot_angle += 90
	
	setview()

if __name__ == "__main__":
    main()
