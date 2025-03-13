import os
from dotenv import load_dotenv

load_dotenv()


def is_running_in_docker() -> bool:
    return os.path.exists('/.dockerenv')


def get_env_variable(var_name: str) -> str:
    docker_env_vars = {
        "REDIS_CONNECTION_STRING": "redis://redis:6379",
        "RABBITMQ_CONNECTION_STRING": "amqp://guest:guest@rabbitmq:5672/",
        'RESULTS_DIR': 'results',
        'RESULTS_FILE_NAME': 'cracked_passwords.json'
    }

    if is_running_in_docker() and var_name in docker_env_vars:
        return docker_env_vars[var_name]

    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"Environment variable {var_name} is missing")
    return value
