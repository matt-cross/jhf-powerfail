#!/usr/bin/env python3

import jhf.solark
import jhf.utils
import sys

    
def main():
    config = jhf.utils.Config().inteless
    token = jhf.solark.auth_token(config)

    if not token:
        print(f"Authentication failed")
        return 1

    data = jhf.solark.current_data(config, token, ("F-grid", "V-grid-L1", "V-grid-L2"))
    print(f"{data}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
