DB_HOST = 'comp520_project-db-1'
DB_NAME = 'BlogService'
DB_USERNAME = 'root'
DB_PASSWORD = 'pass'
FLASK_SECRET_KEY = 'blogservicesecretkey'

from enum import Enum


class Visibility(Enum):
    VISIBLE_TO_ALL = 1
    VISIBLE_TO_GROUP = 2
    VISIBLE_TO_FRIENDS = 3
    VISIBLE_TO_ME_ONLY = 4
