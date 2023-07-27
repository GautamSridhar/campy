import os, sys, time, logging
import numpy as np
from collections import deque
from campy.cameras import unicam
from ximea import xiapi
import time

def LoadSystem(params):

    return params["cameraMake"]


def GetDeviceList(system):

    return system


def LoadDevice(systems, params, cam_params):
    cam_params["camera"] = cam_params["device"]
    return cam_params


def GetSerialNumber(device):

    return device


def GetModelName(camera):

    return camera.get_device_name()


def OpenCamera(cam_params):
    # Open the camera
    camera = xiapi.Camera()
    camera.open_device()

    # Load camera settings
    cam_params["cameraModel"] = GetModelName(camera)
    cam_params = LoadSettings(cam_params, camera)

    return camera, cam_params


def LoadSettings(cam_params, camera):
    # Load settings 
    # if cam_params["cameraModel"] in [b"MQ013MG-ON", b"MQ013RG-ON", b"MQ013CG-ON"]:
    #     camera.set_sensor_feature_selector("XI_SENSOR_FEATURE_ZEROROT_ENABLE")
    #     camera.set_sensor_feature_value(1)

    #     camera.set_downsampling_type("XI_SKIPPING")
    #     camera.set_downsampling(
    #         "XI_DWN_{}x{}".format(cam_params["downsampling"], cam_params["downsampling"])
    #     )

    camera.set_acq_timing_mode("XI_ACQ_TIMING_MODE_FRAME_RATE")
    camera.set_imgdataformat(cam_params["imageFormat"])

    # Set camera exposure,framerate and gain

    camera.set_exposure(int(cam_params["cameraExposureTimeInUs"]))
    camera.set_framerate(cam_params["frameRate"])
    camera.set_gain(cam_params["cameraGain"])

    # Get camera pixel width and height and save to cam_params for metadata
    # Also set camera offset
    camera.set_width(cam_params["frameWidth"]) 
    camera.set_height(cam_params["frameHeight"])
    return cam_params


def StartGrabbing(camera):
    # try:
        camera.start_acquisition()
        return True
    # except Exception:
        return False


def GrabFrame(camera, frameNumber):

    img = xiapi.Image()
    camera.get_image(img)

    return img


def GetImageArray(grabResult):

    return grabResult.get_image_data_numpy()


def GetTimeStamp(grabResult):

    return time.perf_counter()


def DisplayImage(cam_params, dispQueue, grabResult):
    img = grabResult.get_image_data_numpy()
   
    if len(ndim == 2):

        # Downsample image
        img = img[
            :: cam_params["displayDownsample"], :: cam_params["displayDownsample"]]
    else:
        # Downsample image
        img = img[
            :: cam_params["displayDownsample"], :: cam_params["displayDownsample"],:]

    # Send to display queue
    dispQueue.append(img)


def ReleaseFrame(grabResult):

    return grabResult


def CloseCamera(cam_params, camera):
    print("Closing {}... Please wait.".format(cam_params["cameraName"]))
    # Close Basler camera after acquisition stops
    camera.stop_acquisition()
    camera.close_device()


def CloseSystem(system, device_list):
    del system
    del device_list



# class XimeaCamera(Camera):
#     """Class for simple control of a Ximea camera.

#     Uses ximea API. Module documentation `here
#     <https://www.ximea.com/support/wiki/apis/Python>`_.

#     """

#     def __init__(self, **kwargs):
#         """

#         Parameters
#         ----------
#         downsampling : int
#             downsampling factor for the camera
#         """
#         super().__init__(**kwargs)

#         # Test if API for the camera is available
#         try:
#             self.cam = xiapi.Camera()
#         except NameError:
#             raise Exception(
#                 "The xiapi package must be installed to use a Ximea camera!"
#             )

#     def open_camera(self):
#         """ """

#         self.cam.open_device()

#         self.im = xiapi.Image()

#         # If camera supports hardware downsampling (MQ013xG-ON does,
#         # MQ003MG-CM does not):
#         if self.cam.get_device_name() in [b"MQ013MG-ON", b"MQ013RG-ON", b"MQ013CG-ON"]:
#             self.cam.set_sensor_feature_selector("XI_SENSOR_FEATURE_ZEROROT_ENABLE")
#             self.cam.set_sensor_feature_value(1)

#             self.cam.set_downsampling_type("XI_SKIPPING")
#             self.cam.set_downsampling(
#                 "XI_DWN_{}x{}".format(self.downsampling, self.downsampling)
#             )

#         try:
#             if self.roi[0] >= 0:
#                 self.cam.set_width(self.roi[2])
#                 self.cam.set_height(self.roi[3])
#                 self.cam.set_offsetX(self.roi[0])
#                 self.cam.set_offsetY(self.roi[1])
#         except xiapi.Xi_error:
#             return [
#                 "E:Could not set ROI "
#                 + str(self.roi)
#                 + ", w has to be {}:{}:{}".format(
#                     self.cam.get_width_minimum(),
#                     self.cam.get_width_increment(),
#                     self.cam.get_width_maximum(),
#                 )
#                 + ", h has to be {}:{}:{}".format(
#                     self.cam.get_height_minimum(),
#                     self.cam.get_height_increment(),
#                     self.cam.get_height_maximum(),
#                 )
#             ]

#         self.cam.start_acquisition()
#         self.cam.set_acq_timing_mode("XI_ACQ_TIMING_MODE_FRAME_RATE")
#         return ["I:Opened Ximea camera " + str(self.cam.get_device_name())]

#     def set(self, param, val):
#         """

#         Parameters
#         ----------
#         param :

#         val :


#         Returns
#         -------

#         """
#         try:
#             if param == "exposure":
#                 self.cam.set_exposure(int(val * 1000))

#             if param == "framerate":
#                 self.cam.set_framerate(val)
#         except xiapi.Xi_error:
#             return ["E:Invalid {} value {:0.2f}".format(param, val)]

#     def read(self):
#         """ """
#         try:
#             self.cam.get_image(self.im)
#             frame = self.im.get_image_data_numpy()
#         except xiapi.Xi_error:
#             frame = None

#         return frame

#     def release(self):
#         """ """
#         self.cam.stop_acquisition()
#         self.cam.close_device()