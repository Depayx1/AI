from flask import Flask, render_template_string, request, send_from_directory
import openai
import os
import requests
from moviepy.editor import ImageClip, concatenate_videoclips

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Generate Foto & Video AI</title>
</head>
<body>
  <h1>Generate Foto & Video AI dari Teks</h1>
  <form method="POST">
    <input type="text" name="prompt" placeholder="Masukkan deskripsi" required />
    <br/><br/>
    <button type="submit" name="action" value="generate_image">Generate Foto</button>
    <button type="submit" name="action" value="generate_video">Generate Video</button>
  </form>

  <hr/>

  {% if images %}
    <h2>Hasil Gambar:</h2>
    {% for img in images %}
      <img src="{{ img }}" alt="Generated Image" width="300" />
    {% endfor %}
  {% endif %}

  {% if video_file %}
    <h2>Hasil Video:</h2>
    <video width="480" controls>
      <source src="{{ video_file }}" type="video/mp4" />
      Your browser does not support the video tag.
    </video>
  {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    images = []
    video_file = None
    if request.method == "POST":
        prompt = request.form.get("prompt")
        action = request.form.get("action")

        if prompt:
            if action == "generate_image":
                response = openai.Image.create(
                    prompt=prompt,
                    n=1,
                    size="512x512"
                )
                image_url = response['data'][0]['url']
                images.append(image_url)

            elif action == "generate_video":
                frames = []
                for i in range(3):
                    resp = openai.Image.create(
                        prompt=f"{prompt} frame {i+1}",
                        n=1,
                        size="512x512"
                    )
                    frames.append(resp['data'][0]['url'])

                local_images = []
                os.makedirs("static_frames", exist_ok=True)
                for idx, url in enumerate(frames):
                    img_data = requests.get(url).content
                    filename = f"static_frames/frame_{idx}.png"
                    with open(filename, "wb") as f:
                        f.write(img_data)
                    local_images.append(filename)

                clips = [ImageClip(img).set_duration(2) for img in local_images]
                video_output = "static_frames/output_video.mp4"
                video = concatenate_videoclips(clips, method="compose")
                video.write_videofile(video_output, fps=24)

                video_file = "/" + video_output

    return render_template_string(HTML, images=images, video_file=video_file)

@app.route('/static_frames/<path:filename>')
def static_files(filename):
    return send_from_directory('static_frames', filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
    
