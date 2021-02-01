from urllib import request

import cv2
import flytekit
from flytekit import task, workflow
from flytekit.types.file import FlyteFile

@task
def edge_detection_canny(image_location:str) -> FlyteFile:
    working_dir = flytekit.current_context().working_directory
    plane_fname = '{}/plane.jpg'.format(working_dir.name)
    with request.urlopen(image_location) as d, open(plane_fname, 'wb') as opfile:
        data = d.read()
        opfile.write(data)

    img = cv2.imread(plane_fname, 0)
    edges = cv2.Canny(img, 50, 200)  # hysteresis thresholds

    output_file = '{}/output.jpg'.format(working_dir.name)
    cv2.imwrite(output_file, edges)

    return FlyteFile["jpg"](path=output_file)


@workflow
def EdgeDetectorWf(image_input: str) -> FlyteFile:
    edges = edge_detection_canny(image_location=image_input)
    return edges
