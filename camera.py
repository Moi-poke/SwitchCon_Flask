import cv2
from base_camera import BaseCamera


class Camera(BaseCamera):
    def __init__(self, camera_id):
        super(Camera, self).__init__(camera_id)

    @staticmethod
    def frames(camera_id=0):
        camera = cv2.VideoCapture(camera_id)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()
