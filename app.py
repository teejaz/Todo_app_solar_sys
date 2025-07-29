from flask import Flask, render_template, request, send_file, jsonify
from parser import extract_tasks
import json
import io

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    chart_data = []
    goal = ""
    if request.method == "POST":
        raw_input = request.form["task_input"]
        tasks, goal = extract_tasks(raw_input)
        chart_data = [{"label": t["label"], "impact": t["impact"], "effort": t["effort"], "emoji": t["emoji"]} for t in tasks]
        return render_template("index.html", chart_data=chart_data, goal=goal, raw_json=json.dumps({"goal": goal, "tasks": chart_data}, indent=2))
    return render_template("index.html", chart_data=[], goal="", raw_json="")

@app.route("/download", methods=["POST"])
def download():
    json_data = request.form["json_data"]
    file_obj = io.BytesIO(json_data.encode("utf-8"))
    file_obj.seek(0)
    return send_file(file_obj, mimetype="application/json", as_attachment=True, download_name="impact_effort.json")

if __name__ == "__main__":
    app.run(debug=True)