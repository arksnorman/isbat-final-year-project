from flask import Flask, jsonify, request

from src.lvm import create_volume_group, delete_volume_group_forcefully, extend_volume_group
from src.utils import list_unused_block_devices, get_all_lvm_info, get_data
from flask_cors import CORS

app = Flask(__name__)

CORS(app, origins='*')


@app.route("/storage-pools", methods=["GET", "POST", "DELETE", "PUT"])
def get_all_storage_pools():
    try:
        data = get_data(request)
        if request.method.upper() == "PUT":
            success, msg = extend_volume_group(data["name"], list(data["blockDevices"]))
            if success:
                return jsonify({}), 204
            return jsonify(msg), 500
        if request.method.upper() == "DELETE":
            success, msg = delete_volume_group_forcefully(list(data["volumeGroups"]))
            import time
            time.sleep(5)
            if success:
                return jsonify({}), 204
            return jsonify(msg), 500
        if request.method.upper() == "POST":
            print(data)
            success, msg = create_volume_group(data["name"], list(data["blockDevices"]))
            if success:
                return jsonify({}), 204
            return jsonify(msg), 400
        return jsonify(get_all_lvm_info())
    except Exception as e:
        return jsonify({"message": f"Exception from backend: {str(e)}"}), 500


@app.route("/block-devices", methods=["GET"])
def get_unused_block_devices():
    try:
        return jsonify(list_unused_block_devices())
    except Exception as e:
        return jsonify({"message": f"Exception from backend: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
