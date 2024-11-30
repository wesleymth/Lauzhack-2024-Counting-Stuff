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
    count = len(results[0])
    res = {
        "boxes": [],
        "cls" :[]
    }
    for result in results:
        for box in result.boxes:
            cv2.rectangle(img, (int(box.xyxy[0][0]), int(box.xyxy[0][1])),
                          (int(box.xyxy[0][2]), int(box.xyxy[0][3])), (255, 0, 0), rectangle_thickness)
            cv2.putText(img, f"{result.names[int(box.cls[0])]}",
                        (int(box.xyxy[0][0]), int(box.xyxy[0][1]) - 10),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), text_thickness)
            res["boxes"].append(box.xyxy[0])
            res["cls"].append(box.cls[0])
    
    with open(f'data/results_{result.names[int(classes[0])] if classes else "all" }.pkl', 'wb') as f:
        pickle.dump(res, f)
        
    return img, results, count

def predict_and_detect_obb(chosen_model, img, classes=[], conf=0.5, rectangle_thickness=2, text_thickness=1):
    results = predict(chosen_model, img, classes, conf=conf)
    count = len(results[0].obb.xyxy)
    for result in results:
        for box, cls in zip(result.obb.xyxy, result.obb.cls):
            cv2.rectangle(img, (int(box[0]), int(box[1])),
                          (int(box[2]), int(box[3])), (255, 0, 0), rectangle_thickness)
            cv2.putText(img, f"{result.names[int(cls)]}",
                        (int(box[0]), int(box[1]) - 10),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), text_thickness)
    
    res = {
    "boxes": results[0].obb.xyxy,
    "cls" : results[0].obb.cls
    }
    with open(f'data/results_satellite_{result.names[int(classes[0])] if classes else "all"}.pkl', 'wb') as f:
        pickle.dump(res, f)
    
    return img, results, count

def count_people(image, conf=0.5):
    model = YOLO("yolo11x.pt")
    result_img, _, count = predict_and_detect(model, image, classes=[0], conf=conf)
    return result_img, count

def count_satellite(image, classes, conf=0.5):
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
    model = YOLO("yolo11n-obb.pt")
    result_img, _, count = predict_and_detect_obb(model, image, classes, conf=conf)
    return result_img, count 
