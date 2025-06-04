from flask import Flask, render_template, request, send_from_directory
import openai
import os
from moviepy.editor import ImageClip, concatenate_videoclips

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    images = []
    video_file = None
    if request.method == "POST":
        prompt = request.form.get("prompt")
        action = request.form.get("action")

        if prompt:
            if action == "generate_image":
                # Generate 1 gambar dari prompt
                response = openai.Image.create(
                    prompt=prompt,
                    n=1,
                    size="512x512"
                )
                image_url = response['data'][0]['url']
                images.append(image_url)

            elif action == "generate_video":
                # Generate beberapa gambar, lalu buat video slideshow
                frames = []
                for i in range(3):  # generate 3 gambar
                    resp = openai.Image.create(
                        prompt=f"{prompt} frame {i+1}",
                        n=1,
                        size="512x512"
                    )
                    frames.append(resp['data'][0]['url'])

                # Download images ke lokal (Replit perlu modifikasi khusus, contoh di PC lokal)
                import requests
                local_images = []
                for idx, url in enumerate(frames):
                    img_data = requests.get(url).content
                    filename = f"static/frame_{idx}.png"
                    with open(filename, "wb") as f:
                        f.write(img_data)
                    local_images.append(filename)

                # Buat video slideshow dengan moviepy
                clips = [ImageClip(img).set_duration(2) for img in local_images]
                video = concatenate_videoclips(clips, method="compose")
                video_output = "static/videos/output_video.mp4"
                os.makedirs("static/videos", exist_ok=True)
                video.write_videofile(video_output, fps=24)

                video_file = video_output

    return render_template("index.html", images=images, video_file=video_file)

@app.route('/static/videos/<filename>')
def send_video(filename):
    return send_from_directory('static/videos', filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
  
