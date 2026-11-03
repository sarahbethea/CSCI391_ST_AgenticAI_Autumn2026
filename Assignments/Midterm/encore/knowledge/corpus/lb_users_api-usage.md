<!-- source: https://listenbrainz.readthedocs.io/en/latest/users/api-usage.html -->
<!-- site: ListenBrainz documentation -->

# Usage Examples

Note
These examples are written in Python version 3.6.3 and use requests version 2.18.4.

## Prerequisites
All the examples assume you have a development version of the ListenBrainz server set up on localhost. Remember to set DEBUG to True in the config. When in production, you can replace localhost with api.listenbrainz.org to use the real API. In order to use either one, you’ll need a token. You can find it under ROOT/settings/ when signed in, with ROOT being either localhost for the dev version or listenbrainz.org for the real API.
Caution
You should use the token from the API you’re using. In production, change the token to one from listenbrainz.org.

## Examples

### Submitting Listens
See JSON Documentation for details on the format of the Track dictionaries.
If everything goes well, the json response should be {"status": "ok"}, and you should see a recent listen of “Never Gonna Give You Up” when you visit ROOT/user/{your-user-name}.
from time import time
import requests

# Set DEBUG to True to test local dev server.
# API keys for local dev server and the real server are different.
DEBUG = True
ROOT = 'http://localhost:8103' if DEBUG else 'https://api.listenbrainz.org'

def submit_listen(listen_type, payload, token):
    """Submits listens for the track(s) in payload.

    Args:
        listen_type (str): either of 'single', 'import' or 'playing_now'
        payload: A list of Track dictionaries.
        token: the auth token of the user you're submitting listens for

    Returns:
         The json response if there's an OK status.

    Raises:
         An HTTPError if there's a failure.
         A ValueError is the JSON in the response is invalid.
    """

    response = requests.post(
        url="{0}/1/submit-listens".format(ROOT),
        json={
            "listen_type": listen_type,
            "payload": payload,
        },
        headers={
            "Authorization": "Token {0}".format(token)
        }
    )

    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    EXAMPLE_PAYLOAD = [
        {
            # An example track.
            "listened_at": int(time()),
            "track_metadata": {
                "artist_name": "Rick Astley",
                "track_name": "Never Gonna Give You Up",
                "release_name": "Whenever you need somebody"
            }
        }
    ]

    # Input token from the user and call submit listen
    token = input('Please enter your auth token: ')
    json_response = submit_listen(listen_type='single', payload=EXAMPLE_PAYLOAD, token=token)

    print("Response was: {0}".format(json_response))
    print("Check your listens - there should be a Never Gonna Give You Up track, played recently.")

### Getting Listen History
For a user’s entire listening history, use the export API. It provides an asynchronous ZIP download for bulk imports, including those made by third-party applications and MCP servers. Do not retrieve a complete history by repeatedly paginating or scraping the listens API. The example below is for fetching a limited set of listens.
See JSON Documentation for details on the format of the Track dictionaries.
If there’s nothing in the listen history of your user, you can run submit_listens before this.
If there is some listen history, you should see a list of tracks like this:
import requests

# Set DEBUG to True to test local dev server.
# API keys for local dev server and the real server are different.
DEBUG = True
ROOT = 'http://localhost:8103' if DEBUG else 'https://api.listenbrainz.org'

# The following token must be valid, but it doesn't have to be the token of the user you're
# trying to get the listen history of.
TOKEN = 'YOUR_TOKEN_HERE'
AUTH_HEADER = {
    "Authorization": "Token {0}".format(TOKEN)
}


