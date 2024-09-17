from openai import OpenAI
client = OpenAI()

prompt = "a white siamese cat, cartoon style"

with open("cartoon_cat.png", "rb") as image_file:
    response = client.images.create_variation(
      model="dall-e-2",
      image=image_file,
      n=1,
      size="1024x1024",
    )


image_url = response.data[0].url
print(image_url)