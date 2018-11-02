import numpy as np
import cv2
import imutils
import matplotlib.pyplot as plt
import click
from fileutils import read_obj
import sys
from project import eulerAnglesToRotationMatrix
import math

def create_blank(width, height, rgb_color=(0, 0, 0)):
    """Create new image(numpy array) filled with certain color in RGB"""

    # Create black blank image
    image = np.zeros((height, width, 3), np.uint8)

    # Since OpenCV uses BGR, convert the color first
    color = tuple(reversed(rgb_color))

    # Fill image with color
    image[:] = color

    return image

def draw_tracepoints(tracepath, scale=1.0, fit_canvas=True, color=(255, 255, 255), frame=None, title="Tracepath"):
	frame = create_blank(512, 512, rgb_color=(0, 0, 0))

	"""Given a tracepath, draw the path on the given frame."""
	xs = np.array([point.pos[0] for point in tracepath.path])
	ys = np.array([point.pos[1] for point in tracepath.path])

	height = frame.shape[0]
	width = frame.shape[1]

	if fit_canvas:
		draw_points = list(zip(np.interp(xs, (xs.min(), xs.max()), (0, width)), np.interp(ys, (ys.min(), ys.max()), (0, height))))
	else:
		draw_points = list(zip(xs, ys))

	draw_points = list(map(lambda p: (int(p[0] * scale), int(p[1] * scale)), draw_points))

	if len(tracepath.path) <= 1:
		return

	for i in range(len(tracepath.path) - 1):
		cv2.line(frame, draw_points[i], draw_points[i + 1], color)

	cv2.imshow(title, frame)
	# cv2.waitKey(0)

def plotPath(path, coordinate, color):
    pts = path.time_sequence(coordinate)
    plt.plot([p[0] for p in pts], [p[1] for p in pts], color)

def request_bounding_box(frame, height=700):
	"""Prompt for a bounding box for the provided frame.
		The returned object is a tuple of
		(x coordinate, y coordinate, width in x, height in y)"""
	scale = frame.shape[0] / height

	bbox = cv2.selectROI("Select ROI", imutils.resize(frame, height=height), False)
	cv2.destroyWindow("Select ROI")
	cv2.waitKey(1)

	new_bbox = (int(bbox[0] * scale), int(bbox[1] * scale),
				int(bbox[2] * scale), int(bbox[3] * scale))
	return new_bbox

@click.command()
@click.argument('filename')
@click.option('-a', '--angle', help="Camera position in degrees", nargs=3, default=(0, 0, 0))
def display_tracepoints(filename, angle):
	tracepath = read_obj(filename)
	if tracepath is None:
		print("The specified file does not exist.")
		sys.exit(1)

	draw_tracepoints(tracepath, title="{0}".format(filename))

	if not angle == (0, 0, 0):
		x, y, z = [math.radians(int(d)) for d in angle]
		R = eulerAnglesToRotationMatrix(np.array([x, y, z]))
		tracepath.transform(R)
		tracepath.normalize()

		draw_tracepoints(tracepath, title="{0} transformed to {0}".format(filename, angle))

	cv2.waitKey(0)

if __name__ == "__main__":
	display_tracepoints()