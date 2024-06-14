import shutil
import cv2
import numpy as np
import os


class PersonDetector:
    def __init__(self, yolo_weights='config/yolov3.weights', yolo_cfg='config/yolov3.cfg',
                 coco_names='config/coco.names'):
        # self.yolo_weights = yolo_weights
        # self.yolo_cfg = yolo_cfg
        # self.coco_names = coco_names
        # self.net, self.output_layers, self.classes = self.load_yolo()
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.yolo_weights = os.path.join(script_dir, yolo_weights)
        self.yolo_cfg = os.path.join(script_dir, yolo_cfg)
        self.coco_names = os.path.join(script_dir, coco_names)
        self.net, self.output_layers, self.classes = self.load_yolo()

    def load_yolo(self):
        # Check if the files exist
        if not os.path.isfile(self.yolo_weights):
            raise FileNotFoundError(f"YOLO weights file not found: {self.yolo_weights}")
        if not os.path.isfile(self.yolo_cfg):
            raise FileNotFoundError(f"YOLO config file not found: {self.yolo_cfg}")
        if not os.path.isfile(self.coco_names):
            raise FileNotFoundError(f"COCO names file not found: {self.coco_names}")

        net = cv2.dnn.readNet(self.yolo_weights, self.yolo_cfg)
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

        with open(self.coco_names, "r") as f:
            classes = [line.strip() for line in f.readlines()]

        return net, output_layers, classes

    def detect_person_in_image(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error reading image {image_path}")
            return False

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


def find_first_image_without_person(directory):
    detector = PersonDetector()
    for i in range(0, 12):  # Assuming there won't be more than 12 images
        image_path = os.path.join(directory, f'image_{i}.jpg')
        print(f"Image path exists: {os.path.exists(image_path)}")

        if os.path.exists(image_path):
            if not detector.detect_person_in_image(image_path):
                return image_path
    return None


def save_first_image_without_person(directory, save_directory="../garmentsImages"):
    result = find_first_image_without_person(directory)

    if result:
        print(f"The first image without a person is: {result}")
        copied_file_path = shutil.copy(result, save_directory)
        return copied_file_path
    else:
        print("No image without a person was found.")


# Example usage
if __name__ == "__main__":
    directory = "../scrapers/scraped_images\zara_images_2024_06_11-12_18"
    image_path = save_first_image_without_person(directory)
    print(f"The new location of the image: {image_path}")
    # print(os.chdir('/absolute/path/to/backend'))