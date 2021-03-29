# Copy and paste this code to show an extra panel of Markups module outside of the Slicer's main application window. 

markups_module_widget = slicer.modules.markups.createNewWidgetRepresentation()
markups_module_widget.setMRMLScene(slicer.mrmlScene)
markups_module_widget.show()
