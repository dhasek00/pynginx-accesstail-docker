"""
Program Name: tail.py
Author: Ryan Clark
Purpose: On a given access.log file, start at the file end
         and send entries to a parser every 5 seconds.
         The parser will extract status codes and write
         them to a statsd compatible file displaying the
         number of instances which occurred for each range.
"""

import sys
import time
import re
import os
from collections import Counter

# Define some regular expressions to extract the route and status code
RE_ROUTE = "^.+ (/.*) HTTP/.+$"
RE_STATUS = "^ ([0-9]{3}) [0-9]+ $"

def parse_log(lines, statsFile):
    """
    Accepts a list of lines and stats log file as arguments.

    This function will parse a log entry and extract the HTTP status codes.
    It will then count and assign them to their appropriate range.
    Finally it will both print and write the new results to a file at
    /var/log/stats.log

    Looks like the best way to separate the line is using quotes
    0th entry = Everything up to the HTTP Request Method. Not needed.
    1st entry = HTTP Request and Route Requested
    2nd entry = Status code and bytes sent
    """

    # Create a dictionary to hold status values and routes for 500x
    match_dict = { "200s": 0, "300s": 0, "400s": 0,
                   "500s": {"status": 0, "routes": []} }

    for line in lines:
        try:
            # Split line using \ delimiter
            line_split = line.rstrip().split("\"")
            # Extract the status code and routes requested
            route_match = re.match(RE_ROUTE, line_split[1])
            status_match = re.match(RE_STATUS, line_split[2])

            # If matches were found, save them
            if route_match:
                route = route_match.group(1)
            if status_match:
                status = int(status_match.group(1))

            # Categorize the status codes and add to the dictionary
            if status > 199 and status < 300:
                match_dict["200s"] += 1
            elif status > 299 and status < 400:
                match_dict["300s"] += 1
            elif status > 399 and status < 500:
                match_dict["400s"] += 1
            elif status > 499 and status < 600:
                match_dict["500s"]["status"] += 1
                match_dict["500s"]["routes"].append(route)
        except Exception:
            print("Exception caught")
            continue

    # Use the Counter class to group and count the instances of routes
    match_dict["500s"]["count"] = Counter(match_dict["500s"]["routes"])


    # Print the status codes to StdOut
    print("50x:{0}|s\n40x:{1}|s\n30x:{2}|s\n20x:{3}|s").format(match_dict["500s"]["status"],
                                                               match_dict["400s"],
                                                               match_dict["300s"],
                                                               match_dict["200s"])

    # Same as print but save to file
    statsFile.write("50x:{0}|s\n40x:{1}|s\n30x:{2}|s\n20x:{3}|s\n".format(match_dict["500s"]["status"],
                                                               match_dict["400s"],
                                                               match_dict["300s"],
                                                               match_dict["200s"]))
    statsFile.flush()


    for count in match_dict["500s"]["count"].items():
        # Print the routes requested for 500x to StdOut
        print("{0}:{1}|s".format(count[0], count[1]))
        # Same as print but save to file
        statsFile.write("{0}:{1}|s\n".format(count[0], count[1]))
        statsFile.flush()

def main():
    # Run the code in a try block to catch errors or Ctrl-C
    try:

        if len(sys.argv) == 2:
            # Get Filename from python argument
            filename = sys.argv[1].strip()
        elif len(sys.argv) == 1:
            # Ask the user for a filename
            filename = raw_input('Enter filename: ').strip()
        else:
            print("Usage: python tail.py [accesslogfile]")
            sys.exit(1)

        # If file doesn't exist - wait 10 seconds for it to be
        # created. In case service is still starting.
        if os.path.isfile(filename) is False:
            print("File doesn't exist. Waiting 10 for it to be created.")
            for x in range(0,10):
                if os.path.isfile(filename) is False:
                    time.sleep(1)
                else:
                    print("Opening File")
                    break

        # Open the file with read-only privileges in bytes mode
        with open("/var/log/stats.log", "ab") as statsFile:
            with open(filename, 'rb') as logFile:

                # Use seek to get to the end of the file
                logFile.seek(0,2)

                # Run indefinitely
                # Get all new entries and send them to be parsed
                # Sleep for 5 seconds before repeating
                while True:
                    lines = logFile.readlines()
                    parse_log(lines, statsFile)
                    time.sleep(5)

    # If the user Interrupts the program, catch it and
    # print exit. Then exit with code 0.
    except KeyboardInterrupt as e:
        print("\nExited")
        sys.exit(0)

    # Catch-all for exceptions that may occur
    except Exception as e:
        print("Error Occurred: {}".format(str(e)))
        sys.exit(1)


if __name__ == '__main__':
    main()
