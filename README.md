<div align="center">
  <h1><strong>Django Telegram bot</strong></h1>
  <p>Telegram Banking bot with REST API. Based on Django framework and written in Python.</p>
</div>

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Workflow scheme](#workflow-scheme)

## Prerequisites
First of all, make sure you've already completed this steps:
- Installed Python 3.10 from [official source](https://www.python.org/downloads/release/python-31010/) or packet manager. 
<br> Yep, it's time to upgrade your lovely 3.9 :)</br>


- Installed and configured [Ngrok](https://dashboard.ngrok.com/get-started/setup) on your system (optional part). 
<br>This part is already optional. You can run webhook bot on a local machine, but can't get updates on it directly from Telegram Webhook. But using Ngrok as a Proxy between global an local nets could help; </br>

- Installed pipenv: `pip install pipenv`.
<br>

- Optionally installed `make` on your Windows machine. 
<br> Btw, the easiest way to do that is Chocolatey: `choco install make`  </br>


## Installation

(1) Clone this repo at first:
```bash
git clone https://gitlab.com/tooBusyNow/dt.backend.bank-bot.git
cd ./dt.backend.bank-bot
```
(2) Then create a personal `.env` file:
```bash
cat src/.env.example > src/.env
```

(3) Open `.env` file in `src` directory and change <b>TLG_TOKEN</b> value on your actual Token:
```bash
nano src/.env
```

(4) Activate pipenv shell (If you have errors on this step, then you've probably forgot to install Python 3.10.):
```bash
pipenv shell
```

(5) Now it's time to install dependencies: 
```bash
pipenv install
```

(6) Now you are ready to start! 🚀

## Usage

#### (1) Starting with Docker Compose:

```bash
make docker_run
```
It will automatically create superuser for test purposes
with credentials (you can use them in admin panel):
```
login: testadmin
pass: testpass
```

And in order to stop just run:
```bash
make docker_stop
```

After starting the server, you could open your browser and make some requests:<br>
```
localhost:8080/api/me/1077392747/

localhost:8080/api/me/0010101010/

localhost:8080/admin/
```

#### (2) Starting frontend
This will start Django HTTP server with admin panel.
```bash
make dev
```

#### (2) Start bot: polling mode.
This will start Django HTTP server with admin panel.
```bash
make polling
```

#### (4) Start bot: webhook mode. (Uses Ngrok!)
In this case command below starts Telegram bot with webhook. 
```bash
make webhook
```


## Workflow Scheme

(Outdated, will be changed in future updates!)

![Workflow](/img/workflow.png)