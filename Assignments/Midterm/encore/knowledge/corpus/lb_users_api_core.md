<!-- source: https://listenbrainz.readthedocs.io/en/latest/users/api/core.html -->
<!-- site: ListenBrainz documentation -->

# Core

The ListenBrainz server supports the following end-points for submitting and fetching listens.
To retrieve a user’s entire listening history, use the export API. Do not scrape or paginate through the user’s entire history using the listens endpoint. Use that endpoint for recent listens, bounded queries, and incremental updates after importing an export.

### GET /1/search/users/
Search a ListenBrainz-registered user.
Parameters:
- search_term – Input on which search operation is to be performed.

### POST /1/submit-listens
Submit listens to the server. A user token (found on https://listenbrainz.org/settings/ ) must be provided in the Authorization header! Each request should also contain at least one listen in the payload.
Listens should be submitted for tracks when the user has listened to half the track or 4 minutes of the track, whichever is lower. If the user hasn’t listened to 4 minutes or half the track, it doesn’t fully count as a listen and should not be submitted.
For complete details on the format of the JSON to be POSTed to this endpoint, see JSON Documentation.
Parameters:
- return_msid – If set to true and the listen_type is ‘playing_now’, the response will include a recording_msid (to be used for submitting love/hate feedback). Defaults to false.
Request Headers:
- Authorization – Token <user token>
- Content-Type – application/json
Status Codes:
- 200 OK – listen(s) accepted.
- 400 Bad Request – invalid JSON sent, see error message for details.
- 401 Unauthorized – invalid authorization. See error message for details.
Response Headers:
- Content-Type – application/json

### GET /1/user/(mb_username: user_name)/listens
Get listens for user user_name. The format for the JSON returned is defined in our JSON Documentation.
If none of the optional arguments are given, this endpoint will return the DEFAULT_ITEMS_PER_GET most recent listens. The optional max_ts and min_ts UNIX epoch timestamps control at which point in time to start returning listens. You may specify max_ts or min_ts, but not both in one call. Listens are always returned in descending timestamp order.
Parameters:
- max_ts – If you specify a max_ts timestamp, listens with listened_at less than (but not including) this value will be returned.
- min_ts – If you specify a min_ts timestamp, listens with listened_at greater than (but not including) this value will be returned.
- count – Optional, number of listens to return. Default: DEFAULT_ITEMS_PER_GET . Max: MAX_ITEMS_PER_GET
Status Codes:
- 200 OK – Yay, you have data!
- 404 Not Found – The requested user was not found.
Response Headers:
- Content-Type – application/json

### GET /1/user/(mb_username: user_name)/listen-count
Get the number of listens for a user user_name.
The returned listen count has an element ‘payload’ with only key: ‘count’ which unsurprisingly contains the listen count for the user.
Status Codes:
- 200 OK – Yay, you have listen counts!
- 404 Not Found – The requested user was not found.
Response Headers:
- Content-Type – application/json

### GET /1/user/(mb_username: user_name)/playing-now
Get the listen being played right now for user user_name.
This endpoint returns a JSON document with a single listen in the same format as the /user/<user_name>/listens endpoint, with one key difference, there will only be one listen returned at maximum and the listen will not contain a listened_at element.
The format for the JSON returned is defined in our JSON Documentation.
Status Codes:
- 200 OK – Yay, you have data!
- 404 Not Found – The requested user was not found.
Response Headers:
- Content-Type – application/json

### POST /1/playing-now/delete
Clear the playing now status for the user. If a client is provided in the request body, the endpoint will only clear the playing_now if it was submitted by the specified client. If no client is provided, the playing_now will be cleared unconditionally.
Request Headers:
- Authorization – Token <user token>
- Content-Type – application/json
Status Codes:
- 200 OK – Successfully cleared playing now status (or no playing_now exists).
- 400 Bad Request – Invalid request (invalid JSON).
- 401 Unauthorized – Invalid authorization.
- 404 Not Found – The current playing_now was not submitted by the specified client.
Response Headers:
- Content-Type – application/json

### GET /1/user/(mb_username: user_name)/similar-users
Get list of users who have similar music tastes (based on their listen history) for a given user. Returns an array of dicts like these:
{
    "user_name": "hwnrwx",
    "similarity": 0.1938480256
}
Parameters:
- user_name – the MusicBrainz ID of the user whose similar users are being requested.
Status Codes:
- 200 OK – Yay, you have data!
- 404 Not Found – The requested user was not found.
Response Headers:
- Content-Type – application/json

### GET /1/user/(mb_username: user_name)/similar-to/(mb_username: other_user_name)
Get the similarity of the user and the other user, based on their listening history. Returns a single dict:
{
    "user_name": "other_user",
    "similarity": 0.1938480256
}
Parameters:
- user_name – the MusicBrainz ID of the the one user
- other_user_name – the MusicBrainz ID of the other user whose similar users are
Status Codes:
- 200 OK – Yay, you have data!
- 404 Not Found – The requested user was not found.
Response Headers:
- Content-Type – application/json

### GET /1/validate-token
Check whether a User Token is a valid entry in the database.
In order to query this endpoint, send a GET request with the Authorization header set to the value Token [the token value].
Note
This endpoint also checks for token argument in query params (example: /validate-token?token=token-to-check) if the Authorization header is missing for backward compatibility.
A JSON response, with the following format, will be returned.
- If the given token is valid:
{
    "code": 200,
    "message": "Token valid.",
    "valid": true,
    "user_name": "MusicBrainz ID of the user with the passed token"
}
- If the given token is invalid:
{
    "code": 200,
    "message": "Token invalid.",
    "valid": false,
}
Status Codes:
- 200 OK – The user token is valid/invalid.
- 400 Bad Request – No token was sent to the endpoint.

### POST /1/delete-listen
Delete a particular listen from a user’s listen history. This checks for the correct authorization token and deletes the listen.
Note
The listen is not deleted immediately, but is scheduled for deletion, which usually happens shortly after the hour.
The format of the JSON to be POSTed to this endpoint is:
{
    "listened_at": 1,
    "recording_msid": "d23f4719-9212-49f0-ad08-ddbfbfc50d6f"
}
Request Headers:
- Authorization – Token <user token>
- Content-Type – application/json
Status Codes:
- 200 OK – listen deleted.
- 400 Bad Request – invalid JSON sent, see error message for details.
- 401 Unauthorized – invalid authorization. See error message for details.
Response Headers:
- Content-Type – application/json

### GET /1/user/(playlist_user_name)/playlists
Fetch playlist metadata in JSPF format without recordings for the given user. If a user token is provided in the Authorization header, return private playlists as well as public playlists for that user.
Parameters:
- count (int) – The number of playlists to return (for pagination). Default DEFAULT_NUMBER_OF_PLAYLISTS_PER_CALL
- offset (int) – The offset of into the list of playlists to return (for pagination)
Status Codes:
- 200 OK – Yay, you have data!
- 404 Not Found – User not found
Response Headers:
- Content-Type – application/json

### GET /1/user/(playlist_user_name)/playlists/createdfor
Fetch playlist metadata in JSPF format without recordings that have been created for the user. Createdfor playlists are all public, so no Authorization is needed for this call.
Parameters:
- count (int) – The number of playlists to return (for pagination). Default DEFAULT_NUMBER_OF_PLAYLISTS_PER_CALL
- offset (int) – The offset of into the list of playlists to return (for pagination)
Status Codes:
- 200 OK – Yay, you have data!
- 404 Not Found – User not found
Response Headers:
- Content-Type – application/json

### GET /1/user/(playlist_user_name)/playlists/collaborator
Fetch playlist metadata in JSPF format without recordings for which a user is a collaborator. If a playlist is private, it will only be returned if the caller is authorized to edit that playlist.
Parameters:
- count (int) – The number of playlists to return (for pagination). Default DEFAULT_NUMBER_OF_PLAYLISTS_PER_CALL
- offset (int) – The offset of into the list of playlists to return (for pagination)
Status Codes:
- 200 OK – Yay, you have data!
- 404 Not Found – User not found
Response Headers:
- Content-Type – application/json

### GET /1/user/(playlist_user_name)/playlists/recommendations
Fetch recommendation playlist metadata in JSPF format without recordings for playlist_user_name. This endpoint only lists playlists that are to be shown on the listenbrainz.org recommendations pages.
Status Codes:
- 200 OK – success
- 404 Not Found – user not found
Response Headers:
- Content-Type – application/json

### GET /1/user/(playlist_user_name)/playlists/search
Search for playlists associated with a user by name or description.
The search is a fuzzy match based on PostgreSQL trigram similarity and is performed against the playlist title and description. Results are ordered by decreasing similarity. The query is treated as a plain string
Parameters:
- playlist_user_name – the MusicBrainz ID of the user whose playlists are being searched.
Query Parameters:
- query – the query string used to search for playlists. Must be at least 3 characters long.
- name – deprecated alias for :queryparam:`query`.
- count – the number of playlists to return. Default: 25.
- offset – the offset of the playlists to return. Default: 0.
- include_global – if true, also include all public playlists globally in addition to the user’s associated playlists. Default: false.
Status Codes:
- 200 OK – success
- 404 Not Found – user not found
Response Headers:
- Content-Type – application/json

### GET /1/user/(mb_username: user_name)/services
Get list of services which are connected to a given user’s account.
{
    "user_name": "hwnrwx",
    "services": ["spotify"]
}
Parameters:
- user_name – the MusicBrainz ID of the user whose similar users are being requested.
Response Headers:
- Content-Type – application/json
Status Codes:
- 200 OK – Yay, you have data!
- 401 Unauthorized – Invalid authorization. See error message for details.
- 403 Forbidden – Forbidden, you do not have permissions to view this user’s information.
- 404 Not Found – The requested user was not found.

### GET /1/lb-radio/tags
Get recordings for use in LB radio with the specified tags that match the requested criteria.
Parameters:
- tag – the MusicBrainz tag to fetch recordings for, this parameter can be specified multiple times. if more than one tag is specified, the operator param should also be specified.
- operator – specify AND to retrieve recordings that have all the tags, otherwise specify OR to retrieve recordings that have any one of the tags.
- pop_begin – percent is a measure of the recording’s popularity, pop_begin denotes a preferred lower bound on the popularity of recordings to be returned.
- pop_end – percent is a measure of the recording’s popularity, pop_end denotes a preferred upper bound on the popularity of recordings to be returned.
- count – number of recordings to return for the
Response Headers:
- Content-Type – application/json
Status Codes:
- 200 OK – Yay, you have data!
- 400 Bad Request – Invalid or missing param in request, see error message for details.

### GET /1/lb-radio/artist/(seed_artist_mbid)
Get recordings for use in LB radio with the given seed artist. The endpoint returns a dict of all the similar artists, including the seed artist. For each artists, there will be a list of dicts that contain recording_mbid, similar_artist_mbid and total_listen_count:
{
  "recording_mbid": "401c1a5d-56e7-434d-b07e-a14d4e7eb83c",
  "similar_artist_mbid": "cb67438a-7f50-4f2b-a6f1-2bb2729fd538",
  "similar_artist_name": "Boo Hoo Boys",
  "total_listen_count": 232361
}
Parameters:
- mode – mode is the LB radio mode to be used for this query. Must be one of “easy”, “medium”, “hard”.
- max_similar_artists – The maximum number of similar artists to return recordings for.
- max_recordings_per_artist – The maximum number of recordings to return for each artist. If there are aren’t enough recordings, all available recordings will be returned.
- pop_begin – Popularity range percentage lower bound. A popularity range is given to narrow down the recordings into a smaller target group. The most popular recording(s) on LB have a pop percent of 100. The least popular recordings have a score of 0. This range is not coupled to the specified mode, but the mode would often determine the popularity range, so that less popular recordings can be returned on the medium and harder modes.
- pop_end – Popularity range percentage upper bound. See above.
Response Headers:
- Content-Type – application/json
Status Codes:
- 200 OK – Yay, you have data!
- 400 Bad Request – Invalid or missing param in request, see error message for details.

### GET /1/latest-import
Get the timestamp of the newest listen submitted by a user in previous imports to ListenBrainz.
In order to get the timestamp for a user, make a GET request to this endpoint. The data returned will be JSON of the following format:
{
    "musicbrainz_id": "the MusicBrainz ID of the user",
    "latest_import": "the timestamp of the newest listen submitted in previous imports. Defaults to 0"
}
Query Parameters:
- user_name (str) – the MusicBrainz ID of the user whose data is needed
Status Codes:
- 200 OK – Yay, you have data!
Response Headers:
- Content-Type – application/json

### POST /1/latest-import
Update the timestamp of the newest listen submitted by a user in an import to ListenBrainz.
In order to update the timestamp of a user, you’ll have to provide a user token in the Authorization Header. User tokens can be found on https://listenbrainz.org/settings/.
The JSON that needs to be posted must contain a field named ts in the root with a valid unix timestamp. Example:
{
   "ts": 0
}
Request Headers:
- Authorization – Token <user token>
Status Codes:
- 200 OK – latest import timestamp updated
- 400 Bad Request – invalid JSON sent, see error message for details.
- 401 Unauthorized – invalid authorization. See error message for details.

## Timestamps
All timestamps used in ListenBrainz are UNIX epoch timestamps in UTC. When submitting timestamps to us, please ensure that you have no timezone adjustments on your timestamps.

## Constants
Constants that are relevant to using the API:
listenbrainz.webserver.views.api_tools.MAX_LISTEN_PAYLOAD_SIZE = 10240000
The maximum size of a payload in bytes. The same as MAX_LISTEN_SIZE * MAX_LISTENS_PER_REQUEST.
listenbrainz.webserver.views.api_tools.MAX_LISTEN_SIZE = 10240
Maximum overall listen size in bytes, to prevent egregious spamming.
listenbrainz.webserver.views.api_tools.MAX_DURATION_LIMIT = 2073600
The max permitted value of duration field - 24 days
listenbrainz.webserver.views.api_tools.MAX_DURATION_MS_LIMIT = 2073600000
The max permitted value of duration_ms field - 24 days
listenbrainz.webserver.views.api_tools.MAX_LISTENS_PER_REQUEST = 1000
The maximum number of listens in a request.
listenbrainz.webserver.views.api_tools.MAX_ITEMS_PER_GET = 1000
The maximum number of listens returned in a single GET request.
listenbrainz.webserver.views.api_tools.DEFAULT_ITEMS_PER_GET = 25
The default number of listens returned in a single GET request.
listenbrainz.webserver.views.api_tools.MAX_TAGS_PER_LISTEN = 50
The maximum number of tags per listen.
listenbrainz.webserver.views.api_tools.MAX_TAG_SIZE = 64
The maximum length of a tag
listenbrainz.listenstore.LISTEN_MINIMUM_TS = 1033430400
The minimum acceptable value for listened_at field
listenbrainz.db.model.pinned_recording.DAYS_UNTIL_UNPIN = 7
Default number of days after which a pinned recording expires (gets unpinned).
