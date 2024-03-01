import re
import subprocess


def check_vg_space(vg_name, lv_size):
    try:
        cmd = ['vgdisplay', '--units', 'b', '--noheadings', '--nosuffix', vg_name]
        vgdisplay_output = subprocess.check_output(cmd).decode('utf-8')

        # Extract the total size and free size of the volume group from the output
        total_size_match = re.search(r"VG Size\s+(\d+)\s", vgdisplay_output)
        free_size_match = re.search(r"Free\s+\d+\s+(\d+)\s", vgdisplay_output)

        if total_size_match and free_size_match:
            total_size = int(total_size_match.group(1))
            free_size = int(free_size_match.group(1))
            lv_size_bytes = convert_size_to_bytes(lv_size)

            if lv_size_bytes <= free_size:
                return True
            else:
                print("Error: Not enough free space in the volume group.")
                return False
        else:
            print("Error: Failed to retrieve volume group information.")
            return False
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
    if unit in units:
        return int(size[:-1]) * units[unit]
    else:
        return int(size)


def create_logical_volume(vg_name, lv_name, lv_size):
    try:
        subprocess.run(['lvcreate', '-n', lv_name, '-L', lv_size, vg_name], check=True)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, str(e)


def get_logical_volumes(vg_name):
    try:
        cmd = ['lvs', '--units', 'b', '--noheadings', '--nosuffix', '--separator', '|', '-o', 'lv_name,lv_path,lv_size,lv_attr']
        lvs_output = subprocess.check_output(cmd).decode('utf-8')

        lvs_lines = lvs_output.strip().split('\n')

        logical_volumes = []

        for line in lvs_lines:
            # Split the line into fields
            fields = line.strip().split('|')
            # Extract logical volume name, path, size, and attributes
            lv_name = fields[0].strip()
            lv_path = fields[1].strip()
            lv_size = int(fields[2].strip())
            lv_attr = fields[3].strip()
            # Calculate disk usage
            lv_disk_usage = lv_size if 's' not in lv_attr else 0
            # Append LV information to the list
            logical_volumes.append({
                'name': lv_name,
                'path': lv_path,
                'size': lv_size,
                'disk_usage': lv_disk_usage
            })

        return True, logical_volumes
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
        subprocess.run(['vgextend', vg_name] + list(devices), check=True)
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
