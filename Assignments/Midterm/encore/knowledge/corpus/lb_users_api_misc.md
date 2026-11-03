<!-- source: https://listenbrainz.readthedocs.io/en/latest/users/api/misc.html -->
<!-- site: ListenBrainz documentation -->

# Miscellaneous

Various ListenBrainz API endpoints that are not documented elsewhere.

## Explore API
These API endpoints allow fetching fresh releases and cover art details for a given color.

### GET /1/user/(mb_username: user_name)/fresh_releases
Get fresh releases data for the given user.
{
    "artist_credit_name":"Santi & Tuğçe",
    "artist_mbids":[
       "4690076b-1446-43f4-8a84-cfec56dc3601"
    ],
    "caa_id":37026686379,
    "caa_release_mbid":"9432fb06-bd84-4f2e-9386-b2f14e0de54d",
    "confidence":2,
    "release_date":"2023-10-20",
    "release_group_mbid":"30ac1ded-c254-46ac-a41f-7453dada6ae7",
    "release_group_primary_type":"Album",
    "release_group_secondary_type":null,
    "release_mbid":"9432fb06-bd84-4f2e-9386-b2f14e0de54d",
    "release_name":"The Marvelous Real",
    "release_tags":null
}
Parameters:
- sort – The sort order of the results. Must be one of “release_date”, “artist_credit_name”, “release_name”, or “confidence”. Default “release_date”.
- past – Whether to show releases in the past. Default True.
- future – Whether to show releases in the future. Default True.
- days – The number of days of fresh releases to show. Default 14. Max 90.
Status Codes:
- 200 OK – fetch succeeded
- 400 Bad Request – invalid date or number of days passed.
Response Headers:
- Content-Type – application/json

### GET /1/explore/fresh-releases/
This endpoint fetches upcoming and recently released (fresh) releases and returns a list of:
{
    "artist_credit_name": "Röyksopp",
    "artist_mbids": [
      "1c70a3fc-fa3c-4be1-8b55-c3192db8a884"
    ],
    "release_date": "2022-04-29",
    "release_group_mbid": "4f1c579a-8a9c-4f96-92ae-befcdf3e0d32",
    "release_group_primary_type": "Album",
    "release_mbid": "1f1db316-8361-4a40-9633-550b259642f5",
    "release_name": "Profound Mysteries"
}
Parameters:
- release_date – Fresh releases will be shown around this pivot date. Must be in YYYY-MM-DD format
- days – The number of days of fresh releases to show. Max 90 days.
- sort – The sort order of the results. Must be one of “release_date”, “artist_credit_name” or “release_name”. Default “release_date”.
- past – Whether to show releases in the past. Default True.
- future – Whether to show releases in the future. Default True.
Status Codes:
- 200 OK – fetch succeeded
- 400 Bad Request – invalid date or number of days passed.
Response Headers:
- Content-Type – application/json

### GET /1/explore/color/(color)
Fetch a list of releases that have cover art that has a predominant color that is close to the given color.
{
    "payload": {
        "releases" : [
            {
              "artist_name": "Letherette",
              "color": [ 250, 90, 192 ],
              "dist": 109.973,
              "release_mbid": "00a109da-400c-4350-9751-6e6f25e89073",
              "caa_id": 34897349734,
              "release_name": "EP5",
              "recordings": "< array of listen formatted metadata >",
              },
            ". . ."
        ]
    }
}
Status Codes:
- 200 OK – success
Response Headers:
- Content-Type – application/json

### GET /1/explore/lb-radio
Generate a playlist with LB Radio.
Parameters:
- prompt – The LB Radio prompt from which to generate playlists.
- mode – The mode that LB radio should use. Must be easy, medium or hard.
{
    "payload": {
        "jspf" : {}, // <JSPF playlist here>
        "feedback": [] // <user feedback items>
    }
}
Status Codes:
- 200 OK – success
- 400 Bad Request – bad request: some parameters are missing or invalid
- 500 Internal Server Error – Troi encountered an error
Response Headers:
- Content-Type – application/json

## Donors API

### GET /1/donors/recent
Get a list of most recent MeB donors with flairs.

### GET /1/donors/biggest
Get a list of the biggest MeB donors with flairs.

### GET /1/donors/all-flairs
Get flairs for all eligible users.
Returns a JSON object with username as key and the flair description as value. Example:
{
    "rob": {
        "color": "orange"
    },
    "lucifer": {
        "emoji": "devil"
    }
}

## Status API

### GET /1/status/get-dump-info
Get information about ListenBrainz data dumps. You need to pass the id parameter in a GET request to get data about that particular dump.
{
    "id": 1,
    "timestamp": "20190625-165900"
}
Query Parameters:
- id – Integer specifying the ID of the dump, if not provided, the endpoint returns information about the latest data dump.
Status Codes:
- 200 OK – You have data.
- 400 Bad Request – You did not provide a valid dump ID. See error message for details.
- 404 Not Found – Dump with given ID does not exist.
Response Headers:
- Content-Type – application/json

### GET /1/status/service-status
Fetch the recently updated metrics for age of stats, dumps and the number of items in the incoming queue. This function returns JSON:
{
    "dump_age": 60309,
    "incoming_listen_count": 0,
    "stats": [
        {
            "age": 38715,
            "name": "artists_week"
        }
    ],
    "stats_age": 38715,
    "time": 1734021912
}
Status Codes:
- 200 OK – You have data.
Response Headers:
- Content-Type – application/json

### GET /1/status/playlist-status
Fetch the recently updated metrics for age of recommendation playlists. This function returns JSON:
{
    "playlists": [
        {
            "age": 55671,
            "name": "daily-jams"
        },
        {
            "age": 919392,
            "name": "weekly-jams"
        },
        {
            "age": 919184,
            "name": "weekly-exploration"
        }
    ],
    "time": 1734013745
}
Status Codes:
- 200 OK – You have data.
Response Headers:
- Content-Type – application/json
