import cv2
import numpy as np


class PersonDetector:
    def __init__(self, yolo_weights='config/yolov3.weights', yolo_cfg='config/yolov3.cfg', coco_names='config/coco'
                                                                                                      '.names'):
        self.yolo_weights = yolo_weights
        self.yolo_cfg = yolo_cfg
        self.coco_names = coco_names
        self.net, self.output_layers, self.classes = self.load_yolo()

    def load_yolo(self):
        net = cv2.dnn.readNet(self.yolo_weights, self.yolo_cfg)
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        with open(self.coco_names, "r") as f:
            classes = [line.strip() for line in f.readlines()]
        return net, output_layers, classes

    def detect_person_in_image(self, image_path):
        img = cv2.imread(image_path)
        height, width, _ = img.shape
        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)

        class_ids = []
        confidences = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    class_ids.append(class_id)
                    confidences.append(float(confidence))

        for i in range(len(class_ids)):
            if class_ids[i] == 0:  # 'person' class in COCO dataset
                return True
        return False
