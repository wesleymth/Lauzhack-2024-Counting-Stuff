import os
import time as t
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
from src.yolo import count_people_tool, count_storage_tanks_tool
from src.plots import plot_one_feature_temporal, plot_one_feature_distribution, plot_temporal_comparison_multiple_locations
from src.function_calling_agent import get_agent
import os


# import dash
# from dash import dcc, html

app = Flask(__name__)

# File upload configuration
UPLOAD_FOLDER = "./flask_frontend/static/uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PLOTS_FOLDER"] = "./flask_frontend/static/plots"

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
    agent = get_agent([count_people_tool, count_storage_tanks_tool, 
                       plot_one_feature_temporal,
                       plot_one_feature_distribution, 
                       plot_temporal_comparison_multiple_locations,
                    ])
    
    if """51°54'41"N 4°12'33"E""" in user_message:
        user_message += f" file=time-series-Netherlands-Rotterdam.pkl"
    elif """25°11'47"N 56°21'12"E""" in user_message:
        user_message += f" file=time-series-UAE-Fujairah.pkl"
    elif """35°56'38"N 96°44'35"W""" in user_message:
        user_message += f" file=time-series-USA-cushing.pkl"
    
    
    if image_filename is not None:
        user_message += f" image_filename={"./flask_frontend" + image_filename}"
    
    print(f"{user_message=}")
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
    print(request.files)
    if "file" in request.files and request.files["file"].filename!='':
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
        bot_processed_img = None
        bot_response = get_bot_response(message)
   

    plot_dir = os.path.join("./flask_frontend", "static", "plots")
    plot_paths = [url_for("static", filename=f"plots/{file}") for file in os.listdir(plot_dir)]

    # print(file_url)
    # Return JSON response
    response = {
        "bot_response": bot_response,
        "bot_processed_img": bot_processed_img,
        "plot_paths":plot_paths
    }
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
