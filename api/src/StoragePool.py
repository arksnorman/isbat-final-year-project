from flask import Request, jsonify
from src.lvm import create_volume_group, extend_volume_group, delete_volume_group_forcefully
from src.utils import is_used_device, note_down_used_devices, get_all_vg_info


class StoragePool:
    def __init__(self):
        self.request = None

    def get_data(self):
        try:
            return self.request.get_json()
        except Exception as e:
            print("Error getting json data from request: ", str(e))
            return None

    def execute(self, request: Request):
        self.request = request
        if self.request.method == "GET":
            return self.__get_all_storage_pools()
        if self.request.method == "POST":
            return self.__create_pool()
        if self.request.method == "PUT":
            return self.__extend_pool()
        if self.request.method == "DELETE":
            return self.__delete_pool()

    @staticmethod
    def __get_all_storage_pools():
        return jsonify(get_all_vg_info())

    def __create_pool(self):
        data = self.get_data()
        block_devices = list(data["blockDevices"])
        if is_used_device(block_devices):
            return jsonify("Device is already used"), 400
        success, msg = create_volume_group(data["name"], block_devices)
        if success:
            note_down_used_devices(block_devices)
            return jsonify({}), 204
        return jsonify(msg), 400

    def __extend_pool(self):
        data = self.get_data()
        block_devices = list(data["blockDevices"])
        if is_used_device(block_devices):
            return jsonify("Device is already used"), 400
        success, msg = extend_volume_group(data["name"], block_devices)
        if success:
            note_down_used_devices(list(data["blockDevices"]))
            return jsonify({}), 204
        return jsonify(msg), 500

    def __delete_pool(self):
        data = self.get_data()
        volume_groups = list(data["volumeGroups"])
        success, msg = delete_volume_group_forcefully(volume_groups)
        if success:
            return jsonify({}), 204
        return jsonify(msg), 500
