import os


devices = [
    {"name": "loop70", "file": "70.img", "size": 30000},
    {"name": "loop71", "file": "71.img", "size": 6000},
    {"name": "loop72", "file": "72.img", "size": 2000},
    {"name": "loop73", "file": "73.img", "size": 2000}
]

try:
    for dev in devices:
        file = dev["file"]
        size = dev["size"]
        name = dev["name"]
        os.system(f"dd if=/dev/zero of=/opt/{file} bs=1M count={size}")
        os.system(f"losetup /dev/{name} /opt/{file}")
    print("Environment is ready")
    exit(0)
except Exception as e:
    print("Error setting up environment: ", str(e))
    exit(1)
