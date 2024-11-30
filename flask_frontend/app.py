import os
import io
import folium
from PIL import Image
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_from_directory, session

app = Flask(__name__)

# Directories for file uploads
UPLOAD_FOLDER = "./static/uploads"
MAP_FOLDER = "./static/maps"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(MAP_FOLDER):
    os.makedirs(MAP_FOLDER)

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    # Generate a default map centered on a location
    map_path = os.path.join(MAP_FOLDER, "map.html")
    default_map = folium.Map(
        location=[37.7749, -122.4194], zoom_start=10
    )  # Default location San Francisco
    default_map.save(map_path)
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    msg = request.form.get("msg")
    file = request.files.get("file")

    # Save the file if it's valid
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        file_url = f"/static/uploads/{filename}"
    else:
        file_url = None

    # Return the message and file URL to the frontend
    return jsonify({"msg": msg, "file_url": file_url})


@app.route("/update_map", methods=["POST"])
def update_map():
    try:
        lat = float(request.form.get("lat", 46.519962))  # Default to EPFL
        lng = float(request.form.get("lng", 6.566365))
        zoom = int(request.form.get("zoom", 15))
        satellite_map = folium.Map(location=[lat, lng], zoom_start=zoom)
        _ = folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri",
            name="Esri Satellite",
            overlay=False,
            control=True,
        ).add_to(satellite_map)

        map_path = os.path.join(MAP_FOLDER, "map.html")
        satellite_map.save(map_path)

        # Generate map image
        img_data = satellite_map._to_png(1)
        img = Image.open(io.BytesIO(img_data))
        img_path = os.path.join(MAP_FOLDER, "map.png")
        img.save(img_path)

        # Send image to chatbot
        return jsonify({"success": True, "image_url": "/static/maps/map.png"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/send_map_to_chat", methods=["POST"])
def send_map_to_chat():
    image_url = request.form.get("image_url")
    if "chat_messages" not in session:
        session["chat_messages"] = []
    session["chat_messages"].append({"type": "image", "content": image_url})
    return jsonify({"success": True})


@app.route("/save_map", methods=["POST"])
def save_map():
    try:
        # lat = float(request.form.get("lat", 46.519962))  # Default to EPFL
        # lng = float(request.form.get("lng", 6.566365))
        # zoom = int(request.form.get("zoom", 15))
        # satellite_map = folium.Map(location=[lat, lng], zoom_start=zoom)
        # _ = folium.TileLayer(
        #     tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        #     attr="Esri",
        #     name="Esri Satellite",
        #     overlay=False,
        #     control=True,
        # ).add_to(satellite_map)

        # img_data = satellite_map._to_png(1)
        # img = Image.open(io.BytesIO(img_data))
        # img.save("./static/maps/map.png")
        pass
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/maps/<filename>")
def map_file(filename):
    return send_from_directory(MAP_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True)
