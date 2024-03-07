
Welcome to the remote block storage app API with iSCSI
------

This project only runs on Linux preferably `Ubuntu 22.04` and `above`


> Please sure you are running as root user as this app will require root privileges to operate 

Accomplish the above as follows:

```bash
sudo su
```
> You will be prompted to enter your password and all should be good now

Next thing to do here is to update the system as follows
```bash
apt update
```

That said, ensure you have the following packages installed. Dont worry, there is a command below to install all of them
- [ ] git - You will need it to clone the repository 
- [ ] lvm - Linux Logical Volume Manager to deal with storage
- [ ] tgt - iscsi service to serve block devices over the network
- [ ] python virtual environment `python3-venv` as at this time of making this `README`
- [ ] Well networked environment to practice with (Virtualbox, VMware etc)



> To run this project, you will need to perform the following commands

First update the server  

```bash
apt-get upadte
```

Install required system dependecies
```bash
apt install git python3-venv lvm2 tgt
```

Clone repository
```bash
git clone https://github.com/arksnorman/isbat-final-year-project.git
```

Switc to the `api` directory in the project

```bash
cd isbat-final-year-project/api
```

Create a virtual environemnt for the API
```bash
python3 -m venv .venv
```

Activate the python environment
```bash
source .venv/bin/activate
```

Install project requirements/libraries
```bash
pip install -r requirements.txt
```

Prep the virtual storage on the system for testing purposes. This will take some time depending your system speed as in the background, the system is creating virtual storage devices (Linux Loop Devices)
```bash
python prep-dev.py
```

Next step is to create a `.env` file out of the `.env.example` file. This file contains environment variables use by the application. So by default, the `.env` is not available in the project directory and you have create it manually
```bash
cp .env.example .env
```
> This file contains environment variables to be use by the app like `EXCLUDED_DEVICES` which contains a comma seperated list of `CORE` linux block devices to not be used by the application while its performing its operations. Disks in this lisk can include your root partition, data back disk or partion etc

And finally start the API
```bash
python3 app.py
```

Enjoy :)
