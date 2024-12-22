#!/usr/bin/env python3

from collections import namedtuple
import configparser
import json
import sys
import time
import urllib.request

def fatal(msg):
    print(f"FATAL: {msg}")
    sys.exit(1)

class Config:
    def __init__(self, filename):
        config = configparser.ConfigParser()
        try:
            config.read_file(open(filename))
        except:
            fatal(f"Failed to open or parse config file {filename}")

        try:
            self.apikey = config["ECOBEE"]["apikey"]
        except:
            fatal(f"ECOBEE apikey missing from config file {filename}")

def parse_json(string):
    """Parse a json string, return as python namedtuple objects"""
    try:
        return json.loads(string, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    except json.decoder.JSONDecodeError:
        return None
    
def fetch_url(url, desc=None, debug=False):
    """Fetch a URL

    On success, return the response as a string.
    On failure, call fatal with an error message.
    """
    if debug:
        print(f"Attempting to fetch URL '{url}' (desc '{desc}')")
    response = urllib.request.urlopen(url)
    if response.status != 200:
        fatal(f"Failed to open {desc or url}, code {response.status} msg {response.msg}")

    return response.read()

def fetch_url_as_json(url, **kwargs):
    return parse_json(fetch_url(url, **kwargs))

AUTH_TOKEN_FILE="ecobee_token.json"

def auth_token(config):
    """return current access token after refreshing, or None on failure"""

    try:
        token_json = open(AUTH_TOKEN_FILE, "r").read()

        token = parse_json(token_json)

        refreshed_token_json = fetch_url(
            f"https://api.ecobee.com/token?grant_type=refresh_token&refresh_token={token.refresh_token}&client_id={config.apikey}&ecobee_type=jwt",
            "ecobee refresh endpoint")

        refreshed_token = parse_json(refreshed_token_json)

        if len(refreshed_token.access_token) > 0:
            # All good - token was refreshed, and refresh succeeded
            open(AUTH_TOKEN_FILE, "w").write(refreshed_token_json.decode("utf-8"))
            return refreshed_token.access_token

    except:
        # Something failed during the refresh, so just return None
        return None
    
def main():
    config = Config("./jhf-powerfail.conf")

    if auth_token(config):
        print("Already authenticated!")
        return 0

    auth = fetch_url_as_json(
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
            token_string = fetch_url(
                f"https://api.ecobee.com/token?grant_type=ecobeePin&code={auth.code}&client_id={config.apikey}&ecobee_type=jwt",
                desc = "ecobee token endpoint")
        except urllib.error.HTTPError as err:
            token_string = ""

        try:
            token = parse_json(token_string)
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

