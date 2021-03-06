import math
import random
import sys

import click
import cv2
import imutils
import matplotlib.pyplot as plt
import numpy as np

from fileutils import read_obj
from project import eulerAnglesToRotationMatrix


def create_blank(width, height, rgb_color=(0, 0, 0)):
    """Create new image(numpy array) filled with certain color in RGB"""

    # Create black blank image
    image = np.zeros((height, width, 3), np.uint8)

    # Since OpenCV uses BGR, convert the color first
    color = tuple(reversed(rgb_color))

    # Fill image with color
    image[:] = color

    return image

def draw_tracepoints(tracepath, size=512, color=(255, 255, 255), title="Tracepath"):
	frame = create_blank(size, size, rgb_color=(0, 0, 0))

	"""Given a tracepath, draw the path on the given frame."""
	tracepath.normalize(0, size)
	xs = np.array([point.pos[0] for point in tracepath.path])
	ys = np.array([point.pos[1] for point in tracepath.path])

	draw_points = list(zip(xs, ys))
	draw_points = list(map(lambda x: (int(x[0]), int(x[1])), draw_points))
	if len(tracepath.path) <= 1:
		return

	cv2.circle(frame, draw_points[0], 10, (0, 255, 0))

	positions_y = []
	velocities_y = []
	positions_x = []
	velocities_x = []
	speeds = []
	for i in range(len(tracepath.path) - 1):
		x_speed = abs(draw_points[i + 1][0] - draw_points[i][0]) * 4
		y_speed = abs(draw_points[i + 1][1] - draw_points[i][1]) * 8
		total_speed = math.sqrt(x_speed ** 2 + y_speed ** 2)

		motion_color = (color[0], max(0, color[1] - y_speed), color[2])
		# print(motion_color)
		cv2.line(frame, draw_points[i], draw_points[i + 1], motion_color)

		positions_x.append((i, draw_points[i][0]))
		velocities_x.append((i, x_speed))
		positions_y.append((i, draw_points[i][1]))
		velocities_y.append((i, y_speed))
		speeds.append((i, total_speed))

		try:
			if i in tracepath.checkpoint_indices:
				cv2.circle(frame, draw_points[i], 8, (0, 255, 255))
		except AttributeError:
			pass
	
	final_index = len(tracepath.path) - 1
	try:
		if final_index in tracepath.checkpoint_indices:
			cv2.circle(frame, draw_points[final_index], 8, (0, 255, 255))
	except AttributeError:
		pass

	plt.figure(figsize=(20,20))


	"""plt.plot([p[0] for p in positions_x], [p[1] for p in positions_x], color='red')
	plt.plot([p[0] for p in velocities_x], [p[1] for p in velocities_x], color='purple')
	plt.plot([p[0] for p in positions_y], [p[1] for p in positions_y], color='green')
	plt.plot([p[0] for p in velocities_y], [p[1] for p in velocities_y], color='blue')

	plt.scatter([p for p in tracepath.checkpoint_indices], [positions_x[p][1] for p in tracepath.checkpoint_indices], s=80, facecolors='none', edgecolors='r')
	plt.scatter([p for p in tracepath.checkpoint_indices], [velocities_x[p][1] for p in tracepath.checkpoint_indices], s=80, facecolors='none', edgecolors='r')
	plt.scatter([p for p in tracepath.checkpoint_indices], [positions_y[p][1] for p in tracepath.checkpoint_indices], s=80, facecolors='none', edgecolors='r')
	plt.scatter([p for p in tracepath.checkpoint_indices], [velocities_y[p][1] for p in tracepath.checkpoint_indices], s=80, facecolors='none', edgecolors='r')"""
	plt.plot([p[0] for p in speeds], [p[1] for p in speeds], color="green")

	if hasattr(tracepath, 'checkpoint_indices'):
		sorted_checkpoints = sorted(list(tracepath.checkpoint_indices))
		if sorted_checkpoints[-1] >= len(speeds):
			sorted_checkpoints = sorted_checkpoints[:-1]

		plt.scatter([p for p in sorted_checkpoints], [speeds[p][1] for p in sorted_checkpoints], s=80, facecolors='none', edgecolors='r')

	plt.xlabel(title)
	plt.show()

	cv2.imshow(title, frame)
	cv2.waitKey(0)

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

def generate_random_bounding_boxes(seed_box, count, width, height):
    # (x, y, width in x, height in y)
    bboxes = []
    for i in range(0, count):
        RAND_RANGE = 3
        original_bbox = seed_box

        new_x = min(original_bbox[0] + random.randint(-RAND_RANGE, RAND_RANGE), width)
        new_y = min(original_bbox[1] + random.randint(-RAND_RANGE, RAND_RANGE), height)
        new_width = original_bbox[2] + random.randint(-RAND_RANGE, RAND_RANGE)
        if new_x + new_width > width:
            new_width = width - new_x
        new_height = original_bbox[3] + random.randint(-RAND_RANGE, RAND_RANGE)
        if new_y + new_height > height:
            new_height = height - new_y

        bboxes.append((new_x, new_y, new_width, new_height))
    return bboxes

@click.command()
@click.argument('filename')
@click.option('-a', '--angle', help="Camera position in degrees", nargs=3, default=(0, 0, 0))
@click.option('-s', '--size', help="Size of frame", default=512, required=False)
def display_tracepoints(filename, angle, size):
	tracepath = read_obj(filename)
	if tracepath is None:
		print("The specified file does not exist.")
		sys.exit(1)

	print("tracepoint length: {}".format(len(tracepath.path)))
	print("checkpoints: {}".format(sorted(list(tracepath.checkpoint_indices))))
	print("timestamps: {}".format([point.t for point in tracepath.path]))
	draw_tracepoints(tracepath, size=size, title="{0}".format(filename))

	if not angle == (0, 0, 0):																																								
		x, y, z = [math.radians(int(d)) for d in angle]
		R = eulerAnglesToRotationMatrix(np.array([x, y, z]))
		tracepath.transform(R)
		tracepath.normalize()

		draw_tracepoints(tracepath, size=size, title="{0} transformed to {1}".format(filename, angle))

	cv2.waitKey(0)

if __name__ == "__main__":
	display_tracepoints()