def get_listens(username, min_ts=None, max_ts=None, count=None):
    """Gets the listen history of a given user.

    Args:
        username: User to get listen history of.
        min_ts: History before this timestamp will not be returned.
                DO NOT USE WITH max_ts.
        max_ts: History after this timestamp will not be returned.
                DO NOT USE WITH min_ts.
        count: How many listens to return. If not specified,
               uses a default from the server.

    Returns:
        A list of listen info dictionaries if there's an OK status.

    Raises:
        An HTTPError if there's a failure.
        A ValueError if the JSON in the response is invalid.
        An IndexError if the JSON is not structured as expected.
    """
    response = requests.get(
        url="{0}/1/user/{1}/listens".format(ROOT, username),
        params={
            "min_ts": min_ts,
            "max_ts": max_ts,
            "count": count,
        },
        # Note that an authorization header isn't compulsary for requests to get listens
        # BUT requests with authorization headers are given relaxed rate limits by ListenBrainz
        headers=AUTH_HEADER,
    )

    response.raise_for_status()

    return response.json()['payload']['listens']

if __name__ == "__main__":
    username = input('Please input the MusicBrainz ID of the user: ')
    listens = get_listens(username)

    for track in listens:
        print("Track: {0}, listened at {1}".format(track["track_metadata"]["track_name"],
                                                   track["listened_at"]))
Track: Never Gonna Give You Up, listened at 1512040365
Track: Never Gonna Give You Up, listened at 1511977429
Track: Never Gonna Give You Up, listened at 1511968583
Track: Never Gonna Give You Up, listened at 1443521965
Track: Never Gonna Give You Up, listened at 42042042

### Lookup MBIDs
To interact with various ListenBrainz features, you will often need a MBID of the recording of a listen. You can use the Metadata endpoints to lookup MBID and additional metadata for the listen using its track name and artist name. For instance,
#!/usr/bin/env python3

import json
import requests

# Set DEBUG to True to test local dev server.
DEBUG = False
ROOT = 'http://localhost:8103' if DEBUG else 'https://api.listenbrainz.org'

