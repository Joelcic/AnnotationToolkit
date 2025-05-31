import json
import os
import cv2
from PyQt5.QtGui import QColor
import xml.etree.ElementTree as ET


def get_class_color(class_id):
    """
    Generates a distinct color for a given class ID using HSL color space.

    :param class_id: (int) ID of the class for which the color is generated.
    :return: (QColor) A QColor object representing the generated color.
    """
    # Generates a distinct QColor using HSV hue rotation
    hue = (class_id * 137) % 360  # 137 is a good spacing constant
    color = QColor()
    color.setHsl(hue, 255, 180)  # Full saturation, medium lightness
    return color

def save_as_yolo_format(current_index, annotations, output_folder, orig_img):
    """
    Saves the image and annotations in YOLO format.

    :param current_index: (int) Index of the current image, used for naming output files.
    :param annotations: (list of dict) Each dict contains:
                        - "class_id" (int): Class ID.
                        - "bbox" (tuple): (x_min, y_min, x_max, y_max) in pixel coordinates.
                        - "image_size" (tuple): (image_width, image_height) in pixels.
    :param output_folder: (str) Path to the output folder where images and labels will be saved.
    :param orig_img: (numpy.ndarray) Original image (BGR format) to save.
    :return: None
    """
    image_filename = f"{current_index + 1}.jpg"
    label_filename = f"{current_index + 1}.txt"

    os.makedirs(os.path.join(output_folder, "images"), exist_ok=True)
    os.makedirs(os.path.join(output_folder, "labels"), exist_ok=True)

    image_path = os.path.join(output_folder, "images", image_filename)
    label_path = os.path.join(output_folder, "labels", label_filename)

    # Save image
    cv2.imwrite(image_path, orig_img)

    # Save annotations
    with open(label_path, 'w') as f:
        for ann in annotations:
            class_id = ann["class_id"]
            x_min, y_min, x_max, y_max = ann["bbox"]
            img_w, img_h = ann["image_size"]

            # Correct calculation for YOLO normalized format
            x_center = (x_min + x_max) / 2 / img_w
            y_center = (y_min + y_max) / 2 / img_h
            w = (x_max - x_min) / img_w
            h = (y_max - y_min) / img_h

            # Now write to file
            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}\n")

def save_as_coco_format(current_index, annotations, output_folder, orig_img, classes):
    """
    Saves the image and annotations in COCO format JSON.

    :param current_index: (int) Current image index.
    :param annotations: (list of dict) Annotation list.
    :param output_folder: (str) Output folder path.
    :param orig_img: (np.ndarray) Original image (BGR).
    :param classes: (list of str) List of class names, indexed by class_id.
    :return: None
    """
    # Paths
    annotations_folder = os.path.join(output_folder, "annotations")
    images_folder = os.path.join(output_folder, "images")
    os.makedirs(annotations_folder, exist_ok=True)
    os.makedirs(images_folder, exist_ok=True)

    coco_file = os.path.join(annotations_folder, "annotations_coco.json")

    # If JSON exists, load it, otherwise start a new structure
    if os.path.exists(coco_file):
        with open(coco_file, 'r') as f:
            coco_data = json.load(f)
    else:
        coco_data = {
            "images": [],
            "annotations": [],
            "categories": []
        }

    img_w = orig_img.shape[1]
    img_h = orig_img.shape[0]
    image_id = current_index + 1  # or use UUID if you want unique ids

    # Save the image into images/ folder
    image_filename = f"{image_id}.jpg"
    image_path = os.path.join(images_folder, image_filename)
    cv2.imwrite(image_path, orig_img)

    # Add image info
    coco_data["images"].append({
        "id": image_id,
        "file_name": image_filename,
        "width": img_w,
        "height": img_h
    })

    # Ensure categories
    class_ids_in_anns = {ann["class_id"] for ann in annotations}
    for class_id in class_ids_in_anns:
        if not any(cat["id"] == class_id for cat in coco_data["categories"]):
            coco_data["categories"].append({
                "id": class_id,
                "name": classes[class_id],
                "supercategory": "object"
            })

    # Add annotations
    for idx, ann in enumerate(annotations):
        class_id = ann["class_id"]
        x_min, y_min, x_max, y_max = ann["bbox"]
        width = x_max - x_min
        height = y_max - y_min

        coco_data["annotations"].append({
            "id": len(coco_data["annotations"]) + 1,
            "image_id": image_id,
            "category_id": class_id,
            "bbox": [x_min, y_min, width, height],
            "area": width * height,
            "iscrowd": 0
        })

    # Save back the JSON
    with open(coco_file, 'w') as f:
        json.dump(coco_data, f, indent=4)

def save_as_voc_format(current_index, annotations, output_folder, orig_img, classes):
    """
    Saves the image and annotations in Pascal VOC format XML.

    :param current_index: (int) Current image index.
    :param annotations: (list of dict) Annotation list.
    :param output_folder: (str) Output folder path.
    :param orig_img: (np.ndarray) Original image (BGR).
    :param classes: (list of str) List of class names indexed by class_id.
    :return: None
    """
    # Create necessary folders
    images_folder = os.path.join(output_folder, "images")
    labels_folder = os.path.join(output_folder, "labels")
    os.makedirs(images_folder, exist_ok=True)
    os.makedirs(labels_folder, exist_ok=True)

    # Save the image under images/
    img_w = orig_img.shape[1]
    img_h = orig_img.shape[0]
    img_d = orig_img.shape[2] if len(orig_img.shape) == 3 else 1

    image_filename = f"{current_index + 1}.jpg"
    image_path = os.path.join(images_folder, image_filename)
    cv2.imwrite(image_path, orig_img)

    # Create XML root
    annotation = ET.Element("annotation")

    folder = ET.SubElement(annotation, "folder")
    folder.text = "images"

    filename = ET.SubElement(annotation, "filename")
    filename.text = image_filename

    path = ET.SubElement(annotation, "path")
    path.text = image_path

    source = ET.SubElement(annotation, "source")
    database = ET.SubElement(source, "database")
    database.text = "Unknown"

    size = ET.SubElement(annotation, "size")
    width = ET.SubElement(size, "width")
    width.text = str(img_w)
    height = ET.SubElement(size, "height")
    height.text = str(img_h)
    depth = ET.SubElement(size, "depth")
    depth.text = str(img_d)

    segmented = ET.SubElement(annotation, "segmented")
    segmented.text = "0"

    # Add each object
    for ann in annotations:
        class_id = ann["class_id"]
        x_min, y_min, x_max, y_max = ann["bbox"]

        obj = ET.SubElement(annotation, "object")

        name = ET.SubElement(obj, "name")
        name.text = classes[class_id]  # Write class name

        pose = ET.SubElement(obj, "pose")
        pose.text = "Unspecified"

        truncated = ET.SubElement(obj, "truncated")
        truncated.text = "0"

        difficult = ET.SubElement(obj, "difficult")
        difficult.text = "0"

        bndbox = ET.SubElement(obj, "bndbox")
        xmin = ET.SubElement(bndbox, "xmin")
        xmin.text = str(int(x_min))
        ymin = ET.SubElement(bndbox, "ymin")
        ymin.text = str(int(y_min))
        xmax = ET.SubElement(bndbox, "xmax")
        xmax.text = str(int(x_max))
        ymax = ET.SubElement(bndbox, "ymax")
        ymax.text = str(int(y_max))

    # Save XML
    tree = ET.ElementTree(annotation)
    label_filename = f"{current_index + 1}.xml"
    label_path = os.path.join(labels_folder, label_filename)
    tree.write(label_path)