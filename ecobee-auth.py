#!/usr/bin/env python3

from collections import namedtuple
import jhf.ecobee
import jhf.utils
import sys

def main():
    config = jhf.utils.Config().ecobee

    def display_pin(pin):
        print(
            f"""To authenticate this app with Ecobee, log into your Ecobee
account at www.ecobee.com, in the pull-down menu from the upper right
click on 'My Apps', click 'Add Application', and enter this PIN code:

{pin}""")

    def working():
        print(".", end="", flush=True)
        return True

    if jhf.ecobee.authenticate(config, display_pin, working):
        print("Authenticated successfully!")
        return 0
    else:
        print("Failed authentication")
        return 1

if __name__ == "__main__":
    sys.exit(main())

