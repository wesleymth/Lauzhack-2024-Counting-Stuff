import cv2
from ultralytics import YOLO
import matplotlib.pyplot as plt
import pickle
import os

def predict(chosen_model, img, classes=[], conf=0.5):
    if classes:
        results = chosen_model.predict(img, classes=classes, conf=conf)
    else:
        results = chosen_model.predict(img, conf=conf)

    return results

def predict_and_detect(chosen_model, imgs, classes, conf, save_name, save) : 
    
    results = predict(chosen_model, imgs, classes, conf=conf)
    
    all_data = []
    for result, img in zip(results, imgs):
        res = {
        "boxes": [],
        "cls" :[]
            }
        res["original_image"] = img.copy()
        for box in result.boxes:
            if save:
                cv2.rectangle(img, (int(box.xyxy[0][0]), int(box.xyxy[0][1])),
                            (int(box.xyxy[0][2]), int(box.xyxy[0][3])), (255, 0, 0), 2)
            res["boxes"].append(box.xyxy[0])
            res["cls"].append(box.cls[0])
        if save :
            res["image_with_boxes"] = img
            cv2.imwrite(save_name, img)
        all_data.append(res)
    return all_data

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

def show_images_with_boxes(results, name, rectangle_thickness=2):
    for i, result in enumerate(results) : 
        img = result["original_image"].copy()
        for box in result["boxes"]:
            cv2.rectangle(img, (int(box[0]), int(box[1])),
                        (int(box[2]), int(box[3])), (255, 0, 0), rectangle_thickness)
        result["image_with_boxes"] = img[...,::-1] #name
        cv2.imwrite(name, img)
    return results

def select_tanks(results, size_threshold, debug):
    selected_results = []
    for res in results:
        idx = [i for i, size in enumerate(res["size"]) if size > size_threshold]
        keys = ['boxes', 'cls', 'images_boxes', 'is_in_construction', 'size'] if debug else ['is_in_construction', 'size']
        res_selected = {key:[res[key][i] for i in idx] for key in keys}  
        if debug : 
            res_selected['original_image']= res['original_image']
        selected_results.append(res_selected)
    return selected_results

def extract_tanks_infos(results, scale, threshold = 100):
    for res in results :
        images_boxes = []
        is_in_construction = []
        sizes = []
        for x_min, y_min, x_max, y_max in res["boxes"]:
            if y_max - y_min < 0 or x_max - x_min < 0 or y_min < 0 or x_min < 0:
                continue
            else : 
                cropped_image = res["original_image"][int(y_min):int(y_max), int(x_min):int(x_max)] 
                images_boxes.append(cropped_image) 
                center_image = cropped_image[int(cropped_image.shape[0]/2), int(cropped_image.shape[1]/2)]
                mean_color = center_image.mean()
                is_in_construction.append(mean_color > threshold)
                size = cropped_image.shape[1] * scale
                sizes.append(size)
        res["images_boxes"] = images_boxes
        res["is_in_construction"] = is_in_construction
        res["size"] = sizes
    return results

def count_people(images, conf=0.5, save_name = "image_people.png", save=False):
    images = [cv2.imread(image) for image in images]
    model = YOLO("yolo11x.pt")
    res = predict_and_detect(model, images, classes=[0], conf=conf, save_name=save_name, save=save)
    with open(f'{save_name.split(".")[0]}.pkl', 'wb') as f:
        pickle.dump(res, f)
    return res

def count_people_tool(image_path : str) -> int:
    """
    Count the number of people in an image
    """
    res = count_people([image_path], save_name=image_path.replace('uploads', 'processed'), save=True)
    count  = len(res[0]["boxes"])
    return count

def count_satellite(images_path, classes, scale, conf=0.5, save_name = "image_tanks", save=False, size_threshold = 10, debug=True):
    """
    # scale : pixel/meter
    # 2100 meter/ image size
    # classes : list of int
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
    images = [cv2.imread(image) for image in images_path]
    model = YOLO("yolo11n-obb.pt")
    results = predict_and_detect_obb(model, images, classes, conf=conf)
    
    if classes == [2]:
        results = extract_tanks_infos(results, scale=scale/images[0].shape[1])
        results = select_tanks(results, size_threshold, debug)
        
    if save:
        results = show_images_with_boxes(results, save_name)
    
    for res, image_path in zip(results, images_path):
        res["date"] = image_path.split("/")[-1].split("\\")[-1].split(".")[0]
        
    with open(f'{save_name.split(".")[0]}.pkl', 'wb') as f:
        pickle.dump(results, f)
        
    return results 

def count_storage_tanks_tool(image_path : str) -> int:
    """
    Count the number of storage tanks in an image
    """
    res = count_satellite([image_path], [2], scale=2500, save_name=image_path.replace('uploads', 'processed'), save=True)
    count  = len(res[0]["boxes"])
    return count

def count_ships_tool(image_path : str) -> int:
    """
    Count the number of ships in an image
    """
    res = count_satellite([image_path], [1], scale=1000, conf =0.1, save = True, debug = True, save_name=image_path.replace('uploads', 'processed'))
    count  = len(res[0]["boxes"])
    return count

def history_storage_tanks_Rotterdam_tool() -> dict:
    """
    Count the number of storage tanks in a series of images
    """
    folder = "data/time-series"
    images_path = [os.path.join(folder, i) for i in os.listdir(folder)]
    result_img = count_satellite(images_path, [2], conf =0.5, save = False, scale =2500, size_threshold=20, save_name="data/time-series-Netherlands-Rotterdam.png", debug =False)
    return result_img

def history_storage_tanks_cushing_tool() -> dict:
    """
    Count the number of storage tanks in a series of images
    """
    folder = "data/cushing"
    images_path = [os.path.join(folder, i) for i in os.listdir(folder)]
    result_img = count_satellite(images_path, [2], conf =0.5, save = False, scale =5000, size_threshold=20, save_name="data/time-series-USA-cushing.png", debug =False)
    return result_img

def history_storage_tanks_tool() -> dict:
    """
    Count the number of storage tanks in a series of images
    """
    folder = "data/UAE"
    images_path = [os.path.join(folder, i) for i in os.listdir(folder)]
    result_img = count_satellite(images_path, [2], conf =0.5, save = False, scale =3800, size_threshold=40, save_name="data/time-series-UAE-Fujairah.png", debug =False)
    return result_img
