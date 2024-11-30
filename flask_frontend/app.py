import os
import time as t
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
from src.yolo import count_people_tool, count_storage_tanks_tool
from src.function_calling_agent import get_agent
import os


# import dash
# from dash import dcc, html

app = Flask(__name__)

# File upload configuration
UPLOAD_FOLDER = "./flask_frontend/static/uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# # Initialize Dash app
# dash_app = dash.Dash(__name__, server=app, routes_pathname_prefix="/dash/")

# # Dash layout
# dash_app.layout = html.Div(
#     [
#         dcc.Graph(
#             id="example-graph",
#             figure={
#                 "data": [
#                     {"x": [1, 2, 3], "y": [4, 1, 2], "type": "bar", "name": "SF"},
#                     {"x": [1, 2, 3], "y": [2, 4, 5], "type": "bar", "name": "Montréal"},
#                 ],
#                 "layout": {"title": "Dash Data Visualization"},
#             },
#         )
#     ]
# )


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Function to generate chatbot responses
def get_bot_response(user_message, image_filename:str=None):
    # Placeholder for chatbot logic (e.g., OpenAI API call)
    agent = get_agent([count_people_tool, count_storage_tanks_tool])
    
    if image_filename is not None:
        user_message += f" image_filename={"./flask_frontend/" + image_filename}"
    
        print(user_message)
    response = agent.chat(user_message)
    
    return response.response


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

        bot_processed_img = "static/processed/" + file_path.split("/")[-1]
        # Get chatbot response
        bot_response = get_bot_response(message, file_url)
    else:
        bot_response = get_bot_response(message)
   

    print(file_url)
    # Return JSON response
    response = {
        "bot_response": bot_response,
        "bot_processed_img": bot_processed_img,
    }
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
