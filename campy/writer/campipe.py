"""
"""
from imageio_ffmpeg import write_frames
import os
import time
import logging
import sys
from campy.utils import QueueKeyboardInterrupt

def OpenWriter(cam_params, queue):
	writing = False
	folder_name = os.path.join(cam_params["videoFolder"], cam_params["cameraName"])
	file_name = cam_params["videoFilename"]
	full_file_name = os.path.join(folder_name, file_name)

	if not os.path.isdir(folder_name):
		os.makedirs(folder_name)
		print('Made directory {}.'.format(folder_name))
	
	# Load defaults
	pix_fmt_out = cam_params["pixelFormatOutput"]
	codec = cam_params["codec"]
	gpu_params = []

	# CPU compression
	if cam_params["gpuID"] == -1:
		print('Opened: {} using CPU to compress the stream.'.format(full_file_name))
		if pix_fmt_out == 'rgb0':
			pix_fmt_out = 'yuv420p'
		if cam_params["codec"] == 'h264':
			codec = 'libx264'
		elif cam_params["codec"] == 'h265':
			codec = 'libx265'
		gpu_params = ['-r:v', str(cam_params["frameRate"]),
					'-preset', 'fast',
					'-tune', 'fastdecode',
					'-crf', cam_params["quality"],
					'-bufsize', '20M',
					'-maxrate', '10M',
					'-bf:v', '4',
					'-vsync', '0',]

	# GPU compression
	else:
		print('Opened: {} using GPU {} to compress the stream.'.format(full_file_name, cam_params["gpuID"]))
		if cam_params["gpuMake"] == 'nvidia':
			if cam_params["codec"] == 'h264':
				codec = 'h264_nvenc'
			elif cam_params["codec"] == 'h265':
				codec = 'hevc_nvenc'
			gpu_params = ['-r:v', str(cam_params["frameRate"]), # important to play nice with vsync '0'
						'-preset', 'slow', # set to 'fast', 'llhp', or 'llhq' for h264 or hevc
						'-rc', 'vbr',
						'-cq', cam_params["quality"],
						'-qmin', cam_params["quality"],
						'-qmax', cam_params["quality"],
						'-b:v', '0M',
						'-bf:v', '0',
						'-vsync', '0',
						'-2pass', '0',
						'-gpu', str(cam_params["gpuID"]),
						'-f', 'segment',
						'-segment_time', '1800']
		elif cam_params["gpuMake"] == 'amd':
			if pix_fmt_out == 'rgb0':
				pix_fmt_out = 'yuv420p'
			if cam_params["codec"] == 'h264':
				codec = 'h264_amf'
			elif cam_params["codec"] == 'h265':
				codec = 'hevc_amf'
			gpu_params = ['-r:v', str(cam_params["frameRate"]),
						'-usage', 'lowlatency',
						'-rc', 'cqp', # constant quantization parameter
						'-qp_i', cam_params["quality"],
						'-qp_p', cam_params["quality"],
						'-qp_b', cam_params["quality"],
						'-bf:v', '0',
						'-hwaccel', 'auto',
						'-hwaccel_device', str(cam_params["gpuID"]),]
		elif cam_params["gpuMake"] == 'intel':
			if pix_fmt_out == 'rgb0':
				pix_fmt_out = 'nv12'
			if cam_params["codec"] == 'h264':
				codec = 'h264_qsv'
			elif cam_params["codec"] == 'h265':
				codec = 'hevc_qsv'
			gpu_params = ['-r:v', str(cam_params["frameRate"]),
						'-bf:v', '0',]

	# Initialize writer object (imageio-ffmpeg)
	while(True):
		#try:
		try:
				writer = write_frames(
					full_file_name,
					size=(cam_params["frameWidth"], cam_params["frameHeight"]), # size [W,H]
					fps=cam_params["frameRate"],
					quality=None,
					codec=codec,
					pix_fmt_in=cam_params["pixelFormatInput"], # 'bayer_bggr8', 'gray', 'rgb24', 'bgr0', 'yuv420p'
					pix_fmt_out=pix_fmt_out,
					bitrate=None,
					ffmpeg_log_level=cam_params["ffmpegLogLevel"], # 'warning', 'quiet', 'info'
					input_params=['-an'], # '-an' no audio
					output_params=gpu_params,
					)
				writer.send(None) # Initialize the generator
				writing = True
				break

		except KeyboardInterrupt:
				break

		except Exception as e:
				logging.error('Caught exception (campipe.py line 102): {}'.format(e))
				time.sleep(0.1)

	# Initialize read queue object to signal interrupt
	readQueue = {}
	readQueue["queue"] = queue
	readQueue["message"] = 'STOP'

	return writer, writing, readQueue

def WriteFrames(cam_params, writeQueue, stopReadQueue, stopWriteQueue):
	# Start ffmpeg video writer 
	writer, writing, readQueue = OpenWriter(cam_params, stopReadQueue)

	with QueueKeyboardInterrupt(readQueue):
		# Write until interrupted or stop message received
		while(writing):
			try:
				if writeQueue:
					writer.send(writeQueue.popleft())
				else:
					# Once queue is depleted and grabber stops, then stop writing
					if stopWriteQueue:
						writing = False
					# Otherwise continue writing
					time.sleep(0.01)
					#message = writeQueue.popleft()
					#if not isinstance(message, str):
				#		writer.send(message)
				#	elif message=='STOP':
				#		break
				#else:
				#	time.sleep(0.001)
			except Exception as e:
					pass
		#	except KeyboardInterrupt:
		#		stopQueue.append('STOP')

		# Closing up...
		print('Closing video writer for {}. Please wait...'.format(cam_params["cameraName"]))
		writer.close()
		time.sleep(1)
