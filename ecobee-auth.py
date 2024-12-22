#!/usr/bin/env python3

from collections import namedtuple
import jhf.utils
import sys
import time
import urllib.error

AUTH_TOKEN_FILE="ecobee_token.json"

def auth_token(config):
    """return current access token after refreshing, or None on failure"""

    try:
        token_json = open(AUTH_TOKEN_FILE, "r").read()

        token = jhf.utils.parse_json(token_json)

        refreshed_token_json = jhf.utils.fetch_url(
            f"https://api.ecobee.com/token?grant_type=refresh_token&refresh_token={token.refresh_token}&client_id={config.apikey}&ecobee_type=jwt",
            "ecobee refresh endpoint")

        refreshed_token = jhf.utils.parse_json(refreshed_token_json)

        if len(refreshed_token.access_token) > 0:
            # All good - token was refreshed, and refresh succeeded
            open(AUTH_TOKEN_FILE, "w").write(refreshed_token_json.decode("utf-8"))
            return refreshed_token.access_token

    except:
        # Something failed during the refresh, so just return None
        return None
    
def main():
    config = jhf.utils.Config().ecobee

    if auth_token(config):
        print("Already authenticated!")
        return 0

    auth = jhf.utils.fetch_url_as_json(
        f"https://api.ecobee.com/authorize?response_type=ecobeePin&client_id={config.apikey}&scope=smartWrite",
        desc = "ecobee authentication endpoint")

    print(f"reply {auth}")

    print(f"""To authenticate this app with Ecobee, log into your Ecobee
account at www.ecobee.com, in the pull-down menu from the upper right
click on 'My Apps', click 'Add Application', and enter this PIN code:

{auth.ecobeePin}""")


    while True:
        time.sleep(auth.interval)

        try:
            token_string = jhf.utils.fetch_url(
                f"https://api.ecobee.com/token?grant_type=ecobeePin&code={auth.code}&client_id={config.apikey}&ecobee_type=jwt",
                desc = "ecobee token endpoint")
        except urllib.error.HTTPError as err:
            token_string = ""

        try:
            token = jhf.utils.parse_json(token_string)
            if len(token.refresh_token) != 0:
                f = open(AUTH_TOKEN_FILE, "w")
                f.write(token_string.decode("utf-8"))
                f.close()

                print(f"Authenticated!  Token written to {AUTH_TOKEN_FILE}")
                return 0
        except AttributeError:
            pass

        print(".", end="", flush=True)

if __name__ == "__main__":
    sys.exit(main())

