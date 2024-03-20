from ..db_handler import get_login_history_by_user_id
from datetime import datetime, timedelta


def view_login_history_handler(user_id):
    history = get_login_history_by_user_id(user_id)
    result = []
    for i in history:
        # PST (LA time)
        dt_pst_str = i[0].strftime("%Y-%m-%d %H:%M:%S")
        result.append({'datetime': dt_pst_str, 'ip_address': i[1]})
    return result
