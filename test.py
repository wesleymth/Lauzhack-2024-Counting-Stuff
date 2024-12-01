import time
import folium
import numpy as np
import pandas as pd
import gradio as gr
from folium.plugins import MousePosition
from src.function_calling_agent import get_agent
from src.yolo import count_people_tool, count_storage_tanks_tool

# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.


# Function to generate chatbot responses
def get_bot_response(user_message, image_filename: str = None):
    agent = get_agent([count_people_tool, count_storage_tanks_tool])

    if image_filename is not None:
        user_message += f" image_filename={"./flask_frontend/" + image_filename}"

        print(user_message)
    response = agent.chat(user_message)

    return response.response


def add_message(history, message):
    for x in message["files"]:
        history.append({"role": "user", "content": {"path": x}})
    if message["text"] is not None:
        history.append({"role": "user", "content": message["text"]})
    return history, gr.MultimodalTextbox(
        value=None, interactive=False, file_types=["image"]
    )


def bot(history: list):

    # message = history[-1]["content"]
    # image = history[-2]["content"][0].split("/")[-1]
    df = pd.DataFrame(history)
    submitted_content = df[df["role"] == "user"]["content"].tolist()
    images = [
        "./flask_frontend/static/uploads/" + x[0].split("/")[-1]
        for x in submitted_content
        if isinstance(x, tuple)
    ]
    print(images)

    response = "YOYOYOYOYO"

    # response = get_bot_response(user_message=message, image_filename=image)
    if len(images) == 1:
        history.append(
            {
                "role": "assistant",
                "content": (images[-1],),
            }
        )

    history.append({"role": "assistant", "content": f"{images}"})
    for character in response:
        history[-1]["content"] += character
        time.sleep(0.05)
        yield history

    history.append({"role": "assistant", "content": gr.HTML(read_plot())})


def read_plot():
    with open("./flask_frontend/static/plots/plot.html", "r") as file:
        html_content = file.read()
        print("Reading plot...")
    return html_content


with gr.Blocks() as demo:
    chatbot = gr.Chatbot(elem_id="chatbot", bubble_full_width=False, type="messages")

    chat_input = gr.MultimodalTextbox(
        interactive=True,
        file_count="multiple",
        placeholder="Enter message or upload file...",
        show_label=False,
    )

    chat_msg = chat_input.submit(
        add_message, [chatbot, chat_input], [chatbot, chat_input]
    )
    bot_msg = chat_msg.then(bot, chatbot, chatbot, api_name="bot_response")
    bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

demo.launch(
    debug=True,
    allowed_paths=[
        "./flask_frontend/static/processed/",
        "./flask_frontend/static/uploads/",
    ],
)
