import time

from flask import Flask, jsonify, request
from src.BlockStorage import BlockStorage
from src.StoragePool import StoragePool
from src.Snapshots import Snapshots
from flask_cors import CORS

from src.utils import list_unused_block_devices

app = Flask(__name__)

CORS(app, origins='*')

storage_pools = StoragePool()
block_storage = BlockStorage()
snapshots = Snapshots()


@app.route("/storage-pools", methods=["GET", "POST", "DELETE", "PUT"])
def get_all_storage_pools():
    try:
        time.sleep(1)
        return storage_pools.execute(request)
    except Exception as e:
        return jsonify({"message": f"Exception from backend: {str(e)}"}), 500


@app.route("/block-storage", methods=["GET", "POST", "DELETE", "PUT"])
def get_unused_block_devices():
    try:
        time.sleep(1)
        return block_storage.execute(request)
    except Exception as e:
        return jsonify({"message": f"Exception from backend: {str(e)}"}), 500


@app.route("/physical-devices", methods=["GET"])
def get_unused_physical_devices():
    try:
        time.sleep(1)
        return jsonify(list_unused_block_devices())
    except Exception as e:
        return jsonify({"message": f"Exception from backend: {str(e)}"}), 500


@app.route("/snapshots", methods=["GET", "POST", "DELETE", "PUT"])
def deal_with_snapshots():
    try:
        time.sleep(1)
        return snapshots.execute(request)
    except Exception as e:
        return jsonify({"message": f"Exception from backend: {str(e)}"}), 500


# @app.route('/snapshot/download')
# def download_file():
#     # Assuming the file you want to serve is named 'example.txt' and located in the same directory as your Flask app
#     file_path = 'example.txt'
#     # Set the name that will be used when the file is downloaded
#     file_name = 'example.txt'
#     # Send the file to the client
#     return send_file(file_path, as_attachment=True, attachment_filename=file_name)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
