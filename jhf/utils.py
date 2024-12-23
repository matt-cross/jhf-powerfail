import urllib.request
import json
import sys
from collections import namedtuple
import configparser

def fatal(msg):
    print(f"FATAL: {msg}")
    sys.exit(1)


config_filename = "jhf-powerfail.conf"

EcobeeConfig = namedtuple("EcobeeConfig", ["apikey"])
IntelessConfig = namedtuple("Inteless", ["username", "password", "sn"])

class Config:
    def __init__(self, filename = config_filename):
        config = configparser.ConfigParser()
        try:
            config.read_file(open(filename))
        except:
            fatal(f"Failed to open or parse config file {filename}")

        try:
            self.ecobee = EcobeeConfig(apikey = config["ECOBEE"]["apikey"])
            self.inteless = IntelessConfig(
                username = config["INTELESS"]["username"], 
                password = config["INTELESS"]["password"],
                sn = config["INTELESS"]["sn"])
        except:
            fatal(f"Items missing from config file {filename}")

def parse_json(string):
    """Parse a json string, return as python namedtuple objects"""
    try:
        return json.loads(string, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    except (json.decoder.JSONDecodeError, TypeError):
        return None
    
def fetch_url(url, desc=None, headers=None, method=None, data=None, debug=False):
    """Fetch a URL

    On success, return the response as a string.
    On failure, return None
    """
    if debug:
        print(f"Attempting to fetch URL '{url}' (desc '{desc}') with headers '{headers}'")
    request = urllib.request.Request(url = url, headers = headers or {}, method=method, data=data)
    try:
        response = urllib.request.urlopen(request)
        if response.status != 200:
            if debug:
                print(f"Failed to open {desc or url}, code {response.status} msg {response.msg}")
            return None
    except urllib.error.HTTPError as http_error:
        if debug:
            print(f"Failed to open {desc or url}, code {http_error.code} msg {http_error.reason}")
        return None

    return response.read()

def fetch_url_as_json(url, **kwargs):
    return parse_json(fetch_url(url, **kwargs))
