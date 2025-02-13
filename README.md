# Discord Bot Template

Template to create a fully functional Discord bot with modular commands, logging, metrics, caching, and automated deployment. Used by a bot with 25,000+ servers.

**Tech Stack**

- Backend - Python, Redis, MySQL
- Deployment - Docker, Github Actions
- Monitoring - Prometheus, Grafana

## Demo

An example command & monitoring dashboard are provided.

![Screenshot 2025-02-12 212258](https://github.com/user-attachments/assets/99d87bd8-421f-4c90-b644-261cfc6fd99e)
![Screenshot 2025-02-12 200045](https://github.com/user-attachments/assets/8c109044-5733-49f7-9abb-a02704ed7544)


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

8. (Optional) Set up GitHub Actions in `Settings > Secrets and variables > Actions > Repository` for automatic deployment to a Linux server

   ```
   secrets.SSH_KEY
   secrets.SSH_USERNAME
   secrets.SSH_IP
   vars.DEPLOY_PATH
   ```
