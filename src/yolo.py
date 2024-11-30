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

def predict_and_detect(chosen_model, imgs, classes=[], conf=0.5, rectangle_thickness=2, text_thickness=1):
    
    results = predict(chosen_model, imgs, classes, conf=conf)
    name = results[0].names[int(classes[0])] if classes else "all" 
    
    all_data = []
    for result, img in zip(results, imgs):
        res = {
        "boxes": [],
        "cls" :[]
            }
        res["original_image"] = img.copy()
        for box in result.boxes:
            cv2.rectangle(img, (int(box.xyxy[0][0]), int(box.xyxy[0][1])),
                          (int(box.xyxy[0][2]), int(box.xyxy[0][3])), (255, 0, 0), rectangle_thickness)
            cv2.putText(img, f"{result.names[int(box.cls[0])]}",
                        (int(box.xyxy[0][0]), int(box.xyxy[0][1]) - 10),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), text_thickness)
            res["boxes"].append(box.xyxy[0])
            res["cls"].append(box.cls[0])
        res["image_with_boxes"] = img
        all_data.append(res)
    return all_data, name

def predict_and_detect_obb(chosen_model, imgs, classes=[], conf=0.5):
    results = predict(chosen_model, imgs, classes, conf=conf)
    all_data = []
    for result, img in zip(results, imgs):
        res = {}
        res["original_image"] = img.copy()
        res["boxes"] = (list(result.obb.xyxy))
        res["cls"] = (list(result.obb.cls))
        all_data.append(res)
    
    return all_data

def show_images_with_boxes(results, name, rectangle_thickness=2, text_thickness=1):
    for i, result in enumerate(results) : 
        img = result["original_image"].copy()
        for box in result["boxes"]:
            cv2.rectangle(img, (int(box[0]), int(box[1])),
                        (int(box[2]), int(box[3])), (255, 0, 0), rectangle_thickness)
            cv2.putText(img, f"{name}",
                        (int(box[0]), int(box[1]) - 10),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), text_thickness)
        result["image_with_boxes"] = f'data/{name}_{i}.jpg'
        cv2.imwrite(f'data/{name}_{i}.jpg', img[...,::-1])
    return results

def select_tanks(results, size_threshold = 100):
    selected_results = []
    for res in results:
        if res["cls"] == [2]:
            selected_results.append(res)
    return selected_results

def extract_tanks_infos(results, threshold = 100):
    for res in results :
        images_boxes = []
        is_in_construction = []
        sizes = []
        for x_min, y_min, x_max, y_max in res["boxes"]:
            cropped_image = res["original_image"][int(y_min):int(y_max), int(x_min):int(x_max)] 
            images_boxes.append(cropped_image) 
            center_image = cropped_image[int(cropped_image.shape[0]/2), int(cropped_image.shape[1]/2)]
            mean_color = center_image.mean()
            is_in_construction.append(mean_color > threshold)
            size = cropped_image.shape[0]
            sizes.append(size)
        res["images_boxes"] = images_boxes
        res["is_in_construction"] = is_in_construction
        res["size"] = sizes
    return results

def count_people(images, conf=0.5):
    images = [cv2.imread(image) for image in images]
    model = YOLO("yolo11x.pt")
    res, name = predict_and_detect(model, images, classes=[0], conf=conf) 
    with open(f'data/results_{name}.pkl', 'wb') as f:
        pickle.dump(res, f)
    return res

def count_people_tool(image_path : str) -> int:
    """
    Count the number of people in an image
    """
    res = count_people([image_path])
    count  = len(res[0]["boxes"])
    return count

def count_satellite(images, classes, conf=0.5, save_name = "image_tanks", save=False):
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
    results = predict_and_detect_obb(model, images, classes, conf=conf)
    
    if classes == [2]:
        results = extract_tanks_infos(results)
        # results = select_tanks(results)
    if save:
        results = show_images_with_boxes(results, save_name)
        
    with open(f'data/results_satellite_{save_name}.pkl', 'wb') as f:
        pickle.dump(results, f)
    return results 
