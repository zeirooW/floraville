from flask import Flask, request, jsonify
from pymongo import MongoClient
import traceback

app = Flask(__name__)

uri = "mongodb+srv://yuzenn:HruvvlSa21CtbIcl@cluster0.taytznu.mongodb.net/?appName=Cluster0"
client = MongoClient(uri)

db = client["RobloxGame"]
players = db["Players"]

@app.route("/")
def index():
    return jsonify({"status": "ok"})

@app.route("/save", methods=["POST"])
def save_data():
    try:
        data = request.json
        user_id = data.get("UserId")
        player_data = data.get("Data")  # вложенная структура игрока

        if not user_id or player_data is None:
            return jsonify({"error": "Missing UserId or Data"}), 400

        players.update_one(
            {"UserId": user_id},
            {"$set": {"Data": player_data}},
            upsert=True
        )
        return jsonify({"success": True})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@app.route("/load/<int:user_id>", methods=["GET"])
def load_data(user_id):
    try:
        doc = players.find_one({"UserId": user_id}, {"_id": 0})
        if not doc:
            return jsonify({"Data": {}})
        return jsonify(doc)
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@app.route("/delete/<int:user_id>", methods=["DELETE"])
def delete_data(user_id):
    result = players.delete_one({"UserId": user_id})
    if result.deleted_count == 0:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"success": True, "message": f"Data for user {user_id} deleted."})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
