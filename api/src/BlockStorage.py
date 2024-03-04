from flask import Request, jsonify
from src.lvm import create_volume_group, extend_volume_group, delete_volume_group_forcefully, get_logical_volumes, \
    delete_logical_volume_forcefully, has_enough_space, create_logical_volume, get_logical_volume_details
from src.utils import get_all_vg_info, create_tgt_config, reload_tgt, remove_tgt_config_and_reload_tgt


class BlockStorage:
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
            return self.__get_all_block_devices()
        if self.request.method == "POST":
            return self.__create_block_storage()
        if self.request.method == "DELETE":
            return self.__delete_block_device()

    @staticmethod
    def __get_all_block_devices():
        vg_data = get_all_vg_info()

        iqn = "iqn.2024-01.com.example:norman.{}"
        config = """VBoxManage storageattach virtual-machine-name --storagectl SATA --port 1 --device 0 --type hdd --medium iscsi --server 192.168.56.21 --target {} --lun 1"""

        if len(vg_data) == 0:
            return jsonify([])
        res = []
        for vg in vg_data:
            vg_name = vg["name"]
            # print(vg_name)
            success, vols = get_logical_volumes(vg_name)
            if success:
                for vol in vols:
                    main_iqn = iqn.format(vol["name"])
                    vol["pool"] = vg_name
                    vol["config"] = config.format(main_iqn)
                    res.append(vol)
        return jsonify(res)

    def __create_block_storage(self):
        data = self.get_data()
        name = data["name"]
        size = int(float(data["size"]) * 1024)
        pool = data["pool"]

        iqn = "iqn.2024-01.com.example:norman.{}"

        if not has_enough_space(pool, f"{size}M"):
            return jsonify({"Not enough space on storage pool"})

        success, msg = create_logical_volume(pool, name, f"{size}M")
        if success:
            new_success, new_data = get_logical_volume_details(pool, name)
            if not new_success:
                return jsonify("Failed to get lv data"), 500

            main_iqn = iqn.format(name)

            tgt_config = f"""<target {main_iqn}>
    backing-store {new_data["path"]}
</target>"""

            create_tgt_config(name, tgt_config)
            reload_tgt()
            return jsonify({}), 204
        return jsonify(msg), 400

    def __delete_block_device(self):
        try:
            data = self.get_data()
            pool = data["storagePool"]
            device = data["blockDevice"]
            remove_tgt_config_and_reload_tgt(device)
            success, msg = delete_logical_volume_forcefully(pool, device)
            if success:
                return jsonify({}), 204
            return jsonify(msg), 500
        except Exception as e:
            return jsonify(f"Failed to remove block storage: {str(e)}"), 500
