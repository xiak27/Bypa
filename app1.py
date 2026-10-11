import os
from flask import Flask, request, jsonify
from auth_client1 import AutoBypassClient

app = Flask(__name__)
client = AutoBypassClient()

@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "online", "message": "Delta Ultimate Full-Auto Server 运行正常"})

@app.route("/api/bypass", methods=["GET", "POST"])
def bypass_api():
    if request.method == "POST":
        data = request.get_json() or {}
        url = data.get("url")
    else:
        url = request.args.get("url")

    if not url:
        return jsonify({"status": "error", "message": "缺少目标 URL"}), 400

    # 终极形态：直接传入目标链接，所有解析与过盾流程在后台全自动跑通
    result = client.execute_full_auto(url)
    
    if result.get("status") == "success":
        return jsonify(result)
    else:
        return jsonify(result), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True)
