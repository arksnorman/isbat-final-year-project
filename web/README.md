
Welcome to the remote block storage app Frontend with iSCSI
------

This project only runs on Linux preferably `Ubuntu 22.04` and `above`

First step is to install `nodejs`. This is simple on ubuntu as you can use the snap package as follows
```bash
sudo snap install node --classic
```

If using snap packages is not an option, use the following
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - &&\
sudo apt-get install -y nodejs
```

Second step is to install required system dependecies
```bash
sudo apt update && apt install git
```
Clone repository
```bash
git clone https://github.com/arksnorman/isbat-final-year-project.git
```

Switct to the `web` directory in the project

```bash
cd isbat-final-year-project/web
```

Install the web application dependencies
```bash
npm install
```

Next step is to create a `.env` file out of the `.env.example` file. This file contains environment variables used by the web application. So by default, the `.env` is not available in the project directory and you have create it manually from the example file as follows
```bash
cp .env.example .env
```

> After that, open the  `.env` file and update the `VITE_API_URL` to the correct URL of the backend python `API`

Lastly, run the web app. :)

```bash
npm run dev
```

Enjoy :ristas:

