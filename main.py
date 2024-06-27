from flask import Flask, request
import base64
import ffmpeg
import subprocess
app = Flask(__name__)

def extract_using_ffmpeg_subprocess(video_url: str, timestamp: str, image_name: str) -> bool:
  print(video_url, timestamp, image_name)
  try:
    print('start extract')
    command = ['ffmpeg', '-ss', str(timestamp), '-i', video_url, '-vframes', '1', image_name , '-y'] 
    subprocess.run(command)
    print('end extract')
    return True
  except Exception as e:
    print("[Extraction error]", e)
    return False

@app.route('/', methods=['POST'])
def extract():
  if request.method != 'POST': 
    return ('Method not allowed', 405)
  
  data = request.get_json()
  video_url = data['url'] if 'url' in data else None
  timestamp = data['timestamp'] if 'timestamp' in data else None
  image_name = f'{timestamp}.jpg'
  
  if not video_url or (timestamp != 0 and not timestamp):
    return {'error':'Invalid argument in url or time'}, 400
  
  subprocess_res = extract_using_ffmpeg_subprocess(video_url, timestamp, image_name)
  
  if not subprocess_res:
    return {'error':'FFMPEG error'}, 500
  
  data = None
  
  try:
    with open(image_name, "rb") as image_file:
      image_data = image_file.read()
      
    data = base64.b64encode(image_data).decode("utf-8")
    
  except FileNotFoundError:
    print(f"Error: File '{image_name}' not found.")
    return {'error':'Internal server error'}, 500
  
  return {"msg":'ok', "data": data}, 200


if __name__ == "__main__":
    from waitress import serve
    print(f'Running on http://localhost:8080')
    serve(app, host="0.0.0.0", port=8080)