from flask import Flask, render_template, jsonify
import subprocess, pymongo, json

app = Flask(__name__)

with open("enviroment.json","r") as file:
    enviroment = json.loads(s=file.read())

client = pymongo.MongoClient(enviroment["db_string"])
db = client["x_trends"]
collection = db["trends"]

@app.route('/')
def index():
    return render_template(template_name_or_list='index.html')

@app.route('/run-script')
def run_script():

    subprocess.run(["python", "scrapper.py"])

    latest_record = collection.find()

    data = []

    for x in latest_record:
        data.append(x)

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
