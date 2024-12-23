#!/usr/bin/env python3

import argparse
import datetime
import jhf.solark
import jhf.utils
import sys

    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("start_date", help="Start date to accumulate in ISO format (IE YYYY-MM-DD)")
    parser.add_argument("end_date", nargs="?", help="End date to accumulate.  Default = today")
    args = parser.parse_args()

    try:
        start_date = datetime.date.fromisoformat(args.start_date)
    except ValueError:
        print(f"Start date {args.start_date} is not in valid format, must be YYYY-MM-DD")
        return 1

    if args.end_date:
        try:
            end_date = datetime.date.fromisoformat(args.end_date)
        except ValueError:
            print(f"End date {args.end_date} is not in valid format, must be YYYY-MM-DD")
            return 1
    else:
        end_date = datetime.date.today()

    # Connect and retrieve the data
    config = jhf.utils.Config().inteless
    token = jhf.solark.auth_token(config)

    if not token:
        print(f"Authentication failed")
        return 1

    plant_id = jhf.solark.plant_id(config, token)

    data = jhf.solark.energy_data_by_day(config, token, plant_id)

    # Summarize
    results = None

    cur_date = start_date
    while cur_date <= end_date:
        try:
            day_results = data[cur_date.isoformat()]
        except KeyError:
            print(f"WARNING: Data for date {cur_date.isoformat()} not found in data from inverter")

        if results:
            for key,value in day_results.items():
                results[key] += value
        else:
            results = day_results

        cur_date += datetime.timedelta(days=1)

    print(f"Sum: {results}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
