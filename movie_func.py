import cv2

# frameのスタート1、エンドframe count
class Movie:
    def __init__(self,path):
        self.path = path
        self.cap = cap = cv2.VideoCapture(path)
        self.frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = cap.get(cv2.CAP_PROP_FPS)

    def Get_Image(self,frame):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame-1)
        ret, img = self.cap.read()
        return ret, img
