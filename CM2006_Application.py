import vtk
import sys
from matplotlib import cm
import json 
import SimpleITK as sitk
import numpy as np
from vtk.util.numpy_support import numpy_to_vtk
from mask import Mask
from masked_volume import Masked_volume
from timeit import default_timer as timer
from PyQt5 import QtWidgets, uic
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

def load_data_as_numpy(filename):
    reader = sitk.ImageFileReader()
    reader.SetFileName(filename)
    image = reader.Execute()
    array = sitk.GetArrayFromImage(image)

    return array

def convert_numpy_to_vtk(array):
    vtk_img = vtk.vtkImageData()
    depthArray = numpy_to_vtk(array.ravel(order='F'), deep=True, array_type=vtk.VTK_DOUBLE)
    vtk_img.SetDimensions(array.shape)
    vtk_img.SetSpacing([1,1,2])
    vtk_img.SetOrigin([0,0,0])
    vtk_img.GetPointData().SetScalars(depthArray)

    return vtk_img

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('C:/Users/raddn/Desktop/ALL/Dokument/Skola/KTH/Kurser/MASTER/CM2006 Medical Image Visualization/Project/Done/vtk_gui_Win.ui', self) 

        # Setting up the Qt GUI elements to vtk 
        self.vtk_widget_surface = QVTKRenderWindowInteractor(self.vtk_frame1) 
        self.iren_surface = self.vtk_widget_surface.GetRenderWindow().GetInteractor() 
        self.iren_surface.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.ren_surface = vtk.vtkRenderer() 
        self.vtk_widget_surface.GetRenderWindow().AddRenderer(self.ren_surface)

        self.vtk_widget_surface.GetRenderWindow().SetInteractor(self.iren_surface)

        self.vtk_widget_volume = QVTKRenderWindowInteractor(self.vtk_frame2) 
        self.iren_volume = self.vtk_widget_volume.GetRenderWindow().GetInteractor() 
        self.iren_volume.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.ren_volume = vtk.vtkRenderer() 
        self.vtk_widget_volume.GetRenderWindow().AddRenderer(self.ren_volume)

        self.vtk_widget_volume.GetRenderWindow().SetInteractor(self.iren_volume)

        # Connecting vertebrae selector Checkboxes
        self.checkBox_list=list()
        self.checkBox_16.toggled.connect(lambda: self.check_to_pick(self.checkBox_16, 0))
        self.checkBox_list.append(self.checkBox_16)
        self.checkBox_17.toggled.connect(lambda: self.check_to_pick(self.checkBox_17, 1))
        self.checkBox_list.append(self.checkBox_17)
        self.checkBox_18.toggled.connect(lambda: self.check_to_pick(self.checkBox_18, 2))
        self.checkBox_list.append(self.checkBox_18)
        self.checkBox_19.toggled.connect(lambda: self.check_to_pick(self.checkBox_19, 3))
        self.checkBox_list.append(self.checkBox_19)
        self.checkBox_20.toggled.connect(lambda: self.check_to_pick(self.checkBox_20, 4))
        self.checkBox_list.append(self.checkBox_20)
        self.checkBox_21.toggled.connect(lambda: self.check_to_pick(self.checkBox_21, 5))
        self.checkBox_list.append(self.checkBox_21)
        self.checkBox_22.toggled.connect(lambda: self.check_to_pick(self.checkBox_22, 6))
        self.checkBox_list.append(self.checkBox_22)
        self.checkBox_23.toggled.connect(lambda: self.check_to_pick(self.checkBox_23, 7))
        self.checkBox_list.append(self.checkBox_23)
        self.checkBox_24.toggled.connect(lambda: self.check_to_pick(self.checkBox_24, 8))
        self.checkBox_list.append(self.checkBox_24)
        self.all_pushButton.pressed.connect(self.all_checked)
        self.clear_pushButton.pressed.connect(self.clear_all)

        # Connecting CheckBoxes and buttons to corresponding vtk elements and functions
        self.ano_checkBox.toggled.connect(self.ano_toggle) #Anotations toggle
        self.segCol_checkBox.toggled.connect(self.segCol_toggle) #Segmentation color toggle
        self.rot_checkBox.toggled.connect(self.rot_toggle) #Automatic rotation toggle
        self.timer_count = 0
        self.invert_checkBox.toggled.connect(self.invert_toggle) #Invert plane toggle
        self.x_radioButton.toggled.connect(self.normal_changed) #Plane normal changer
        self.y_radioButton.toggled.connect(self.normal_changed)
        self.stereo_checkBox.toggled.connect(self.stereo_toggle)
        
        self.cutter_slider.valueChanged.connect(self.cut_changed) #Cut slider

        self.opacity_slider.valueChanged.connect(self.opacity_changed) #Opacity slider
        self.color_slider.valueChanged.connect(self.color_changed) #Color slider
        self.bone_radioButton.toggled.connect(self.color_changed) #Color Mode
        self.jet_radioButton.toggled.connect(self.color_changed) #Color Mode

        #Load the JSON file:
        with open('C:/Users/raddn/Desktop/ALL/Dokument/Skola/KTH/Kurser/MASTER/CM2006 Medical Image Visualization/Project/Done/004/verse004_ctd.json') as f:
            self.jason = json.load(f)

        # Easier way to define color (RGB)
        self.bonecolor=cm.get_cmap('bone')
        self.jet=cm.get_cmap('jet')

        # Data path 
        filename = "C:/Users/raddn/Desktop/ALL/Dokument/Skola/KTH/Kurser/MASTER/CM2006 Medical Image Visualization/Project/Done/004/verse004.nii.gz"
        filename_seg = "C:/Users/raddn/Desktop/ALL/Dokument/Skola/KTH/Kurser/MASTER/CM2006 Medical Image Visualization/Project/Done/004/verse004_seg.nii.gz"

        # Setting up the sources for the image and segmented image as NumPy array
        np_arr = load_data_as_numpy(filename)
        np_arr=np.rot90(np_arr,3,(0,2))

        np_arr_seg = load_data_as_numpy(filename_seg)
        np_arr_seg=np.rot90(np_arr_seg,3,(0,2))

        # SEGMENTATION
        # Segment the vertebrae and create a mask for each vertebrae 
        mask=Mask(np_arr_seg)
        masks=list()
        custom_array=[0,5,5,7,7,7,7,7,3]
        for i in range(len(self.jason)):                                     #play around with second and third argument to adjust the height interval to be segmented.
            if i==3:
                seg=mask.segment(int(self.jason[i].get("X")),(9),(12+i))     #special case to make the segment a little bit better
            elif i==4:
                seg=mask.segment(int(self.jason[i].get("X")),(9),(12+i))     #special case to make the segment a little bit better
            elif i==7:
                seg=mask.segment(int(self.jason[i].get("X")),(16),(11+i))
            else:
              seg=mask.segment(int(self.jason[i].get("X")),(11+i),(11+custom_array[i])) 
            
            masks.append(seg)

        # SURFACE RECONSTRUCTION: MAPPING AND ACTOR 
        # Mapping and actor creation of the surface image
        vtk_img = convert_numpy_to_vtk(np_arr)
        contour = vtk.vtkMarchingCubes()
        contour.SetInputData(vtk_img)
        contour.ComputeNormalsOn()
        contour.ComputeGradientsOn()
        contour.SetValue(0, 200) 

        con_mapper = vtk.vtkPolyDataMapper()
        con_mapper.SetInputConnection(contour.GetOutputPort())
        con_mapper.ScalarVisibilityOff()

        # Define illumination parameter and color properties
        prop = vtk.vtkProperty()
        prop.SetAmbient(0.4)
        prop.SetDiffuse(0.6)
        prop.SetSpecular(0.8)
        prop.SetSpecularPower(5)
        prop.SetColor((self.bonecolor(250)[:-1]))

        # Set up the image actor
        self.image_actor = vtk.vtkActor()
        self.image_actor.SetMapper(con_mapper)
        self.image_actor.SetProperty(prop)
        self.image_actor.SetOrigin(61,0,60)
        self.image_actor.PickableOff()

        # Mapping and actor creation of all vertebrae mask segments
        self.surface_actors=list()
        for i in range(len(self.jason)):
        # Mapping of all the segments
            vtkseg=(convert_numpy_to_vtk(masks[i]))
            contour_seg = vtk.vtkMarchingCubes()
            contour_seg.SetInputData(vtkseg)
            contour_seg.ComputeNormalsOn()
            contour_seg.ComputeGradientsOn()
            contour_seg.SetValue(0, 3) 

            con_mapper_seg = vtk.vtkPolyDataMapper()
            con_mapper_seg.SetInputConnection(contour_seg.GetOutputPort())
            con_mapper_seg.ScalarVisibilityOff()

            # Define induvidual illumination and color properties
            self.prop_seg = vtk.vtkProperty()
            self.prop_seg.SetAmbient(0.4)
            self.prop_seg.SetDiffuse(0.6)
            self.prop_seg.SetSpecular(0.8)
            self.prop_seg.SetSpecularPower(5)
            self.prop_seg.SetColor((self.bonecolor(500)[:-1]))

            # Set up the segment actors
            self.seg_actor = vtk.vtkActor()
            self.seg_actor.SetMapper(con_mapper_seg)
            self.seg_actor.SetProperty(self.prop_seg)
            self.seg_actor.SetOrigin(61,0,60)
            self.surface_actors.append(self.seg_actor)

        # VOLUME RENDERING: MAPPING AND ACTORS 
        # Create the volume data of the mask sections
        self.seg_images=list()
        for i in range (len(self.jason)):
            seg_image=Masked_volume(np_arr,masks[i], int(self.jason[i].get("X")))
            self.seg_images.append(seg_image)

        # Setting up transfer functions for color and opacity
        volumeColor=vtk.vtkColorTransferFunction()
        rgb=(self.bonecolor(100)[:-1])
        volumeColor.AddRGBPoint(-100, rgb[0], rgb[1], rgb[2])
        rgb=(self.bonecolor(550)[:-1])
        volumeColor.AddRGBPoint(1000, rgb[0], rgb[1], rgb[2])

        volumeScalarOpacity=vtk.vtkPiecewiseFunction()
        volumeScalarOpacity.AddPoint(-100, 0.25)
        volumeScalarOpacity.AddPoint(1000, 0.85)

        volumeGradientOpacity=vtk.vtkPiecewiseFunction()
        volumeGradientOpacity.AddPoint(0,   0.0)
        volumeGradientOpacity.AddPoint(50,  0.5)
        volumeGradientOpacity.AddPoint(100, 1.0)

        # Defining the volume properties
        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(volumeColor)
        volumeProperty.SetScalarOpacity(volumeScalarOpacity)
        volumeProperty.SetGradientOpacity(volumeGradientOpacity)
        volumeProperty.SetInterpolationTypeToLinear()
        volumeProperty.ShadeOn()
        volumeProperty.SetAmbient(0.8)
        volumeProperty.SetDiffuse(0.4)
        volumeProperty.SetSpecular(0.0)

        # Creating the plane actor
        self.plane = vtk.vtkPlane()
        self.plane.SetOrigin(20,0,0)
        self.plane.SetNormal(1,0,0)

        # Setting up the volume actors
        self.volume_actors=list()
        for i in range(len(self.jason)):
            seg_data=self.seg_images[i].Get_masked_image()
            vtk_seg = convert_numpy_to_vtk(seg_data)
            vol_map = vtk.vtkGPUVolumeRayCastMapper()
            vol_map.SetInputData(vtk_seg)
            vol_map.AddClippingPlane(self.plane)

            self.volume_actor = vtk.vtkVolume()
            self.volume_actor.SetMapper(vol_map)
            self.volume_actor.SetProperty(volumeProperty)
            self.volume_actor.SetOrigin(61,0,60)
            self.volume_actors.append(self.volume_actor)

        # Creation and connetion of annotation text actors to renders
        self.show_surface_annotation=False
        self.show_volume_annotation=False
        self.surface_text_actors=list()
        self.volume_text_actors=list()
        for i in range(len(self.jason)):
            atext=vtk.vtkVectorText()
            astring=str(self.jason[i].get("label"))
            atext.SetText(astring)

            text_mapper=vtk.vtkPolyDataMapper()
            text_mapper.SetInputConnection(atext.GetOutputPort())

            textProperty = vtk.vtkProperty()
            textProperty.SetColor(1,1,1)
            textProperty.SetOpacity(1)
            textProperty.SetAmbient(1.0)
            textProperty.SetDiffuse(0.0)
            textProperty.SetSpecular(0.0)

            text_actor=vtk.vtkFollower()
            text_actor.SetMapper(text_mapper)
            text_actor.SetProperty(textProperty)
            text_actor.SetScale(11,11,11)
            text_actor.AddPosition(self.jason[8].get("Y"), self.jason[i].get("X"), -23)
            text_actor_copy=vtk.vtkFollower()
            text_actor_copy.ShallowCopy(text_actor)
            self.surface_text_actors.append(text_actor)
            self.volume_text_actors.append(text_actor_copy)

        # RENDERER
        # Define some light sources for the renderer
        spotlight1=vtk.vtkLight()
        spotlight1.SetColor(1, 1, 1)
        spotlight1.SetFocalPoint(61, 142, 60)
        spotlight1.SetPosition(0, 300, 0)
        spotlight1.PositionalOn() 
        spotlight1.SetConeAngle(80)

        spotlight2=vtk.vtkLight()
        spotlight2.SetColor(1, 1, 1)
        spotlight2.SetFocalPoint(61, 142, 60)
        spotlight2.SetPosition(0, -300, 0)
        spotlight2.PositionalOn() 
        spotlight2.SetConeAngle(80)

        self.ren_surface.AddLight(spotlight1)
        self.ren_surface.AddLight(spotlight2)
        self.ren_volume.AddLight(spotlight1)
        self.ren_volume.AddLight(spotlight2)

        # setting up and connecting the camera to the renders
        camera_surface = vtk.vtkCamera()
        camera_surface.SetViewUp(0., -1, 0.) 
        camera_surface.SetPosition(-800, 100, 100)
        camera_surface.SetFocalPoint(61, 142, 60)

        camera_volume = vtk.vtkCamera()
        camera_volume.SetViewUp(0., -1, 0.)
        camera_volume.SetPosition(-800, 100, 100)
        camera_volume.SetFocalPoint(61, 142, 60)

        self.ren_surface.SetActiveCamera(camera_surface)
        self.ren_volume.SetActiveCamera(camera_volume)

        # Setting the color of the renderers background to black
        self.ren_surface.SetBackground(0., 0., 0.)
        self.ren_volume.SetBackground(0., 0., 0.)

        # Setting up and connect the vtkpicker to the surface renderer
        self.picker = vtk.vtkCellPicker()
        self.picker.SetTolerance(0.0)
        self.picker.AddObserver("EndPickEvent", self.process_pick)
        self.vtk_widget_surface.SetPicker(self.picker)

        # Add the actors to the surface renderer
        for i in range(len(self.jason)):
            self.ren_surface.AddActor(self.surface_actors[i])   
        self.ren_surface.AddActor(self.image_actor)

        # Setting up the crystal eyes the stereo render
        self.vtk_widget_surface.GetRenderWindow().GetStereoCapableWindow() 
        self.vtk_widget_surface.GetRenderWindow().StereoCapableWindowOn() 
        self.vtk_widget_surface.GetRenderWindow().SetStereoRender(0) 
        self.vtk_widget_surface.GetRenderWindow().SetStereoTypeToCrystalEyes() #SetStereoTypeToAnaglyph()

        self.vtk_widget_volume.GetRenderWindow().GetStereoCapableWindow() 
        self.vtk_widget_volume.GetRenderWindow().StereoCapableWindowOn() 
        self.vtk_widget_volume.GetRenderWindow().SetStereoRender(0) 
        self.vtk_widget_volume.GetRenderWindow().SetStereoTypeToCrystalEyes()

        #Start
        self.show()
        self.iren_surface.Initialize()
        self.iren_volume.Initialize()
        self.iren_surface.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self.click_to_pick)
        self.iren_surface.Start()
        self.iren_volume.Start()

    # Toggles the corresponding picked actor in the volume render
    def process_pick(self, object, event):
        self.NewPickedActor = self.picker.GetActor() 
        if self.NewPickedActor:
            picked_index=self.surface_actors.index(self.NewPickedActor)
            self.checkBox_list[picked_index].toggle()

    # Extracts the mouse left-click coordinates and feed it into the picker
    def click_to_pick(self, object, event):
        x, y = object.GetEventPosition() 
        self.picker.Pick(x,y, 0, self.ren_surface)
        #self.picker.Pick(round(x/2), round(y/2), 0, self.ren_surface) #<- For Jimmy's Mac

    # Toggles the annotation actors
    def ano_toggle(self):
        if self.sender().isChecked():
            self.show_surface_annotation = True
            self.show_volume_annotation = True
            for i in range(len(self.jason)):
                self.ren_surface.AddActor(self.surface_text_actors[i])
                self.surface_text_actors[i].SetCamera(self.ren_surface.GetActiveCamera())
                if self.seg_images[i].Get_active_status() == True:
                    self.ren_volume.AddActor(self.volume_text_actors[i])
                    self.volume_text_actors[i].SetCamera(self.ren_volume.GetActiveCamera())
        else:
            self.show_surface_annotation = False
            self.show_volume_annotation = False
            for i in range(len(self.jason)):
                self.ren_surface.RemoveActor(self.surface_text_actors[i])
                if self.seg_images[i].Get_active_status() == True:
                    self.ren_volume.RemoveActor(self.volume_text_actors[i])
        self.vtk_widget_volume.GetRenderWindow().Render()
        self.vtk_widget_surface.GetRenderWindow().Render()

    # Toggles the vertebrae color visualization
    def segCol_toggle(self):
        for i in range(len(self.jason)):
            if self.sender().isChecked():
                self.surface_actors[i].GetProperty().SetColor(self.jet(i*30)[:-1])
            else:
                self.surface_actors[i].GetProperty().SetColor(self.bonecolor(250)[:-1])
        self.vtk_widget_surface.GetRenderWindow().Render()
    
    # Adjusts the scalar opacity transfer function for the volume render according to the slider value
    def opacity_changed(self):
        volumeScalarOpacity = vtk.vtkPiecewiseFunction()
        volumeScalarOpacity.AddPoint(-100, self.opacity_slider.value()/3400)
        volumeScalarOpacity.AddPoint(1000, self.opacity_slider.value()/1000)
        for i in range(len(self.jason)):
            self.volume_actors[i].GetProperty().SetScalarOpacity(volumeScalarOpacity)
        self.vtk_widget_volume.GetRenderWindow().Render()
    
    # Adjusts the color transfer function for the volume render according to the slider value
    def color_changed(self):
        volumeColor=vtk.vtkColorTransferFunction()
        if self.bone_radioButton.isChecked():
            rgb=(self.bonecolor(self.color_slider.value())[:-1])
            volumeColor.AddRGBPoint(-100, rgb[0], rgb[1], rgb[2])
            rgb=(self.bonecolor(self.color_slider.value()+500)[:-1])
            volumeColor.AddRGBPoint(1000, rgb[0], rgb[1], rgb[2])
        elif self.jet_radioButton.isChecked():
            rgb=(self.jet(self.color_slider.value())[:-1])
            volumeColor.AddRGBPoint(-100, rgb[0], rgb[1], rgb[2])
            rgb=(self.jet(self.color_slider.value()+500)[:-1])
            volumeColor.AddRGBPoint(1000, rgb[0], rgb[1], rgb[2])
        for i in range(len(self.jason)):
            self.volume_actors[i].GetProperty().SetColor(volumeColor)
        self.vtk_widget_volume.GetRenderWindow().Render()

    # Toggles the corresponding selected actor from the CheckBoxes in the volume render
    def check_to_pick(self, object, index):
        if object.isChecked():
            self.ren_volume.AddActor(self.volume_actors[index])
            self.seg_images[index].Switch_active_status()
            if self.show_volume_annotation == True:
                self.ren_volume.AddActor(self.volume_text_actors[index])
                self.volume_text_actors[index].SetCamera(self.ren_volume.GetActiveCamera())
        elif object.isChecked() == False:
            self.ren_volume.RemoveActor(self.volume_actors[index])
            self.seg_images[index].Switch_active_status()
            if self.show_volume_annotation == True:
                self.ren_volume.RemoveActor(self.volume_text_actors[index])
        self.vtk_widget_volume.GetRenderWindow().Render()

    # Selects all volume actors
    def all_checked(self):
        for i in range(len(self.checkBox_list)):
            if self.checkBox_list[i].isChecked() == False:
                self.checkBox_list[i].toggle()

    # Removes all volume actors
    def clear_all(self):
        for i in range(len(self.checkBox_list)):
            if self.checkBox_list[i].isChecked() == True:
                self.checkBox_list[i].toggle()

    # Toggle continious rotation of the surface render around its axial axis
    def rot_toggle(self):
        if self.rot_checkBox.isChecked():
            self.iren_surface.AddObserver('TimerEvent', self.rot_execute)
            self.iren_surface.CreateRepeatingTimer(10)

    def rot_execute(self, object, event):
        if self.rot_checkBox.isChecked():
            angle = self.timer_count % 360
            for i in range(len(self.jason)):
                self.surface_actors[i].SetOrientation(0, angle, 0)
            self.image_actor.SetOrientation(0, angle, 0)
            self.vtk_widget_surface.GetRenderWindow().Render()
            self.timer_count += 0.5

    # Selects slicing position according to the slider and selected direction
    def cut_changed(self):
        (x, y, z) = self.plane.GetOrigin()
        if self.x_radioButton.isChecked():
            x=self.cutter_slider.value()
        elif self.y_radioButton.isChecked():
            y=self.cutter_slider.value()
        elif self.z_radioButton.isChecked():
            z=self.cutter_slider.value()
        self.plane.SetOrigin(x, y, z)
        self.vtk_widget_volume.GetRenderWindow().Render()

    # Toggle starting point for the plane slicer/inverts the slicer normal 
    def invert_toggle(self):
        (x, y, z) = self.plane.GetNormal()
        self.plane.SetNormal(x*-1, y*-1, z*-1)
        self.vtk_widget_volume.GetRenderWindow().Render()

    # Changes the axis the slicer operates on according to new selected axis
    def normal_changed(self):
        if self.x_radioButton.isChecked():
            self.plane.SetNormal(1, 0, 0)
            self.plane.SetOrigin(20,0,0)
            self.cutter_slider.setMinimum(20)
            self.cutter_slider.setMaximum(130)
            self.cutter_slider.setProperty("value", 20)
        elif self.y_radioButton.isChecked():
            self.plane.SetNormal(0, 1, 0)
            self.plane.SetOrigin(0,20,0)
            self.cutter_slider.setMinimum(20)
            self.cutter_slider.setMaximum(290)
            self.cutter_slider.setProperty("value", 20)
        elif self.z_radioButton.isChecked():
            self.plane.SetNormal(0, 0, 1)
            self.plane.SetOrigin(0,0,10)
            self.cutter_slider.setMinimum(10)
            self.cutter_slider.setMaximum(110)
            self.cutter_slider.setProperty("value", 10)
        if self.invert_checkBox.isChecked():
            (x, y, z) = self.plane.GetNormal()
            self.plane.SetNormal(x*-1, y*-1, z*-1)
        self.vtk_widget_volume.GetRenderWindow().Render()

    # Toggle the stero rendering 
    def stereo_toggle(self):
        if self.stereo_checkBox.isChecked():
            self.vtk_widget_surface.GetRenderWindow().SetStereoRender(1) 
            self.vtk_widget_volume.GetRenderWindow().SetStereoRender(1) 
            self.vtk_widget_surface.GetRenderWindow().Render()
            self.vtk_widget_volume.GetRenderWindow().Render()
        else:
            self.vtk_widget_surface.GetRenderWindow().SetStereoRender(0) 
            self.vtk_widget_volume.GetRenderWindow().SetStereoRender(0) 
            self.vtk_widget_surface.GetRenderWindow().Render()
            self.vtk_widget_volume.GetRenderWindow().Render()

    def closeEvent(self, event):
        can_exit = True
        if can_exit:
            #Remove all actors from renderer
            self.ren_volume.RemoveAllViewProps()
            self.ren_surface.RemoveAllViewProps()
            #Delete renderer binding
            del self.ren_volume
            del self.ren_surface
            #Release all sys resources from RW
            self.iren_surface.GetRenderWindow().Finalize()
            self.iren_volume.GetRenderWindow().Finalize()
            event.accept()
        else:
            event.ignore()
app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()

