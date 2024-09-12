from collections import deque
from PIL import Image
import os

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
                        "text": "You take image-generation prompts and turn them into sticker styled image-generation prompts.",
                    }
                ],
            },
            {"role": "user", "content": [{"type": "text", "text": "A cat"}]},
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "A cute, cartoon-style cat with big eyes, wearing a colorful collar, surrounded by playful yarn balls and bright daisies, in a vibrant sticker design.",
                    }
                ],
            },
            {"role": "user", "content": [{"type": "text", "text": prompt}]},
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
    image_url = response.data[0].url
    image_queue.append({"prompt": prompt, "url": image_url})
    return jsonify({"url": image_url})


@app.get("/api/list/")
def get_image():
    # lists based on "/static/images/<prompt>.jpg"
    
    return jsonify([
        {"prompt": "", "url": f"/static/images/{image}"}
        for image in os.listdir("static/images")
    ])
    return jsonify([
  {
    "prompt": "Cat",
    "url": "https://oaidalleapiprodscus.blob.core.windows.net/private/org-o6VmyHuFm8y3SgHMah8J8Uat/user-n9PunPLiIU6n7i0hmZNUMDZP/img-J9q3CGnl5r9SAKLDsqqmgzYx.png?st=2024-09-12T09%3A22%3A26Z&se=2024-09-12T11%3A22%3A26Z&sp=r&sv=2024-08-04&sr=b&rscd=inline&rsct=image/png&skoid=d505667d-d6c1-4a0a-bac7-5c84a87759f8&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-09-11T23%3A20%3A00Z&ske=2024-09-12T23%3A20%3A00Z&sks=b&skv=2024-08-04&sig=yrSW3rbNfpPaUWza4ncsIT86cpWMoFa6kZ4ToEqp/6I%3D"
  },
  {
    "prompt": "unicorn",
    "url": "https://oaidalleapiprodscus.blob.core.windows.net/private/org-o6VmyHuFm8y3SgHMah8J8Uat/user-n9PunPLiIU6n7i0hmZNUMDZP/img-YlRWc7COmtopVMYATjtFyYNH.png?st=2024-09-12T09%3A23%3A01Z&se=2024-09-12T11%3A23%3A01Z&sp=r&sv=2024-08-04&sr=b&rscd=inline&rsct=image/png&skoid=d505667d-d6c1-4a0a-bac7-5c84a87759f8&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-09-11T23%3A18%3A11Z&ske=2024-09-12T23%3A18%3A11Z&sks=b&skv=2024-08-04&sig=aJHXkDzniKPFfAX/1pBGa/ur3hME%2BVYq8RQ/zDVNeZ0%3D"
  },
  {
    "prompt": "cat",
    "url": "https://oaidalleapiprodscus.blob.core.windows.net/private/org-o6VmyHuFm8y3SgHMah8J8Uat/user-n9PunPLiIU6n7i0hmZNUMDZP/img-VYcMDbgxyzmTDseWaHXKQk3p.png?st=2024-09-12T09%3A26%3A50Z&se=2024-09-12T11%3A26%3A50Z&sp=r&sv=2024-08-04&sr=b&rscd=inline&rsct=image/png&skoid=d505667d-d6c1-4a0a-bac7-5c84a87759f8&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-09-11T23%3A36%3A39Z&ske=2024-09-12T23%3A36%3A39Z&sks=b&skv=2024-08-04&sig=OEgKOMPQ9tOCZYFLz4xV1TYWiH45x4x55etdLUukS2w%3D"
  },
  {
    "prompt": "dog",
    "url": "https://oaidalleapiprodscus.blob.core.windows.net/private/org-o6VmyHuFm8y3SgHMah8J8Uat/user-n9PunPLiIU6n7i0hmZNUMDZP/img-XGyCbvaq2Kk4h1QY9JfSblvf.png?st=2024-09-12T09%3A27%3A12Z&se=2024-09-12T11%3A27%3A12Z&sp=r&sv=2024-08-04&sr=b&rscd=inline&rsct=image/png&skoid=d505667d-d6c1-4a0a-bac7-5c84a87759f8&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-09-11T23%3A12%3A13Z&ske=2024-09-12T23%3A12%3A13Z&sks=b&skv=2024-08-04&sig=WxVZUz3u5lFTRMeU8X8A970DjgQcywDAMtM5o/Y2sSg%3D"
  },
  {
    "prompt": "unicorn",
    "url": "https://oaidalleapiprodscus.blob.core.windows.net/private/org-o6VmyHuFm8y3SgHMah8J8Uat/user-n9PunPLiIU6n7i0hmZNUMDZP/img-QwxxWx5L3zLqs6KWJVOpV77T.png?st=2024-09-12T09%3A27%3A36Z&se=2024-09-12T11%3A27%3A36Z&sp=r&sv=2024-08-04&sr=b&rscd=inline&rsct=image/png&skoid=d505667d-d6c1-4a0a-bac7-5c84a87759f8&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-09-11T19%3A58%3A13Z&ske=2024-09-12T19%3A58%3A13Z&sks=b&skv=2024-08-04&sig=jU35N6B63tYS6WmMsAA6KDiMbYmhu3nOjJdLQB/kjnE%3D"
  }
])
    if image_queue:
        return jsonify(list(image_queue))
    return []

def load_image(url, prompt):
    """
    Load the image
    """
    response = requests.get(url, stream=True)
    image = Image.open(response.raw)
    file_path = f"static/images/{prompt}.png"
    resized = image.resize((512, 512,))
    image.save(file_path)
    return f"/{file_path}"
    
app.run(debug=True)
