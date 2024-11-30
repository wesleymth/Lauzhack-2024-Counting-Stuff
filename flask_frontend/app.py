from flask import Flask, render_template, request, jsonify, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# File upload configuration
UPLOAD_FOLDER = "./flask_frontend/static/uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    # Get message
    message = request.form.get("msg")

    # Handle file upload
    file_url = None
    if "file" in request.files:
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            file_url = url_for("static", filename=f"uploads/{filename}")

    # Return JSON response
    response = {"message": message, "file_url": file_url}
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
