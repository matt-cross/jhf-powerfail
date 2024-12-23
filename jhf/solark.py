import datetime
import json
from . import utils

def auth_token(config):
    request_data = {
        "username": config.username,
        "password": config.password,
        "grant_type": "password",
        "client_id": "csp-web",
        "source": "elinter",
    }
    request_data_json = json.dumps(request_data)
    result = utils.fetch_url_as_json(
        "https://www.solarkcloud.com/oauth/token",
        method = "POST",
        headers = {
            "Content-Type": "application/json;charset=UTF-8"
        },
        data = request_data_json.encode()
    )

    if not result:
        return None

    if result.code != 0:
        print(f"Authentication failure: {result.msg}")
        return None

    return result.data.access_token

def plant_id(config, auth):
    result = utils.fetch_url_as_json(
        f"https://www.solarkcloud.com/api/v1/plants?page=1&limit=10&name=&status=&type=-1&sortCol=createAt&order=2",
        headers = { "Authorization": f"Bearer {auth}" })

    return result.data.infos[0].id 

def inverter_params(config, auth):
    """Returns a dict that maps param name to ID, or an empty dict on failure"""
    raw = utils.fetch_url_as_json(
        f"https://www.solarkcloud.com/api/v1/inverter/params?lan=en&devType=2&sn={config.sn}",
        headers = { "Authorization": f"Bearer {auth}" })

    if not raw:
        return None

    result = {}
    for info in raw.data.infos:
        for item in info.groupContent:
            result[item.label] = item.id

    return result

def current_data(config, auth, param_names):
    param_mapping = inverter_params(config, auth)
    param_ids = []
    for name in param_names:
        if name in param_mapping:
            param_ids.append(str(param_mapping[name]))
        else:
            print(f"No ID found for param name {name}")
            return None

    today = datetime.date.today().isoformat()

    result = utils.fetch_url_as_json(
        f"https://www.solarkcloud.com/api/v1/inverter/{config.sn}/day?sn={config.sn}&date={today}&edate={today}&lan=en&params={','.join(param_ids)}",
        headers = { "Authorization": f"Bearer {auth}" })

    cur_values = {}
    for item in result.data.infos:
        value = float(item.records[-1].value)
        label = item.label
        cur_values[label] = value

    return cur_values

def energy_data_by_day(config, auth, plant_id):
    # This will fetch all data by day.  The trick is that the "date=2"
    # argument will fetch all data where the date in YYYY-MM-DD format
    # starts with "2" - which will be all data from Jan 1, 2000 to Dec
    # 31, 2999.
    result = utils.fetch_url_as_json(
        f"https://www.solarkcloud.com/api/v1/plant/energy/{plant_id}/month?lan=en&date=2&id={plant_id}",
        headers = { "Authorization": f"Bearer {auth}" })

    # The result puts data in ".data.infos", which is a list of "info"
    # items.  Each info item has "unit", "label", and a list of
    # records which each contain "time" (which is an ISO format date)
    # and "value" fields.
    #
    # We want to convert it into a dict whose primary key is date, and
    # that contains for each day a dict whose keys are labels (such as
    # "Load", "PV, "Export", and "Import") and whose values are the
    # corresponding value for that day.

    by_day = {}
    for item in result.data.infos:
        label = item.label
        for record in item.records:
            date = record.time
            value = float(record.value)
            if date in by_day:
                by_day[date][label] = value
            else:
                by_day[date] = {label: value}

    return by_day
