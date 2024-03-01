import re
import subprocess
from dotenv import load_dotenv
import os

load_dotenv()

EXCLUDED_DEVICES = os.getenv("EXCLUDED_DEVICES")

DEV_LIST = EXCLUDED_DEVICES.split(",")


def get_data(request):
    try:
        return request.get_json()
    except:
        return {}


def list_unused_block_devices():
    output = subprocess.check_output(['lsblk', '-n', '-o', 'NAME,SIZE,MOUNTPOINT'])
    output = output.decode('utf-8').strip().split('\n')

    unused_devices = []

    for line in output:
        parts = line.split()

        if len(parts) == 2:
            raw_device, size = parts
            clean_device = remove_non_alphanumeric_from_ends(raw_device)
            device = clean_device if clean_device not in DEV_LIST else None
            if device is not None:
                unused_devices.append({"device": f"/dev/{device}", "size": size})

    return unused_devices


def get_all_lvm_info():
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


def remove_non_alphanumeric_from_ends(string):
    # Using regular expression to remove non-alphanumeric characters from the beginning and end of the string
    return re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', string)
