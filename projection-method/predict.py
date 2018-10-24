import click
import imutils
from fileutils import readData, read_obj
import matplotlib.pyplot as plt
import time
from time import sleep
import cv2
import os
import math
from project import eulerAnglesToRotationMatrix
import numpy as np
from motiontrack import Tracker
from tracepoint import TracePath, TracePoint
from classify import classifyDTW, computeSegment
from vizutils import draw_tracepoints, plotPath
from readvideo import getTracePathFromVideoFile

def prepData(data, R):
	for category in data:
		for tracepath in data[category]:
			tracepath.transform(R)
			tracepath.normalize()

def playVideo(filename, fps):
	video_segment = read_obj(filename)
	print("Video is " + str(len(video_segment) * (1 / 29.97)) + " seconds long") # TODO hardcoded FPS
	for frame_index in range(len(video_segment)):
		frame = video_segment[frame_index]
		frame = imutils.resize(frame, height=700)
		cv2.imshow("video", frame)
		cv2.waitKey(0)

@click.command()
@click.argument('filename')
@click.option('-f', '--fps', help="Input video framerate", default=29.97)
@click.option('--preview', help="Just view the video", is_flag=True)
@click.option('-d', '--data', help="Location of the data directory", default="data")
@click.option('-a', '--angle', help="Camera position in degrees", nargs=3, default=(0, 0, 0))
def predict(filename, fps, data, angle, preview):
	if not os.path.exists(filename):
		print("Invalid filename provided!")
		return
	if not os.path.exists(data):
		print("Invalid data directory provided!")
		return
	if preview:
		playVideo(filename, fps)
		return

	data = readData(data)

	x, y, z = [math.radians(int(d)) for d in angle]
	transform = eulerAnglesToRotationMatrix(np.array([x, y, z]))
	prepData(data, transform)

	video_data = getTracePathFromVideoFile(filename, fps)
	#video_data.transform(transform)
	video_data.normalize()

	print(classifyDTW(data, video_data))
	#print(computeSegment(video_data, data, 3))

if __name__ == "__main__":
	predict()