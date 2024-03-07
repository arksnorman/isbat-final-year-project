
Welcome to the remote block storage app API with iSCSI
------

This project only runs on Linux preferably `Ubuntu 22.04` and `above`


> Please ensure that you are running as root user as this app will require root privileges to operate 

Accomplish the above as follows:

```bash
sudo su
```
> You will be prompted to enter your password and all should be good now

Next thing to do here is to update the system as follows
```bash
apt update
```

That said, ensure that you have the following packages installed. Don't worry, there is a command below to install all of them
- [x] git - You will need it to clone the repository 
- [x] lvm - Linux Logical Volume Manager to deal with storage
- [x] tgt - iscsi service to serve block storage devices over the network
- [x] python virtual environment `python3-venv` at the time of making this `README`
- [x] Well networked environment with internet to practice with (Virtualbox, VMware etc)



> To run this project, you will need to perform a series of commands as follows

First update the server  

```bash
apt-get upadte
```

Install the required system dependencies
```bash
apt install git python3-venv lvm2 tgt
```

Clone the repository to your computer
```bash
git clone https://github.com/arksnorman/isbat-final-year-project.git
```

Switch to the `api` directory in the project

```bash
cd isbat-final-year-project/api
```

Create a virtual environment for the API
```bash
python3 -m venv .venv
```

Activate the new python environment
```bash
source .venv/bin/activate
```

Install all the project requirements/libraries
```bash
pip install -r requirements.txt
```

Prep the virtual storage on the system for testing purposes. This will take some time depending on your system speed. In the background, the system is creating virtual storage devices (Linux Loop Devices)
```bash
python prep-dev.py
```

Next step is to create a `.env` file out of the `.env.example` file. This file contains environment variables used by the application. By default, the `.env` is not available in the project directory, and you will have to create it manually as so
```bash
cp .env.example .env
```
> This file contains environment variables to be used by the app like `EXCLUDED_DEVICES` which contains a comma seperated list of `CORE` linux physical block devices that are not to be included in the app operations. Disks in this list may include your root partition, data backup disk etc

And finally start the API
```bash
python3 app.py
```

Enjoy :ristas:
