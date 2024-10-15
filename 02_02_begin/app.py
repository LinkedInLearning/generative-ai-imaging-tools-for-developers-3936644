from collections import deque
from PIL import Image
import os
import uuid

from flask import Flask, request, jsonify, render_template
import requests
from openai import OpenAI

app = Flask(__name__)

client = OpenAI()

image_queue = deque()

def enhance_prompt(client, prompt):
    "TODO: Challenge code below"
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
        "role": "system",
        "content": [
            {
            "text": "You take image-generation prompts and turn them into sticker styled image-generation prompts.",
            "type": "text"
            }
        ]
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "A cat"
            }
        ]
        },
        {
        "role": "assistant",
        "content": [
            {
            "type": "text",
            "text": "A cute, cartoon-style cat with big eyes, wearing a colorful collar, surrounded by playful yarn balls and bright daisies, in a vibrant sticker design."
            }
        ]
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": prompt,
            }
        ]
        }
    ],
    temperature=1,
    max_tokens=2048,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    response_format={
        "type": "text"
    }
    )
    return response.choices[0].message.content


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/")
def api():
    """
    payload includes prompt, returns image
    """
    data = request.json
    prompt = data["prompt"]

    proccessed_prompt = enhance_prompt(client, prompt)
    print("====================================")
    print(proccessed_prompt)
    print("====================================")
    response = client.images.generate(
        model="dall-e-3",
        prompt=proccessed_prompt,
        size="1024x1024",
        quality="standard", 
        n=1,
    )
    url = load_image(response.data[0].url, prompt)
    return jsonify({"url": url})


@app.get("/api/list/")
def get_image():
    return jsonify([
        {"prompt": image.split("-id")[0], "url": f"/static/images/{image}"}
        for image in os.listdir("static/images")
        if image.endswith(".png")
    ])
    

def load_image(url, prompt):
    """
    Load the image
    """
    response = requests.get(url, stream=True)
    image = Image.open(response.raw)
    uuid_string = str(uuid.uuid4())[:3]
    file_path = f"static/images/{prompt}-id{uuid_string}.png"
    resized = image.resize((512, 512,))
    image.save(file_path)
    return f"/{file_path}"
    
app.run(debug=True, port=5000)
