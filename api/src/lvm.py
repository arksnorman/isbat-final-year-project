import subprocess
import time
from src.utils import calculate_md5


def restore_snapshot(vg, snapshot_name, original_lv_name):
    try:
        subprocess.run(["lvconvert", "--mergesnapshot", f"{vg}/{snapshot_name}"], check=True)
        subprocess.run(["lvchange", "--refresh", f"{vg}/{original_lv_name}"], check=True)
        return True, None
    except Exception as e:
        return False, f"Error restoring snapshot: {e}"


def get_snapshots(lv):
    try:
        cmd = ['lvs', '--units', 'g', '--noheadings', '--nosuffix', '--separator', '#', '-o', 'lv_name,lv_path,lv_size,lv_time,origin']
        output = subprocess.check_output(cmd).decode('utf-8')

        lvs_lines = output.strip().split('\n')

        logical_volumes = []

        for line in lvs_lines:
            if len(line.strip()) == 0:
                continue

            fields = line.strip().split("#")
            lv_name, lv_path, lv_size, lv_time, origin = fields

            if len(origin.strip()) > 0 and lv == origin.strip():
                logical_volumes.append({
                    'name': lv_name.strip(),
                    'path': lv_path.strip(),
                    'size': lv_size.strip(),
                    "time": lv_time.strip(),
                    "origin": origin.strip(),
                })

        return True, logical_volumes
    except Exception as e:
        return False, str(e)


def create_snapshot(vg, lv):
    try:
        lv_info = get_logical_volume_details(vg, lv)
        success, data = lv_info

        if not success:
            return False, data

        size = str(int(float(data["size"]) * 1024)) + "M"

        if not has_enough_space(vg, size):
            return False, "Not enough space on storage pool"
        snapshot_name = calculate_md5(str(time.time()))
        subprocess.run(["lvcreate", "--snapshot", "--name", snapshot_name, "--size", size, f"{vg}/{lv}"], check=True)
        return True, None
    except Exception as e:
        return False, f"Error creating snapshot: {str(e)}"


def has_enough_space(vg_name, lv_size):
    try:
        cmd = ['vgs', '--units', 'b', '--noheadings', '--nosuffix', '--separator', ':', '-o', 'vg_size,vg_free', vg_name]
        output = subprocess.check_output(cmd).decode('utf-8')
        output = output.strip()

        if len(output) == 0:
            return False

        fields = output.split(":")
        free_size = int(fields[1])

        lv_size_bytes = convert_size_to_bytes(lv_size)

        if lv_size_bytes <= free_size:
            return True
        return True
    except subprocess.CalledProcessError:
        print("Error: Failed to retrieve volume group information.")
        return False


def convert_size_to_bytes(size):
    """
    Converts size from human-readable format (e.g., '1G' for 1 gigabyte) to bytes.

    Parameters:
        size (str): Size in human-readable format.

    Returns:
        int: Size in bytes.
    """
    units = {'K': 1024, 'M': 1024 ** 2, 'G': 1024 ** 3, 'T': 1024 ** 4}
    unit = size[-1]
    if str(unit).upper() in units.keys():
        return int(size[:-1]) * units[unit]
    else:
        return int(size)


def create_logical_volume(vg_name, lv_name, lv_size):
    try:
        subprocess.run(['lvcreate', '-n', lv_name, '-L', lv_size, vg_name], check=True)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, str(e)


def delete_logical_volume_forcefully(vg_name, lv_name):
    try:
        subprocess.run(['lvremove', '--force', '/dev/' + vg_name + '/' + lv_name], check=True)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, str(e)


def get_logical_volumes(vg_name):
    try:
        cmd = ['lvs', '--units', 'g', '--noheadings', '--nosuffix', '--separator', '#', '-o', 'lv_name,lv_path,lv_size,lv_time,origin']
        lvs_output = subprocess.check_output(cmd).decode('utf-8')

        lvs_lines = lvs_output.strip().split('\n')

        logical_volumes = []

        for line in lvs_lines:
            if len(line.strip()) == 0:
                continue

            fields = line.strip().split("#")
            lv_name, lv_path, lv_size, lv_time, origin = fields

            if len(origin.strip()) == 0:
                logical_volumes.append({
                    'name': lv_name.strip(),
                    'path': lv_path.strip(),
                    'size': lv_size.strip(),
                    "time": lv_time.strip(),
                    "origin": origin.strip(),
                })

        return True, logical_volumes
    except subprocess.CalledProcessError as e:
        return False, str(e)


def get_logical_volume_details(vg_name, lv):
    try:
        cmd = ['lvs', '--units', 'g', '--noheadings', '--nosuffix', '--separator', '#', '-o', 'lv_name,lv_path,lv_size,lv_time,origin', f"{vg_name}/{lv}"]
        output = subprocess.check_output(cmd).decode('utf-8')
        output = output.strip()

        fields = output.split("#")
        lv_name, lv_path, lv_size, lv_time, origin = fields

        return True, {
            'name': lv_name.strip(),
            'path': lv_path.strip(),
            'size': lv_size.strip(),
            "time": lv_time.strip(),
            "origin": origin.strip(),
        }
    except subprocess.CalledProcessError as e:
        return False, str(e)


def create_volume_group(vg_name: str, devices: list):
    try:
        subprocess.run(['vgcreate', vg_name] + list(devices), check=True)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, str(e)


def extend_volume_group(vg_name, devices: list):
    try:
        subprocess.run(['vgextend', vg_name] + list(set(devices)), check=True)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, str(e)


def delete_volume_group_forcefully(volume_groups: list):
    failed_vgs_errors = []

    for volume in volume_groups:
        try:
            subprocess.run(['vgremove', '--force', volume], check=True)
        except subprocess.CalledProcessError as e:
            failed_vgs_errors.append(f"Storage pool [{volume}] encountered error while being deleted: {str(e)}")

    if len(failed_vgs_errors) == 0:
        return True, None
    return False, "<br>".join(failed_vgs_errors)
