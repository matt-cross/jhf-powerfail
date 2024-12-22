import json
import time
import urllib.error
import urllib.parse
from . import utils

auth_token_file="ecobee_token.json"

def auth_token(config):
    """return current access token after refreshing, or None on failure"""

    try:
        token_json = open(auth_token_file, "r").read()

        token = utils.parse_json(token_json)

        refreshed_token_json = utils.fetch_url(
            f"https://api.ecobee.com/token?grant_type=refresh_token&refresh_token={token.refresh_token}&client_id={config.apikey}&ecobee_type=jwt",
            "ecobee refresh endpoint")

        refreshed_token = utils.parse_json(refreshed_token_json)

        if len(refreshed_token.access_token) > 0:
            # All good - token was refreshed, and refresh succeeded
            open(auth_token_file, "w").write(refreshed_token_json.decode("utf-8"))
            return refreshed_token.access_token

    except:
        # Something failed during the refresh, so just return None
        return None
    
def authenticate(config, pin_display_callback, working_callback):
    """Authenticate with ecobee using API key in config.

    The overall protocol requires the user to log in to ecobee, go the
    'My Apps' menu, add an app (which requires providing the
    dynamically generated PIN code), and approve it.

    To accomplish this, this function will call the
    pin_display_callback with the PIN when it receives it so that it
    can be displayed to the user.  While working it will will call
    working_callback periodically.

    If the working callback returns a non-truthy value, the
    authentication will be aborted and this function will return.

    Returns True on authentication success, and False on failure."""

    if auth_token(config):
        # Already authenticated
        return True

    auth = utils.fetch_url_as_json(
        f"https://api.ecobee.com/authorize?response_type=ecobeePin&client_id={config.apikey}&scope=smartWrite",
        desc = "ecobee authentication endpoint")

    pin_display_callback(auth.ecobeePin)

    while True:
        time.sleep(auth.interval)

        try:
            token_string = utils.fetch_url(
                f"https://api.ecobee.com/token?grant_type=ecobeePin&code={auth.code}&client_id={config.apikey}&ecobee_type=jwt",
                desc = "ecobee token endpoint")
        except urllib.error.HTTPError as err:
            token_string = ""

        try:
            token = utils.parse_json(token_string)
            if len(token.refresh_token) != 0:
                f = open(auth_token_file, "w")
                f.write(token_string.decode("utf-8"))
                f.close()

                return True
        except AttributeError:
            pass

        if not working_callback():
            return False

def get_mode(config):
    token = auth_token(config)

    if not token:
        return None

    selector = {
        "selection": {
            "selectionType": "registered",
            "selectionMatch": "",
            "includeSettings": True,
        }
    }
    selector_json = json.dumps(selector)
    settings = utils.fetch_url_as_json(
        f"https://api.ecobee.com/1/thermostat?json={urllib.parse.quote(selector_json)}",
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": f"Bearer {token}",
        },
    )

    return settings.thermostatList[0].settings.hvacMode

def set_mode(config, mode):
    token = auth_token(config)

    if not token:
        return None

    selector = {
        "selection": {
            "selectionType": "registered",
            "selectionMatch": "",
        },
        "thermostat": {
            "settings": {
                "hvacMode": mode,
            }
        }
    }
    selector_json = json.dumps(selector)
    response = utils.fetch_url_as_json(
        f"https://api.ecobee.com/1/thermostat?json",
        method = "POST",
        data = selector_json.encode(),
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": f"Bearer {token}",
        },
    )

    return (response.status.code, response.status.message)
