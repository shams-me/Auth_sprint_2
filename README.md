# Async API for Auth Service

Asynchronous Auth API is designed to provide a simple and easy-to-use API for user authentication and authorization.

### Technologies Used

- **Language**: Python + FastAPI
- **Server**: ASGI server (uvicorn)
- **Storage**: ElasticSearch
- **Caching**: Redis Cluster
- **Containerization**: Docker

## Installation and Usage

Follow these steps to install and run the project:

1. Clone the repository:

```shell
git clone https://github.com/chingisdev/Auth_sprint_1.git
```

</br>

2. Set up the environment variables in an .env file in the root of the project:

| Variable                       | Explanation                  | Example               |
|--------------------------------|------------------------------|-----------------------|
| `POSTGRES_HOST`                | PostgreSQL Hostname          | `postgres_test`       |
| `POSTGRES_PASSWORD`            | PostgreSQL Password          | `123qwe`              |
| `POSTGRES_USER`                | PostgreSQL User              | `app`                 |
| `POSTGRES_DB`                  | PostgreSQL Database Name     | `movies_database`     |
| `POSTGRES_PORT`                | PostgreSQL Port              | `5432`                |
| `REDIS_HOST`                   | Redis Hostname               | `redis_test`          |
| `REDIS_PORT`                   | Redis Port                   | `6379`                |
| `JWT_SECRET`                   | Secret key to generate token | `some_mega_hard_pass` |
| `SERVICE_HOST`                 | Service Host                 | `localhost`           |
| `SERVICE_PORT`                 | Service Port                 | `8000`                |
| `CACHE_EXPIRE_TIME_IN_SECONDS` | Cache expire time            | `600`                 |

</br>

3. make sure that every service in `docker-compose.yml` pointing to your env file:

```yaml
    env_file:
      - <your_path/.env>
```

4. Start the services:

```shell
docker-compose up
```

This command will:

- Start the containers
- Initialize the PostgreSQL database
- Initialize the Redis database
- Creates superuser with roles
- Start the auth API service

## Features

You can explore all the API endpoints through Swagger's interactive documentation. Once you have launched the
application, simply copy and paste the following URL into your browser's address bar:

`http://localhost:8000/api/openapi`

This will provide you with detailed information about each endpoint, allowing you to understand and interact with the
API more effectively.

## Contribution Guidelines

When contributing to this project, please follow these naming conventions for branches:

- **Valid Branch Actions (as action):** Use `feat` for features or `fix` for bug fixes.
- **Goal Action (as goal):** The goal must start with a verb and describe the branch's purpose.

### Valid Branch Name Example

Format: `issue_number/action-goal`

Example: `15/feat-add-sort-query-results`

## Setup Development Environment

1. You can prepare your local environment with this:

```shell
python -m venv venv &&
. venv/bin/activate &&
pip install -r requirements.txt &&
pre-commit install
```
