from flask import Request, jsonify
from src.lvm import create_volume_group, extend_volume_group, delete_volume_group_forcefully, create_snapshot, \
    get_snapshots, delete_logical_volume_forcefully, restore_snapshot, get_logical_volume_details
from src.utils import create_tgt_config, reload_tgt


class Snapshots:
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
            return self.__get_snapshots()
        if self.request.method == "POST":
            return self.__create_snapshot()
        if self.request.method == "PUT":
            return self.__restore_snapshot()
        if self.request.method == "DELETE":
            return self.__delete_snapshot()

    def __get_snapshots(self):
        # data = self.get_data()
        block_device = self.request.args.get("blockDevice")
        success, data = get_snapshots(block_device)
        if not success:
            return jsonify(data), 500
        return jsonify(data)

    def __create_snapshot(self):
        data = self.get_data()
        pool = data["pool"]
        block_device = data["device"]

        success, msg = create_snapshot(pool, block_device)

        if success:
            return jsonify({}), 204
        return jsonify(msg), 400

    def __restore_snapshot(self):
        data = self.get_data()
        pool = data["pool"]
        block_device = data["device"]
        snapshot = data["snapshot"]

        iqn = "iqn.2024-01.com.example:norman.{}"

        success, msg = restore_snapshot(pool, snapshot, block_device)

        if success:
            new_success, new_data = get_logical_volume_details(pool, block_device)
            if not new_success:
                return jsonify("Failed to get lv data"), 500

            main_iqn = iqn.format(block_device)

            tgt_config = f"""<target {main_iqn}>
    backing-store {new_data["path"]}
</target>"""

            create_tgt_config(block_device, tgt_config)
            reload_tgt()
            return jsonify({}), 204
        return jsonify(msg), 400

    def __delete_snapshot(self):
        data = self.get_data()
        pool = data["pool"]
        block_device = data["device"]

        success, msg = delete_logical_volume_forcefully(pool, block_device)

        if success:
            return jsonify({}), 204
        return jsonify(msg), 500
