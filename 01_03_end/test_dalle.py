from openai import OpenAI
client = OpenAI()

user_prompt = "programming cat"

prompt_template = "A cute sticker of {}, cartoon style"

prompt = prompt_template.format(user_prompt)

response = client.images.generate(
  model="dall-e-3",
  prompt=prompt,
  size="1024x1024",
  quality="standard",
  n=1,
)

image_url = response.data[0].url
print(image_url)