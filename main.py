from flask import Flask, render_template, request, send_from_directory
import sqlite3
from pytube import YouTube
import os

app = Flask(__name__)

output_folder = 'output'

def create_table():
  conn = sqlite3.connect('submit.db')
  cur = conn.cursor()
  cur.execute('''CREATE TABLE IF NOT EXISTS info(
              iid INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              song TEXT NOT NULL,
              link TEXT NOT NULL,
              filename TEXT NOT NULL)''')
  conn.commit()
  conn.close()

def show_table():
  conn = sqlite3.connect('submit.db')
  cur = conn.cursor()
  cur.execute('SELECT * FROM info')
  data = cur.fetchall()
  conn.close()
  return data

def download_song(url, output_path):
  yt = YouTube(url)
  audio_stream = yt.streams.filter(only_audio=True).first()
  audio_stream.download(output_path)
  return audio_stream.default_filename

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    name = request.form['name']
    song = request.form['song']
    link = request.form['link']
    if not os.path.exists(output_folder):
      os.makedirs(output_folder)

    # Download the song and get the filename
    filename = download_song(link, output_folder)
    
    conn = sqlite3.connect('submit.db')
    cur = conn.cursor()
    cur.execute('''INSERT INTO info(name, song, link, filename) VALUES(?, ?, ?, ?)''', (name, song, link, filename))
    conn.commit()
    conn.close()
    return render_template('index.html', audio_url=filename)
  data = show_table()
  return render_template('index.html', data=data)

# enable this function when there is more than 1 submission of the same thing

# @app.route('/delete', methods=['POST'])
# def delete():
#   iid = request.form['iid']
#   conn = sqlite3.connect('submit.db')
#   cur = conn.cursor()
#   cur.execute("DELETE FROM info WHERE iid=?", (iid,))
#   conn.commit()
#   conn.close()
#   data = show_table()
#   return render_template('index.html', data=data)

@app.route('/uploads/<path:filename>')
def serve_file(filename):
    return send_from_directory(output_folder, filename)

@app.route('/output/<path:filename>')
def get_file(filename):
    return send_from_directory(output_folder, filename)

create_table()

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)
