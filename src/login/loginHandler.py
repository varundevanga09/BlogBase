import secrets
import base64
from ..db_handler import create_user, get_user_from_name, create_login_history


#####
# login
#####
def login_handler(username, password):
    # get record
    result = get_user_from_name(username)

    # Not exist
    if result is None:
        raise InvalidLoginInformationException

    id, salt, encoded_password = result

    # check password
    combined = (salt + password).encode('utf-8')
    encoded_input_password = base64.b64encode(combined).decode('utf-8')

    # wrong password
    if encoded_password != encoded_input_password:
        raise InvalidLoginInformationException

    return id


def add_login_history(user_id, ip_address):
    create_login_history(user_id, ip_address)


#####
# create account
#####
def create_account_handler(username, password):
    salt = secrets.token_hex(4)
    combined = (salt + password).encode('utf-8')
    encoded_password = base64.b64encode(combined).decode('utf-8')

    new_user_id = create_user(username, encoded_password, salt)
    print(f"Created new user with ID: {new_user_id}")

    return new_user_id


class InvalidLoginInformationException(Exception):
    pass
