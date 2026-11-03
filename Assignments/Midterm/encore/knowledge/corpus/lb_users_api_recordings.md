<!-- source: https://listenbrainz.readthedocs.io/en/latest/users/api/recordings.html -->
<!-- site: ListenBrainz documentation -->

# Recordings


## Feedback API
These API endpoints allow to submit and retrieve feedback for a user’s recordings

### POST /1/feedback/recording-feedback
Submit recording feedback (love/hate) to the server. A user token (found on https://listenbrainz.org/settings/ ) must be provided in the Authorization header! Each request should contain only one feedback in the payload.
For complete details on the format of the JSON to be POSTed to this endpoint, see Feedback JSON Documentation.
Request Headers:
- Authorization – Token <user token>
Status Codes:
- 200 OK – feedback accepted.
- 400 Bad Request – invalid JSON sent, see error message for details.
- 401 Unauthorized – invalid authorization. See error message for details.
Response Headers:
- Content-Type – application/json

### GET /1/feedback/user/(mb_username: user_name)/get-feedback
Get feedback given by user user_name. The format for the JSON returned is defined in our Feedback JSON Documentation.
If the optional argument score is not given, this endpoint will return all the feedback submitted by the user. Otherwise filters the feedback to be returned by score.
Parameters:
- score (int) – Optional, If 1 then returns the loved recordings, if -1 returns hated recordings.
- count (int) – Optional, number of feedback items to return, Default: DEFAULT_ITEMS_PER_GET Max: MAX_ITEMS_PER_GET.
- offset (int) – Optional, number of feedback items to skip from the beginning, for pagination. Ex. An offset of 5 means the top 5 feedback will be skipped, defaults to 0.
- metadata (str) – Optional, ‘true’ or ‘false’ if this call should return the metadata for the feedback.
Status Codes:
- 200 OK – Yay, you have data!
Response Headers:
- Content-Type – application/json

### GET /1/feedback/recording/(recording_mbid)/get-feedback-mbid
Get feedback for recording with given recording_mbid. The format for the JSON returned is defined in our Feedback JSON Documentation.
Parameters:
- score (int) – Optional, If 1 then returns the loved recordings, if -1 returns hated recordings.
- count (int) – Optional, number of feedback items to return, Default: DEFAULT_ITEMS_PER_GET Max: MAX_ITEMS_PER_GET.
- offset (int) – Optional, number of feedback items to skip from the beginning, for pagination. Ex. An offset of 5 means the top 5 feedback will be skipped, defaults to 0.
Status Codes:
- 200 OK – Yay, you have data!
Response Headers:
- Content-Type – application/json

### GET /1/feedback/recording/(recording_msid)/get-feedback
Get feedback for recording with given recording_msid. The format for the JSON returned is defined in our Feedback JSON Documentation.
Parameters:
- score (int) – Optional, If 1 then returns the loved recordings, if -1 returns hated recordings.
- count (int) – Optional, number of feedback items to return, Default: DEFAULT_ITEMS_PER_GET Max: MAX_ITEMS_PER_GET.
- offset (int) – Optional, number of feedback items to skip from the beginning, for pagination. Ex. An offset of 5 means the top 5 feedback will be skipped, defaults to 0.
Status Codes:
- 200 OK – Yay, you have data!
Response Headers:
- Content-Type – application/json

### POST /1/feedback/user/(mb_username: user_name)/get-feedback-for-recordings
Get feedback given by user user_name for the list of recordings supplied. The format for the JSON returned is defined in our Feedback JSON Documentation.
If the feedback for given recording MSID doesn’t exist then a score 0 is returned for that recording.
The format of the post data should look as follows:
{
    "recording_msids": ["<msid1>", "<msid2>", "<msid3>"],
    "recording_mbids": ["<mbid1>", "<mbid2>", "<mbid3>"]
}
Status Codes:
- 200 OK – Yay, you have data!
Response Headers:
- Content-Type – application/json

### GET /1/feedback/user/(mb_username: user_name)/get-feedback-for-recordings
Get feedback given by user user_name for the list of recordings supplied. The format for the JSON returned is defined in our Feedback JSON Documentation.
If the feedback for given recording MSID doesn’t exist then a score 0 is returned for that recording.
Note
If you get a 502 error while querying this endpoint using a GET request, consider reducing the number of total recordings you are querying in 1 request. As a rule of thumb, requesting maximum ~75 recordings in 1 request will avert the error.
The reason this error occurs is because the recording uuids are query params which are part of the request url. The length of the url is subject to a general limit imposed at the middleware level so requests with long urls never reach the ListenBrainz backend. Due to the same reason, the backend cannot provide a meaningful error.
Parameters:
- recordings (str) – comma separated list of recording_msids for which feedback records are to be fetched. this param is deprecated and will be removed in the future. use recording_msids instead.
- recording_msids (str) – comma separated list of recording_msids for which feedback records are to be fetched.
- recording_mbids (str) – comma separated list of recording_mbids for which feedback records are to be fetched.
Status Codes:
- 200 OK – Yay, you have data!
Response Headers:
- Content-Type – application/json

### POST /1/feedback/import
Import feedback from external service.

## Pinned Recording API
These API endpoints allow submitting, deleting, and retrieving ListenBrainz pinned recordings for users.

### POST /1/pin
Pin a recording for user. A user token (found on https://listenbrainz.org/settings/) must be provided in the Authorization header! Each request should contain only one pinned recording item in the payload.
Note: Pinning a new recording will automatically unpin (deactivate) any currently active pin. Pins are active for a default duration (DAYS_UNTIL_UNPIN days) unless pinned_until is specified.
The format of the JSON to be POSTed to this endpoint should look like the following:
{
    "recording_msid": "40ef0ae1-5626-43eb-838f-1b34187519bf",
    "recording_mbid": "<this field is optional>",
    "blurb_content": "Wow..",
    "pinned_until": 1824001816
}
Request Headers:
- Authorization – Token <user token>
Status Codes:
- 200 OK – feedback accepted.
- 400 Bad Request – invalid JSON sent, see error message for details.
- 401 Unauthorized – invalid authorization. See error message for details.
Response Headers:
- Content-Type – application/json

### POST /1/pin/unpin
Unpins the currently active pinned recording for the user. A user token (found on https://listenbrainz.org/settings/) must be provided in the Authorization header!
Note: This action only deactivates the current pin. It does NOT delete the pin from the user’s history. The pin will still appear in GET /<user_name>/pins. To fully remove a pin, use POST /pin/delete/<row_id>.
Request Headers:
- Authorization – Token <user token>
Status Codes:
- 200 OK – recording unpinned.
- 401 Unauthorized – invalid authorization. See error message for details.
- 404 Not Found – could not find the active recording to unpin for the user. See error message for details.
Response Headers:
- Content-Type – application/json

### POST /1/pin/delete/(row_id)
Deletes the pinned recording with given row_id from the server. A user token (found on https://listenbrainz.org/settings/) must be provided in the Authorization header!
Note: Unlike unpinning, this action permanently removes the pin from the user’s history.
Request Headers:
- Authorization – Token <user token>
Parameters:
- row_id (int) – the row_id of the pinned recording that should be deleted.
Status Codes:
- 200 OK – recording unpinned.
- 401 Unauthorized – invalid authorization. See error message for details.
- 404 Not Found – the requested row_id for the user was not found.
Response Headers:
- Content-Type – application/json

### GET /1/pin/(int: row_id)
Get a pinned recording by its row_id. Returns the pin with track metadata. The JSON returned by the API will look like the following:
{
    "pinned_recording": {
        "blurb_content": "Awesome recording!",
        "created": 1623997168,
        "row_id": 10,
        "pinned_until": 1623997485,
        "recording_mbid": "af60273b-3c3f-4b07-8e91-1f9f4aa9d627",
        "recording_msid": "fd7d9162-a284-4a10-906c-faae4f1e166b",
        "track_metadata": {
            "artist_name": "Rick Astley",
            "track_name": "Never Gonna Give You Up"
        },
        "user_name": "-- the MusicBrainz ID of the user who pinned this recording --"
    }
}
Parameters:
- row_id (int) – the row_id of the pinned recording.
Status Codes:
- 200 OK – Yay, you have data!
- 404 Not Found – The requested pin was not found.
Response Headers:
- Content-Type – application/json

### GET /1/(mb_username: user_name)/pins
Get a list of all recordings ever pinned by a user with given user_name in descending order of the time they were originally pinned.
Note: This includes both currently active pins and past (deactivated/unpinned) pins.
The JSON returned by the API will look like the following:
{
    "count": 10,
    "offset": 0,
    "pinned_recordings": [
        {
            "blurb_content": "Awesome recording!",
            "created": 1623997168,
            "row_id": 10,
            "pinned_until": 1623997485,
            "recording_mbid": null,
            "recording_msid": "fd7d9162-a284-4a10-906c-faae4f1e166b"
            "track_metadata": {
                "artist_name": "Rick Astley",
                "track_name": "Never Gonna Give You Up"
            }
        },
        "-- more pinned recording items here ---"
    ],
    "total_count": 10,
    "user_name": "-- the MusicBrainz ID of the user --"
}
Parameters:
- user_name (str) – the MusicBrainz ID of the user whose pin track history requested.
- count (int) – Optional, number of pinned recording items to return, Default: DEFAULT_ITEMS_PER_GET Max: MAX_ITEMS_PER_GET
- offset (int) – Optional, number of pinned recording items to skip from the beginning, for pagination. Ex. An offset of 5 means the most recent 5 pinned recordings from the user will be skipped, defaults to 0
Status Codes:
- 200 OK – Yay, you have data!
- 400 Bad Request – Invalid query parameters. See error message for details.
- 404 Not Found – The requested user was not found.
Response Headers:
- Content-Type – application/json

### GET /1/(mb_username: user_name)/pins/following
Get a list containing the active pinned recordings for all users in a user’s user_name following list. The returned pinned recordings are sorted in descending order of the time they were pinned. The JSON returned by the API will look like the following:
{
    "count": 1,
    "offset": 0,
    "pinned_recordings": [
        {
        "blurb_content": "Spectacular recording!",
        "created": 1624000841,
        "row_id": 1,
        "pinned_until": 1624605641,
        "recording_mbid": null,
        "recording_msid": "40ef0ae1-5626-43eb-838f-1b34187519bf",
        "track_metadata": {
            "artist_name": "Rick Astley",
            "track_name": "Never Gonna Give You Up"
        },
        "user_name": "-- the MusicBrainz ID of the user who pinned this recording --"
        },
        "-- more pinned recordings from different users here ---"
    ],
    "user_name": "-- the MusicBrainz ID of the original user --"
}
Parameters:
- user_name (str) – the MusicBrainz ID of the user whose followed user’s pinned recordings are being requested.
- count (int) – Optional, number of pinned recording items to return, Default: DEFAULT_ITEMS_PER_GET Max: MAX_ITEMS_PER_GET
- offset (int) – Optional, number of pinned recording items to skip from the beginning, for pagination. Ex. An offset of 5 means the most recent pinned recordings from the first 5 users will be skipped, defaults to 0
Status Codes:
- 200 OK – Yay, you have data!
- 400 Bad Request – Invalid query parameters. See error message for details.
- 404 Not Found – The requested user was not found.
Response Headers:
- Content-Type – application/json

### GET /1/(mb_username: user_name)/pins/current
Get the currently pinned recording by a user with given user_name. The JSON returned by the API will look like the following:
{
    "pinned_recording": {
        "blurb_content": "Awesome recording!",
        "created": 1623997168,
        "row_id": 10,
        "pinned_until": 1623997485,
        "recording_mbid": null,
        "recording_msid": "fd7d9162-a284-4a10-906c-faae4f1e166b"
        "track_metadata": {
            "artist_name": "Rick Astley",
            "track_name": "Never Gonna Give You Up"
        }
    },
    "user_name": "-- the MusicBrainz ID of the user --"
}
If there is no current pin for the user, “pinned_recording” field will be null.
Note: A pin ceases to be current if it is manually unpinned, expires (defaults to DAYS_UNTIL_UNPIN days), or is replaced by a new pin.
Parameters:
- user_name (str) – the MusicBrainz ID of the user whose pin track history requested.
Status Codes:
- 200 OK – Yay, you have data!
- 404 Not Found – The requested user was not found.
Response Headers:
- Content-Type – application/json

### POST /1/pin/update/(row_id)
Updates the blurb content of a pinned recording for the user. A user token (found on https://listenbrainz.org/settings/) must be provided in the Authorization header! Each request should contain only one pinned recording item in the payload.
The format of the JSON to be POSTed to this endpoint should look like the following:
{
    "blurb_content": "Wow..",
}
Request Headers:
- Authorization – Token <user token>
Status Codes:
- 200 OK – feedback accepted.
- 400 Bad Request – invalid JSON sent, see error message for details.
- 401 Unauthorized – invalid authorization. See error message for details.
Response Headers:
- Content-Type – application/json
