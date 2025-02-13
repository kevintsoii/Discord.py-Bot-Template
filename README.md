# Discord Bot Template

Discord.py bot template to create a fully functioning bot with modular commands, logging, metrics, and caching. Used by a bot with 25,000+ servers.

**Tech Stack**

- Backend - Python, Redis, MySQL
- Deployment - Docker, Github Actions
- Monitoring - Prometheus, Grafana

**Contents**

- Get Started
- Caching
- Monitoring

## Demo

## Prerequisites

- [Python](https://www.python.org/) 3+
- [Docker](https://www.docker.com/)

## Getting Started

1. Create an `.env` file with your Discord bot token(s)

   ```
   TOKEN=
   TEST_TOKEN=
   ```

2. Modify settings in `config.py`

3. Modify DB initialization in `db/init.sql`

4. (Optional) Set up a venv

   ```
   python -m venv .venv
   ```

5. (Optional) Run the test version to experiment with new commands (no MySQL, Redis, or Prometheus)

   ```
   run-test.bat
   ```

6. Run the bot in production

   ```
   docker compose up --build
   ```

7. (Optional) Set up a Dashboard in Grafana: http://localhost:3000/

   - add a data source
   - import `grafana/dashboard.json` after replacing the data source ID

8. (Optional) Set up GitHub Actions for automatic deployment to a Linux server

   ```
   secrets.SSH_IP
   secrets.SSH_USERNAME
   secrets.SSH_IP
   vars.DEPLOY_PATH
   ```