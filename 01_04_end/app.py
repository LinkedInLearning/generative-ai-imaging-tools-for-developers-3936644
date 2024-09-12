from collections import deque
from flask import Flask, request, jsonify, render_template

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
        return "Your prompt has been flagged for moderation. Please try another prompt."
    return prompt


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
    moderation = client.moderations.create(input=prompt)

    flagged = moderation.results[0].flagged
    if flagged:
        return jsonify({"error": prompt})
    proccessed_prompt = enhance_prompt(client, prompt)
    response = client.images.generate(
        model="dall-e-3",
        prompt=proccessed_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    image_queue.append({"prompt": prompt, "url": image_url})
    return jsonify({"url": image_url})


@app.get("/api/list/")
def get_image():
    if image_queue:
        return jsonify(list(image_queue))
    return []


app.run(debug=True)
