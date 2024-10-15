from collections import deque
from PIL import Image
import os
import uuid

from flask import Flask, request, jsonify, render_template
import requests
from openai import OpenAI

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

app = Flask(__name__)

client = OpenAI()

image_queue = deque()

USER_PROMPT = "Vintage photo of a beautiful sunset over the ocean."

def generate_image(prompt):
    response = requests.post(
        f"https://api.stability.ai/v2beta/stable-image/generate/ultra",
        headers={
            "authorization": f"Bearer {STABILITY_API_KEY}",
            "accept": "image/*"
        },
        files={"none": ''},
        data={
            "prompt": prompt,
            "output_format": "webp",
        },
    )
    path = f"static/images/{USER_PROMPT}.webp"
    with open(path, "wb") as file:
        file.write(response.content)
    return path


    if response.status_code == 200:
        with open(f"./{USER_PROMPT}.webp", 'wb') as file:
            file.write(response.content)
    else:
        raise Exception(str(response.json()))


def moderate_prompt(client, prompt):
    moderation = client.moderations.create(input=prompt)
    flagged = moderation.results[0].flagged
    if flagged:
        ("Your prompt was flagged by our system.", flagged,)
    return prompt, flagged

def enhance_prompt(client, prompt):
    "TODO: Challenge code below"
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": "You take image generation prompts and enhance them to create modern conference booth design prompts. Output should be short and concise prompt."
            }
        ]
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "Sustainable AI"
            }
        ]
        },
        {
        "role": "assistant",
        "content": [
            {
            "type": "text",
            "text": "Design a modern conference booth featuring sustainable AI technology. Incorporate eco-friendly materials, interactive AI displays, and live demos that highlight energy-efficient solutions."
            },
        ]
        },
{
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": prompt,
            },
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
    prompt, flagged = moderate_prompt(client, prompt)
    if flagged:
        return jsonify({"error": "Your prompt was flagged by our system."})
    
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

@app.post("/api/variations/")
def variations():
    """
    receives image url and returns variations
    """
    image = request.json["image"]
    with open(f"static/images/{image}", "rb") as image_file:
        response = client.images.create_variation(
            model="dall-e-2",
            image=image_file,
            n=1,
            size="1024x1024",
        )
        image_name = image.split("-id")[0]
    loaded = [load_image(variation.url, f"{image_name} variation") for variation in response.data]
    return jsonify({"success": True, "images": loaded})

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
