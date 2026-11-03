<!-- source: https://listenbrainz.readthedocs.io/en/latest/users/api/recommendation.html -->
<!-- site: ListenBrainz documentation -->

# Recommendations

ListenBrainz uses collaborative filtering to generate recording recommendations, which may be further processed to generate playlists for users.

## Recording Recommendation API
These api endpoints allow to fetch the raw collaborative filtered recording IDs.

### GET /1/cf/recommendation/user/(mb_username: user_name)/recording
Get recommendations sorted on rating and ratings for user user_name.
A sample response from the endpoint may look like:
{
    "payload": {
        "last_updated": 1588494361,
        "type": "<artist_type>",
        "entity": "recording",
        "mbids": [
            {
                "recording_mbid": "526bd613-fddd-4bd6-9137-ab709ac74cab",
                "score": 9.345
            },
            {
                "recording_mbid": "a6081bc1-2a76-4984-b21f-38bc3dcca3a5",
                "score": 6.998
            }
        ],
        "user_name": "unclejohn69",
        "count": 10,
        "total_mbid_count": 30,
        "offset": 10
    }
}
Note
- This endpoint is experimental and probably will change in the future.
Parameters:
- count (int) – Optional, number of recording mbids to return, Default: DEFAULT_ITEMS_PER_GET Max: MAX_ITEMS_PER_GET
- offset (int) – Optional, number of mbids to skip from the beginning, for pagination. Ex. An offset of 5 means the 5 mbids will be skipped, defaults to 0
Status Codes:
- 200 OK – Successful query, you have data!
- 400 Bad Request – Bad request, check response['error'] for more details
- 404 Not Found – User not found.
- 204 No Content – Recommendations for the user haven’t been generated, empty response will be returned

## Recording Recommendation Feedback API
These api endpoints allow to submit and retrieve feedback for raw collaborative filtered recordings.

### POST /1/recommendation/feedback/submit
Submit recommendation feedback. A user token (found on https://listenbrainz.org/settings/ ) must be provided in the Authorization header! Each request should contain only one feedback in the payload.
A sample feedback may look like:
{
    "recording_mbid": "d23f4719-9212-49f0-ad08-ddbfbfc50d6f",
    "rating": "love"
}
Request Headers:
- Authorization – Token <user token>
Status Codes:
- 200 OK – feedback accepted.
- 400 Bad Request – invalid JSON sent, see error message for details.
- 401 Unauthorized – invalid authorization. See error message for details.
Response Headers:
- Content-Type – application/json

### POST /1/recommendation/feedback/delete
Delete feedback for a user. A user token (found on https://listenbrainz.org/settings/ ) must be provided in the Authorization header! Each request should contain only one recording mbid in the payload. A sample feedback may look like:
{
    "recording_mbid": "d23f4719-9212-49f0-ad08-ddbfbfc50d6f",
}
Request Headers:
- Authorization – Token <user token>
Status Codes:
- 200 OK – feedback deleted.
- 400 Bad Request – invalid JSON sent, see error message for details.
- 401 Unauthorized – invalid authorization. See error message for details.
Response Headers:
- Content-Type – application/json

### GET /1/recommendation/feedback/user/(mb_username: user_name)
Get feedback given by user user_name.
A sample response may look like:
{
    "count": 1,
    "feedback": [
        {
            "created": "1345679998",
            "recording_mbid": "d23f4719-9212-49f0-ad08-ddbfbfc50d6f",
            "rating": "love"
        },
        "-- more feedback data here ---"
    ],
    "offset": 0,
    "total_count": 1,
    "user_name": "Vansika"
}
If the optional argument rating is not given, this endpoint will return all the feedback submitted by the user. Otherwise filters the feedback to be returned by rating.
Parameters:
- rating (str) – Optional, refer to db/model/recommendation_feedback.py for allowed rating values.
- count (int) – Optional, number of feedback items to return, Default: DEFAULT_ITEMS_PER_GET Max: MAX_ITEMS_PER_GET.
- offset (int) – Optional, number of feedback items to skip from the beginning, for pagination. Ex. An offset of 5 means the top 5 feedback will be skipped, defaults to 0.
Status Codes:
- 200 OK – Yay, you have data!
- 404 Not Found – User not found.
- 400 Bad Request – Bad request, check response['error'] for more details
Response Headers:
- Content-Type – application/json

### GET /1/recommendation/feedback/user/(mb_username: user_name)/recordings
Get feedback given by user user_name for the list of recordings supplied.
A sample response may look like:
{
    "feedback": [
        {
            "created": 1604033691,
            "rating": "bad_recommendation",
            "recording_mbid": "9ffabbe4-e078-4906-80a7-3a02b537e251"
        },
        {
            "created": 1604032934,
            "rating": "hate",
            "recording_mbid": "28111d2c-a80d-418f-8b77-6aba58abe3e7"
        }
    ],
    "user_name": "Vansika Pareek"
}
An empty response will be returned if the feedback for given recording MBID doesn’t exist.
Parameters:
- mbids (str) – comma separated list of recording_mbids for which feedback records are to be fetched.
Status Codes:
- 200 OK – Yay, you have data!
- 400 Bad Request – Bad request, check response['error'] for more details.
- 404 Not Found – User not found.
Response Headers:
- Content-Type – application/json
