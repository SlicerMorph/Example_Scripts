# Animating a TPS warp between two point sets
#
#
# This script will show how to load a model with a corresponding landmark set, warp the model  
# to a target point set, and create an animation of this transformation. The animation will be 
# created as a sequence node, and will be displayed in the Sequences module in the final step.
# This sequence can be saved through the Screen Capture module.
#
# Sara Rolfe


#
# First, define functions that will be used to create this animation  
#
# This function is a utility that takes a fiducial node from the Slicer scene and returns a 
# set of VTK points
def getVTKPoints(fiducialNode):
  points = vtk.vtkPoints()
  point=[0,0,0]
  for i in range(fiducialNode.GetNumberOfFiducials()):
    fiducialNode.GetNthFiducialPosition(i,point)
    points.InsertNextPoint(point)
  return points

# This function expands a source point set in the direction of a target point set, scaled by a factor
def expandAlongWarpVector(sourcePoints, targetPoints, scaleFactor):
  expandedPoints = vtk.vtkPoints()
  currentPoint=[0,0,0]
  for i in range(sourcePoints.GetNumberOfPoints()):
    sourcePoint = sourcePoints.GetPoint(i)
    targetPoint = targetPoints.GetPoint(i)
    expansionVector=[0,0,0]
    expansionVector[0] = targetPoint[0]-sourcePoint[0]
    expansionVector[1] = targetPoint[1]-sourcePoint[1]
    expansionVector[2] = targetPoint[2]-sourcePoint[2]
    currentPoint[0]=sourcePoint[0]+(expansionVector[0]*scaleFactor)
    currentPoint[1]=sourcePoint[1]+(expansionVector[1]*scaleFactor)
    currentPoint[2]=sourcePoint[2]+(expansionVector[2]*scaleFactor)
    expandedPoints.InsertNextPoint(currentPoint)
  return expandedPoints

# This function sets up a sequence node, transform sequence, and sequence browser in the Slicer scene that will be used to capture the transform animation. It then initiates the recording.
def startRecording(modelNode, sourceLMNode, transformNode, sequenceName):
  #set up sequences for template model and PC TPS transform
  modelSequence=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceNode", sequenceName+"ModelSequence")
  modelSequence.SetHideFromEditors(0)
  transformSequence = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceNode", sequenceName+"TFSequence")
  transformSequence.SetHideFromEditors(0)
  #Set up a new sequence browser and add sequences
  browserNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceBrowserNode", sequenceName+"SequenceBrowser")
  browserLogic=slicer.modules.sequences.logic()
  browserLogic.AddSynchronizedNode(modelSequence,modelNode,browserNode)
  browserLogic.AddSynchronizedNode(modelSequence,sourceLMNode,browserNode)
  browserLogic.AddSynchronizedNode(transformSequence,transformNode,browserNode)
  browserNode.SetRecording(transformSequence,'true')
  browserNode.SetRecording(modelSequence,'true')
  #Set up widget to record
  browserWidget=slicer.modules.sequences.widgetRepresentation()
  browserWidget.setActiveBrowserNode(browserNode)
  recordWidget = browserWidget.findChild('qMRMLSequenceBrowserPlayWidget')
  recordWidget.setRecordingEnabled(1)

# This function ends recording of the sequence, and displays the captured sequence in the sequences browser.
def stopRecording():
  browserWidget=slicer.modules.sequences.widgetRepresentation()
  recordWidget = browserWidget.findChild('qMRMLSequenceBrowserPlayWidget')
  recordWidget.setRecordingEnabled(0)
  slicer.util.selectModule(slicer.modules.sequences)
  
#
# Now, run the animation
#  
# Get the model, source points and target points from the scene. Customize the visualization of these nodes (color, visibiility, etc) before running this script.
modelNode = getNode("model")
sourcePoints = getNode("source") 
targetPoints = getNode("target") 

# Set the number of unique frames to be created. The transform will appear smoother with a higher frame number.
frameNumber = 50

# Set up a TPS transform and initialize with no difference between source and target points
sourceLMVTK = getVTKPoints(sourcePoints)
targetLMVTK = getVTKPoints(targetPoints)
VTKTPS = vtk.vtkThinPlateSplineTransform()
VTKTPS.SetSourceLandmarks( sourceLMVTK )
VTKTPS.SetTargetLandmarks( sourceLMVTK )
VTKTPS.SetBasisToR()  # for 3D transform

# Add the TPS transform to the Slicer scene and apply to the model and source landmark points
transformNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTransformNode', 'TPS Transform')
transformNode.SetAndObserveTransformToParent( VTKTPS )
sourcePoints.SetAndObserveTransformNodeID(transformNode.GetID())
modelNode.SetAndObserveTransformNodeID(transformNode.GetID())

# Set up a seqeunce to capture the warping and start recording 
sequenceNamePrefix = "TPSWarp"
startRecording(modelNode, sourcePoints, transformNode, sequenceNamePrefix)

# The transform is interpolated by the set frameNumber and the target points are updated at each interval
for frame in range(frameNumber):
  scaleFactor = frame/frameNumber
  currentLMVTK = expandAlongWarpVector(sourceLMVTK, targetLMVTK, scaleFactor)
  VTKTPS.SetTargetLandmarks( currentLMVTK )

# Stop capturing the sequence and switch to the Sequences module to view.
stopRecording()