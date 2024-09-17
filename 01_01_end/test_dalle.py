from openai import OpenAI
client = OpenAI()

prompt = "a white siamese cat, cartoon style"

response = client.images.generate(
  model="dall-e-3",
  prompt=prompt,
  size="1024x1024",
  quality="standard",
  n=1,
)

image_url = response.data[0].url
print(image_url)