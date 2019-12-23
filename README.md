# mercatus

Telegram Bot that send you updates about stocks/etf/etc. supported by Alpha Vantage.
They offfer a free tier API Key, so this is completely free.

## 🚀 Quickstart

Simply chat with the [bot](https://telegram.me/MercatusBot)

## 🖥 Self-Hosting

You can host it yourself of course. You will need a server.

### From a prebuilt docker image

```sh
wget https://raw.githubusercontent.com/cupcakearmy/mercatus/master/docker-compose.yml

# Set your own telegram bot token
vim docker-compose.yml

docker-compose up -d
```

### Completely from source

```sh
git clone https://github.com/cupcakearmy/mercatus

# Insert the variables found in the docker-compose.yml file with your token
touch .env
vim .env

docker-compose -f docker-compose.dev.yml up -d
```
