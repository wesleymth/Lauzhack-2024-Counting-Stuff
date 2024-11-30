import cv2
from ultralytics import YOLO
import matplotlib.pyplot as plt
import pickle

def predict(chosen_model, img, classes=[], conf=0.5):
    if classes:
        results = chosen_model.predict(img, classes=classes, conf=conf)
    else:
        results = chosen_model.predict(img, conf=conf)

    return results

def predict_and_detect(chosen_model, img, classes=[], conf=0.5, rectangle_thickness=2, text_thickness=1):
    results = predict(chosen_model, img, classes, conf=conf)
    name = results[0].names[int(classes[0])] if classes else "all" 
    
    all_data = []
    for result in results:
        res = {
        "boxes": [],
        "cls" :[]
            }
        for box in result.boxes:
            cv2.rectangle(img, (int(box.xyxy[0][0]), int(box.xyxy[0][1])),
                          (int(box.xyxy[0][2]), int(box.xyxy[0][3])), (255, 0, 0), rectangle_thickness)
            cv2.putText(img, f"{result.names[int(box.cls[0])]}",
                        (int(box.xyxy[0][0]), int(box.xyxy[0][1]) - 10),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), text_thickness)
            res["boxes"].append(box.xyxy[0])
            res["cls"].append(box.cls[0])
        all_data.append(res)
    return img, all_data, name

def predict_and_detect_obb(chosen_model, img, classes=[], conf=0.5, rectangle_thickness=2, text_thickness=1):
    results = predict(chosen_model, img, classes, conf=conf)
    name = results[0].names[int(classes[0])] if classes else "all"
    all_data = []
    for result in results:
        res = {
        "boxes": [],
        "cls" :[]
            }
        for box, cls in zip(result.obb.xyxy, result.obb.cls):
            cv2.rectangle(img, (int(box[0]), int(box[1])),
                          (int(box[2]), int(box[3])), (255, 0, 0), rectangle_thickness)
            cv2.putText(img, f"{result.names[int(cls)]}",
                        (int(box[0]), int(box[1]) - 10),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), text_thickness)
            res["boxes"].append(box)
            res["cls"].append(cls)
        all_data.append(res)
    
    return img, all_data, name


def extract_images_boxes(images, results):
    for res, image in zip (results, images) :
        images_boxes = []
        for x_min, y_min, x_max, y_max in res["boxes"]:
            cropped_image = image[int(y_min):int(y_max), int(x_min):int(x_max)] 
            images_boxes.append(cropped_image) 
        res["images_boxes"] = images_boxes
    return results

def is_in_construction(results, threshold = 100):
    for image in results :
        colors = []
        is_in_construction = []
        for i, cropped_image in enumerate(image["images_boxes"]):
            center_image = cropped_image[int(cropped_image.shape[0]/2), int(cropped_image.shape[1]/2)]
            mean_color = center_image.mean()
            colors.append(mean_color)
            is_in_construction.append(mean_color > threshold)
        
        image["color"] = colors
        image["is_in_construction"] = is_in_construction
    return results

def count_people(image, conf=0.5):
    image = cv2.imread(image)
    model = YOLO("yolo11x.pt")
    result_img, res, name = predict_and_detect(model, image, classes=[0], conf=conf) 
    with open(f'data/results_{name}.pkl', 'wb') as f:
        pickle.dump(res, f)
    return res

def count_people_tool(image_path : str) -> int:
    """
    Count the number of people in an image
    """
    res = count_people(image_path)
    count  = len(res[0]["boxes"])
    return count

def count_satellite(images, classes, conf=0.5):
    """
    classes : list of int
    {0: 'plane',
    1: 'ship',
    2: 'storage tank',
    3: 'baseball diamond',
    4: 'tennis court',
    5: 'basketball court',
    6: 'ground track field',
    7: 'harbor',
    8: 'bridge',
    9: 'large vehicle',
    10: 'small vehicle',
    11: 'helicopter',
    12: 'roundabout',
    13: 'soccer ball field',
    14: 'swimming pool'}
    
    """
    images = [cv2.imread(image) for image in images]
    model = YOLO("yolo11n-obb.pt")
    result_img, results, name = predict_and_detect_obb(model, images, classes, conf=conf)
    
    if classes == [2]:
        results = extract_images_boxes(images, results)
        results = is_in_construction(results)
        
    with open(f'data/results_satellite_{name}.pkl', 'wb') as f:
        pickle.dump(results, f)
    return result_img 