def lookup_metadata(track_name: str, artist_name: str, incs: str) -> dict:
    """Looks up the metadata for a listen using track name and artist name."""
    params = {
        "recording_name": track_name,
        "artist_name": artist_name
    }
    if incs:
        params["metadata"] = True
        params["incs"] = incs
    response = requests.get(
        url="{0}/1/metadata/lookup/".format(ROOT),
        params=params
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    track_name = input('Please input the track name of the listen: ').strip()
    artist_name = input('Please input the artist name of the listen: ').strip()
    incs = input('Please input extra metadata to include (leave empty if not desired): ').strip()

    metadata = lookup_metadata(track_name, artist_name, incs)

    print()
    if metadata:
        print("Metadata found.")
        print(json.dumps(metadata, indent=4))
    else:
        print("No metadata found.")
Please provide the prompted data to the script to lookup the given track. Currently the release argument for a listen is not used, but we plan to support in the near future, so we encourage you to start sending release information if you have it.
{
    "artist_credit_name": "Ariana Grande",
    "artist_mbids": [
        "f4fdbb4c-e4b7-47a0-b83b-d91bbfcfa387"
    ],
    "metadata": {
        "recording": {
            "rels": [
                {
                    "artist_mbid": "eb811bf7-4c99-4781-84c0-10ba6b8e33b3",
                    "artist_name": "Carl Falk",
                    "instrument": "guitar",
                    "type": "instrument"
                },
                {
                    "artist_mbid": "c8af4490-e48a-4f91-aef9-2b1e39369576",
                    "artist_name": "Savan Kotecha",
                    "instrument": "background vocals",
                    "type": "vocal"
                },
                {
                    "artist_mbid": "0d33cc88-28ae-44d5-be7e-7a653e518720",
                    "artist_name": "Jeanette Olsson",
                    "instrument": "background vocals",
                    "type": "vocal"
                }
            ]
        }
    },
    "recording_mbid": "9f24c0f7-a644-4074-8fbd-a1dba03de129",
    "recording_name": "One Last Time",
    "release_mbid": "be5d97b1-408a-4e95-b924-0a61955048de",
    "release_name": "My Everything"
}

### Love/hate feedback
To provide love/hate feedback on listens, you need a recording MBID or a recording MSID. If you submit a playing_now listen, you can set the parameter return_msid to :true: to get the recording_msid in the response body. See the submit-listens example for more details. If you have neither, you can look up the MBID using the metadata endpoints. See Lookup MBIDs for an example of the same. Here is an example of how to submit love/hate feedback using the ListenBrainz API. Refer to Feedback API for more details.
#!/usr/bin/env python3

import requests

# Set DEBUG to True to test local dev server.
# API keys for local dev server and the real server are different.
DEBUG = True
ROOT = 'http://localhost:8103' if DEBUG else 'https://api.listenbrainz.org'

def submit_feedback(token: str, recording_mbid: str, score: int):
    """ Submit feedback for recording. """
    response = requests.post(
        url="{0}/1/feedback/recording-feedback".format(ROOT),
        json={"recording_mbid": recording_mbid, "score": score},
        headers={"Authorization": f"Token {token}"}
    )
    response.raise_for_status()
    print("Feedback submitted.")


if __name__ == "__main__":
    recording_mbid = input('Please input the recording mbid of the listen: ').strip()
    score = int(input('Please input the feedback score (1, 0 or -1): ').strip())
    token = input('Please enter your auth token: ').strip()

    submit_feedback(token, recording_mbid, score)
Please provide the prompted data to the script to submit feedback.

### Latest Import
Set and get the timestamp of the latest import into ListenBrainz.

#### Setting
from time import time
import requests

# Set DEBUG to True to test local dev server.
# API keys for local dev server and the real server are different.
DEBUG = True
ROOT = 'http://localhost:8103' if DEBUG else 'https://api.listenbrainz.org'


def set_latest_import(timestamp, token, service="librefm"):
    """Sets the time of the latest import.

    Args:
        timestamp: Unix epoch to set latest import to.
        token: the auth token of the user you're setting latest_import of
        service: service to set latest import time of.

    Returns:
        The JSON response if there's an OK status.

    Raises:
        An HTTPError if there's a failure.
        A ValueError if the JSON response is invalid.
    """
    response = requests.post(
        url="{0}/1/latest-import".format(ROOT),
        json={
            "ts": timestamp,
            "service": service
        },
        headers={
            "Authorization": "Token {0}".format(token),
        }
    )

    response.raise_for_status()

    return response.json()

if __name__ == "__main__":
    ts = int(time())
    token = input('Please enter your auth token: ')
    json_response = set_latest_import(ts, token)

    print("Response was: {0}".format(json_response))
    print("Set latest import time to {0}.".format(ts))

#### Getting
If your user has never imported before and the latest import has never been set by a script, then the server will return 0 by default. Run set_latest_import before this if you don’t want to actually import any data.
import requests

# Set DEBUG to True to test local dev server.
# API keys for local dev server and the real server are different.
DEBUG = True
ROOT = 'http://localhost:8103' if DEBUG else 'https://api.listenbrainz.org'

# The token can be any valid token.
TOKEN = 'YOUR_TOKEN_HERE'
AUTH_HEADER = {
    "Authorization": "Token {0}".format(TOKEN)
}

def get_latest_import(username, service="lastfm"):
    """Gets the latest import timestamp of a given user.

    Args:
        username: User to get latest import time of.
        service: service to get latest import time of.

    Returns:
        A Unix timestamp if there's an OK status.

    Raises:
        An HTTPError if there's a failure.
        A ValueError if the JSON in the response is invalid.
        An IndexError if the JSON is not structured as expected.
    """
    response = requests.get(
        url="{0}/1/latest-import".format(ROOT),
        params={
            "user_name": username,
            "service": service
        },
        headers=AUTH_HEADER,
    )

    response.raise_for_status()
    return response.json()["latest_import"]


if __name__ == "__main__":
    username = input('Please input the MusicBrainz ID of the user: ')
    timestamp = get_latest_import(username)

    print("User {0} last imported on {1}".format(username, timestamp))
You should see output like this:
User naiveaiguy last imported on 30 11 2017 at 12:23
