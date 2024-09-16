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


def moderate_prompt(client, prompt):
    """
    Moderate the prompt
    """
    moderation = client.moderations.create(input=prompt)
    flagged = moderation.results[0].flagged
    if flagged:
        return "Your prompt has been flagged for moderation. Please try another prompt.", flagged
    return prompt, flagged


def enhance_prompt(client, prompt):
    """
    Enhance the prompt by adding a few more tokens
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        {
          "role": "system",
          "content": [
            {
              "type": "text",
              "text": "You take image-generation prompts and turn them into sticker styled image-generation prompts for software developers."
            }
          ]
        },
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "a cat"
            }
          ]
        },
        {
          "role": "assistant",
          "content": [
            {
              "type": "text",
              "text": "Sticker style illustration of a cute, cartoonish cat with oversized eyes programming on a laptop, a playful expression, and a colorful, whimsical background filled with yarn balls and fish toys. Include fun, bold outlines and a vibrant color palette!"
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
        response_format={"type": "text"},
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
    moderated_prompt, flagged = moderate_prompt(client, prompt)

    if flagged:
        return jsonify({"error": moderated_prompt})

    proccessed_prompt = enhance_prompt(client, prompt)
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
        {"prompt": image.split("-id")[1], "url": f"/static/images/{image}"}
        for image in os.listdir("static/images")
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
    
app.run(debug=True)
