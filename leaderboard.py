#!/usr/bin/env python
'''
This script will grab the leaderboard from Advent of Code and post it to Slack
'''
# pylint: disable=wrong-import-order
# pylint: disable=C0301,C0103,C0209

import os
import datetime
import sys
import json
import requests

LEADERBOARD_ID = os.environ.get('LEADERBOARD_ID')
SESSION_ID = os.environ.get('SESSION_ID')
SLACK_WEBHOOK = os.environ.get('SLACK_WEBHOOK')

# If the ENV Var hasn't been set, then try to load from local config.
# Simply create secrets.py with these values defined.
# See README for more detailed directions on how to fill these variables.
if not all([LEADERBOARD_ID, SESSION_ID, SLACK_WEBHOOK]):
    from secrets import LEADERBOARD_ID, SESSION_ID, SLACK_WEBHOOK

# You should not need to change this URL
LEADERBOARD_URL = "https://adventofcode.com/{}/leaderboard/private/view/{}".format(
        datetime.datetime.today().year,
        LEADERBOARD_ID)


def formatLeaderMessage(members):
    """
    Format the message to conform to Slack's API
    """
    blocks = [{
        "type": "divider"
    }]

    for idx, member in enumerate(members):
        match idx:
            case 0:
                medal = ":first_place_medal:"
            case 1:
                medal = ":second_place_medal:"
            case 2:
                medal = ":third_place_medal:"
            case _:
                medal = ":round_pushpin:"
        blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"{medal}\t*{member[0]}*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"{member[1]} pts\t{member[2]} :star:"
                    }
                ]
        })
        blocks.append({
                "type": "divider"
        })

    blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"<{LEADERBOARD_URL}|View Leaderboard Online>"
            }
    })

    return blocks


def parseMembers(members_json):
    """
    Handle member lists from AoC leaderboard
    """
    # get member name, score and stars
    members = [(m["name"],
                m["local_score"],
                m["stars"]
                ) for m in members_json.values()]

    # sort members by score, descending
    members.sort(key=lambda s: (-s[1], -s[2]))

    return members


def postMessage(message):
    """
    Post the message to to Slack's API in the proper channel
    """
    payload = json.dumps({
        "blocks": message
    })

    requests.post(
        SLACK_WEBHOOK,
        data=payload,
        timeout=60,
        headers={"Content-Type": "application/json"}
    )


def main():
    """
    Main program loop
    """
    # make sure all variables are filled
    if LEADERBOARD_ID == "" or SESSION_ID == "" or SLACK_WEBHOOK == "":
        print("Please update script variables before running script.\n\
                See README for details on how to do this.")
        sys.exit(1)

    # retrieve leaderboard
    r = requests.get(
        "{}.json".format(LEADERBOARD_URL),
        timeout=60,
        cookies={"session": SESSION_ID},
        headers={
            'User-Agent': 'charles.vignal@owkin.com'
        }
    )
    if r.status_code != requests.codes.ok:  # pylint: disable=no-member
        print("Error retrieving leaderboard")
        sys.exit(1)

    # get members from json
    members = parseMembers(r.json()["members"])

    # generate message to send to slack
    message = formatLeaderMessage(members[:10])

    # send message to slack
    postMessage(message)


if __name__ == "__main__":
    main()
