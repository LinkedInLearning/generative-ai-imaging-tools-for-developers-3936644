import os
import requests

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

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

    if response.status_code == 200:
        with open(f"./{USER_PROMPT}.webp", 'wb') as file:
            file.write(response.content)
    else:
        raise Exception(str(response.json()))
    
if __name__ == "__main__":
    generate_image(USER_PROMPT)
    print(USER_PROMPT)

