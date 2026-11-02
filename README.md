# Self-Healing Infrastructure using Prometheus, Alertmanager and Ansible

An automated infrastructure recovery project that monitors an NGINX web service, detects failures, sends alerts, and automatically restarts the failed Docker container using Ansible.

## Project Overview

This project demonstrates a self-healing mechanism using monitoring and automation tools.

When the NGINX service fails:

1. Prometheus detects the failure using monitoring metrics.
2. The `NginxDown` alert is triggered.
3. Alertmanager forwards the alert to a Python webhook receiver.
4. The Python receiver executes an Ansible playbook.
5. Ansible restarts the NGINX Docker container.
6. Prometheus detects service recovery and resolves the alert.

## Architecture

```text
              NGINX Web Server
                     |
                     v
             NGINX Exporter
                     |
                     v
                Prometheus
                     |
                NginxDown
                     |
                     v
               Alertmanager
                     |
                HTTP Webhook
                     |
                     v
             Python Receiver
                     |
                     v
                 Ansible
                     |
                     v
             Docker Restart
                     |
                     v
             NGINX Recovered
```

## Technologies Used

- Ubuntu WSL
- Docker
- Docker Compose
- NGINX
- Prometheus
- NGINX Prometheus Exporter
- Alertmanager
- Python
- Ansible
- Shell commands

## Project Structure

```text
self-healing-infrastructure/
│
├── alertmanager/
│   └── alertmanager.yml
│
├── ansible/
│   ├── recovery.yml
│   ├── recovery_receiver.py
│   └── recovery_receiver.log
│
├── nginx/
│   ├── index.html
│   └── default.conf
│
├── prometheus/
│   ├── prometheus.yml
│   └── alert-rules.yml
│
└── compose.yaml
```

## Prerequisites

Install and configure:

- Docker Desktop
- Ubuntu WSL
- Docker Compose
- Python 3
- Ansible

Ensure Docker Desktop WSL integration is enabled for Ubuntu.

## Installation and Execution

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd self-healing-infrastructure
```

### 2. Start the Docker services

```bash
docker compose up -d
```

### 3. Start the Python webhook receiver

Open a separate Ubuntu terminal:

```bash
python3 ansible/recovery_receiver.py
```

Keep this terminal running.

**Important:** The current Python receiver uses an absolute WSL path for the Ansible playbook. If you clone this project into another directory, update the `PLAYBOOK` path in `recovery_receiver.py`.

### 4. Verify the services

NGINX:

```bash
curl http://localhost:8085
```

Prometheus:

```bash
curl http://localhost:9091/-/healthy
```

Alertmanager:

```bash
curl http://localhost:9093/-/healthy
```

NGINX exporter:

```bash
curl -s http://localhost:9113/metrics | grep '^nginx_up'
```

### 5. Test automatic recovery

Stop the NGINX container:

```bash
docker stop self-healing-nginx
```

Wait approximately 30–45 seconds for monitoring and alert processing.

Check the alert:

```bash
curl -s http://localhost:9091/api/v1/alerts
```

Check the recovery logs:

```bash
tail -n 30 ansible/recovery_receiver.log
```

Check the NGINX container:

```bash
docker ps -a --filter name=self-healing-nginx
```

### 6. Verify successful recovery

```bash
curl -I http://localhost:8085
```

```bash
curl -s http://localhost:9113/metrics | grep '^nginx_up'
```

Expected results:

- HTTP response: `200 OK`
- Metric: `nginx_up 1`
- Ansible output: `NGINX recovery completed: self-healing-nginx`

## Monitoring URLs

| Service | URL |
|---|---|
| NGINX | http://localhost:8085 |
| Prometheus | http://localhost:9091 |
| Alertmanager | http://localhost:9093 |
| NGINX Exporter | http://localhost:9113/metrics |

## Test Results

The automatic recovery test was successfully completed.

| Test | Result |
|---|---|
| NGINX failure detection | Successful |
| Prometheus alert generation | Successful |
| Alertmanager webhook | Successful |
| Python receiver | Successful |
| Ansible playbook execution | Successful |
| Docker container restart | Successful |
| NGINX service recovery | Successful |
| Alert resolution | Successful |

## Learning Outcomes

- Monitoring infrastructure using Prometheus.
- Configuring alert rules and Alertmanager.
- Integrating Python webhooks.
- Automating recovery using Ansible.
- Managing Docker containers.
- Troubleshooting Linux and WSL environments.
- Understanding automated incident recovery.

## Conclusion

This project demonstrates how monitoring and automation tools can work together to detect infrastructure failures and automatically restore services. It provides practical DevOps experience in monitoring, alerting, Docker, Python automation, and Ansible.

**Project Status:** Core implementation and automatic recovery test completed.
