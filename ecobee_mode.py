#!/usr/bin/env python3

import argparse
import jhf.ecobee
import jhf.utils
import sys

def main():
    parser = argparse.ArgumentParser(
        prog = "ecobee_mode.py",
        description = "Tool to view and change ecobee thermostat modes"
        )
    parser.add_argument("mode", nargs="?",
                        help=f"Mode to set thermostat to.  Valid modes={jhf.ecobee.valid_modes}")
    args = parser.parse_args()
    
    config = jhf.utils.Config().ecobee
    if args.mode:
        code, message = jhf.ecobee.set_mode(config, args.mode)

        if code != 0:
            print(f"Failed to set mode to {args.mode}, message={message}")
            return 1

    mode = jhf.ecobee.get_mode(config)
    if mode:
        print(f"ecobee thermostat mode is now '{mode}'")
        return 0
    else:
        print(f"failed to retrieve ecobee thermostate mode")
        return 1

if __name__ == "__main__":
    sys.exit(main())
