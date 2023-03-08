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


- Installed and configured [Ngrok](https://dashboard.ngrok.com/get-started/setup) on your system. 
<br>This part is essential by now, cause we are going to run Django server on a local machine, but we can't get updates on it directly from Telegram Webhook. So, we'll use Ngrok as a Proxy between global an local nets; </br>

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

So, [like I said](#concept), you have to start Ngrok before starting the Django Webserver.
And make sure you're running Ngrok on the same port as it specified in .env file. This example assumes that you haven't changed the default configuration: `PORT=8000` 

```bash
 ngrok http 8000
```

Just wait until you see that session status is Online: 

![Ngrok-example](/img/ngrok-example.png)

Now you can finally start the Django Webserver:
```bash
 make dev
```

Or if you're willing to open admin panel directly:
```bash
 make admin
```

Webhook bot starts with this command:
```bash
 make webhook
```

After starting the server, you could open your browser and make some requests:<br>
```
localhost:8000/api/me/1077392747/

localhost:8000/api/me/0010101010/

localhost:8000/admin/
```

## Workflow Scheme

(Outdated, will be changed in future updates!)

![Workflow](/img/workflow.png)