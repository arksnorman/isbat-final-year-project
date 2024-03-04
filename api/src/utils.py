import hashlib
import json
import re
import subprocess
from dotenv import load_dotenv
import os

app_dir = os.path.dirname(os.path.abspath(__file__))
used_devices_file = os.path.join(app_dir, "storage", "used-devices.json")

load_dotenv()

EXCLUDED_DEVICES = os.getenv("EXCLUDED_DEVICES")

DEV_LIST = EXCLUDED_DEVICES.split(",")


def calculate_md5(input_string):
    md5_hash = hashlib.md5(input_string.encode()).hexdigest()
    return md5_hash


def get_used_devices():
    if not os.path.exists(used_devices_file):
        return []

    try:
        with open(used_devices_file) as f:
            return list(json.load(f))
    except Exception as e:
        print(f"Error loading used devices: {str(e)}")
        return []


def note_down_used_devices(devices: list):
    used_devices = get_used_devices()
    new_list = set(devices + used_devices)
    try:
        with open(used_devices_file, "w") as f:
            json.dump(new_list, f)
    except Exception as e:
        print(f"Error note down used devices: {str(e)}")


def get_data(request):
    try:
        return request.get_json()
    except:
        return {}


def list_unused_block_devices():
    output = subprocess.check_output(['lsblk', '-n', '-o', 'SIZE,MOUNTPOINT,PATH,TYPE'])
    output = output.decode('utf-8').strip().split('\n')
    allowed_devices = ["loop", "disk", "part"]

    used, unused = get_physical_volumes()

    print(used, unused)

    unused_devices = []

    for line in output:
        parts = line.split()

        if len(parts) == 3:
            size, raw_device, device_type = parts
            clean_device = raw_device.strip()
            device = clean_device if clean_device not in set(DEV_LIST + get_used_devices() + used) else None
            if device is not None and device_type.strip() in allowed_devices:
                unused_devices.append({"device": device, "size": size})

    return unused_devices


def get_all_vg_info():
    cmd = ['vgs', '--units', 'g', '--noheadings', '--nosuffix', '--separator', ':', '-o', 'vg_name,vg_size,vg_free']
    vgs_output = subprocess.check_output(cmd).decode('utf-8')

    vgs_lines = vgs_output.strip().split('\n')

    vg_info = []

    for line in vgs_lines:
        if len(line) == 0:
            continue

        fields = line.strip().split(':')

        vg_name = fields[0].strip()
        vg_size = float(fields[1].strip())
        vg_free = float(fields[2].strip())

        vg_used = vg_size - vg_free

        vg_info.append({"name": vg_name, "size": vg_size, "usedSize": vg_used})

    return vg_info


def is_used_device(devices: list):
    used_devices = get_used_devices()
    for device in devices:
        if device in used_devices:
            return True
    return False


def free_devices(devices: list):
    used_devices = set(get_used_devices())
    for device in devices:
        if device in used_devices:
            used_devices.remove(device)

    try:
        with open(used_devices_file, "w") as f:
            json.dump(used_devices, f)
    except Exception as e:
        print(f"Error note down free/used devices: {str(e)}")


def get_physical_volumes():
    cmd = ['pvs', '--noheadings', '-o', 'pv_name,vg_name', '--separator', ':']
    output = subprocess.check_output(cmd, text=True)

    lines = output.split('\n')

    unused_physical_volumes = []
    used_devices = []

    for line in lines:
        fields = line.split(':')

        if len(fields) == 2:
            pv_name, vg_name = fields

            if vg_name.strip() == "":
                unused_physical_volumes.append(pv_name.strip())
            else:
                used_devices.append(pv_name.strip())

    return used_devices, unused_physical_volumes


def reload_tgt():
    if not check_service_status("tgt"):
        start_service("tgt")
    try:
        os.system("service tgt reload")
    except Exception as e:
        print("Failed to reload tgt: ", str(e))


def check_service_status(service_name):
    try:
        subprocess.run(["service", service_name, "status"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def start_service(service_name):
    """Start a service."""
    try:
        subprocess.run(["service", service_name, "restart"], check=True)
        print(f"Service '{service_name}' started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error starting service '{service_name}': {e}")


def create_tgt_config(dev_name, config):
    try:
        with open(f"/etc/tgt/conf.d/{dev_name}.conf", "w") as f:
            f.write(config)
    except Exception as e:
        print("Failed top save config: ", str(e))


def remove_tgt_config_and_reload_tgt(dev_name):
    try:
        os.system(f"rm -rf /etc/tgt/conf.d/{dev_name}.conf")
        reload_tgt()
    except Exception as e:
        print("Failed remove config: ", str(e))


def remove_non_alphanumeric_from_ends(string):
    # Using regular expression to remove non-alphanumeric characters from the beginning and end of the string
    return re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', string)
