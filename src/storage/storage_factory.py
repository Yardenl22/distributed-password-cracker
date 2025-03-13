from pathlib import Path

from src.common import utils
from src.common.config import config
from src.storage.base import BaseStorage
from src.storage.json import JSONStorage


RESULTS_DIRECTORY: str = utils.get_env_variable('RESULTS_DIR')
RESULTS_FILE_NAME: str = utils.get_env_variable('RESULTS_FILE_NAME')


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = ROOT_DIR / RESULTS_DIRECTORY
RESULTS_FILE_PATH = RESULTS_DIR / RESULTS_FILE_NAME
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


class StorageFactory:
    @staticmethod
    def get_storage() -> BaseStorage:
        storage_type = config.SERVICE.STORAGE_TYPE.lower()

        if storage_type == 'json':
            return JSONStorage(storage_path=str(RESULTS_FILE_PATH))
        else:
            raise ValueError(f'Unknown storage type: {storage_type}')

storage = StorageFactory.get_storage()
