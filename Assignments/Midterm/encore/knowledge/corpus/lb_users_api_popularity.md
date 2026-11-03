<!-- source: https://listenbrainz.readthedocs.io/en/latest/users/api/popularity.html -->
<!-- site: ListenBrainz documentation -->

# Popularity

The popularity APIs return the total listen and listeners count for various entities and also a way to query top entities for a given artist.

### GET /1/popularity/top-recordings-for-artist/(artist_mbid)
Get the top recordings by listen count for a given artist. The response is of the following format:
[
  {
    "artist_mbids": [
      "b7ffd2af-418f-4be2-bdd1-22f8b48613da"
    ],
    "artist_name": "Nine Inch Nails",
    "caa_id": 2546761764,
    "caa_release_mbid": "2d410836-5add-3661-b0b0-168ba1696611",
    "length": 373133,
    "recording_mbid": "13dd61c7-ce73-4e97-9f0c-9f0e53144411",
    "recording_name": "Closer",
    "release_color": {
        "blue": 104,
        "green": 104,
        "red": 84
    },
    "release_mbid": "ba8701ba-dc7c-4bca-9c83-846ee8c3d576",
    "release_name": "The Downward Spiral",
    "total_listen_count": 1380798,
    "total_user_count": 129454
  }
]
Status Codes:
- 200 OK – you have data!
- 400 Bad Request – invalid artist_mbid

### GET /1/popularity/top-release-groups-for-artist/(artist_mbid)
Get the top release groups by listen count for a given artist. The response is of the following format:
[
  {
    "artist": {
      "artist_credit_id": 368737,
      "artists": [],
      "name": "Pritam"
    },
    "release": {
      "caa_id": 14996821464,
      "caa_release_mbid": "488ef20e-7a2b-4daf-8bee-4f54fe26c7ab",
      "date": "2016-10-26",
      "name": "Ae Dil Hai Mushkil",
      "rels": [],
      "type": "Album"
    },
    "release_color": {
      "blue": 64,
      "green": 69,
      "red": 113
    },
    "release_group": {
      "caa_id": 14996821464,
      "caa_release_mbid": "488ef20e-7a2b-4daf-8bee-4f54fe26c7ab",
      "date": "2016-10-26",
      "name": "Ae Dil Hai Mushkil",
      "rels": [],
      "type": "Album"
    },
    "release_group_mbid": "d0991cc9-2277-4f5e-bd4d-2fa44507f623",
    "tag": {},
    "total_listen_count": 1432,
    "total_user_count": 82
  },
]
Parameters:
- artist_mbid (str) – the mbid of the artist to get top release groups for
Status Codes:
- 200 OK – you have data!
- 400 Bad Request – invalid artist_mbid

### POST /1/popularity/recording
Get the total listen count and total unique listeners count for a given recording.
A JSON document with a list of recording_mbids and inc string must be POSTed. Up to MAX_ITEMS_PER_GET items can be requested at once. Example:
{
    "recording_mbids": [
        "13dd61c7-ce73-4e97-9f0c-9f0e53144411",
        "22ad712e-ce73-9f0c-4e97-9f0e53144411"
    ]
}
The response maintains the order of the recording mbids supplied and also includes any recordings for which the data was not found with counts set to null. Example:
[
    {
        "recording_mbid": "13dd61c7-ce73-4e97-9f0c-9f0e53144411",
        "total_listen_count": 1000,
        "total_user_count": 10
    },
    {
        "recording_mbid": "22ad712e-ce73-9f0c-4e97-9f0e53144411",
        "total_listen_count": null,
        "total_user_count": null
    }
]
Status Codes:
- 200 OK – you have data!
- 400 Bad Request – invalid recording_mbid(s)

### POST /1/popularity/artist
Get the total listen count and total unique listeners count for a given artist.
A JSON document with a list of artists and inc string must be POSTed. Up to MAX_ITEMS_PER_GET items can be requested at once. Example:
{
    "artist_mbids": [
        "13dd61c7-ce73-4e97-9f0c-9f0e53144411",
        "22ad712e-ce73-9f0c-4e97-9f0e53144411"
    ]
}
The response maintains the order of the artist mbids supplied and also includes any artists for which the data was not found with counts set to null. Example:
[
    {
        "artist_mbid": "13dd61c7-ce73-4e97-9f0c-9f0e53144411",
        "total_listen_count": 1000,
        "total_user_count": 10
    },
    {
        "artist_mbid": "22ad712e-ce73-9f0c-4e97-9f0e53144411",
        "total_listen_count": null,
        "total_user_count": null
    }
]
Status Codes:
- 200 OK – you have data!
- 400 Bad Request – invalid artist_mbid(s)

### POST /1/popularity/release
Get the total listen count and total unique listeners count for a given release.
A JSON document with a list of releases and inc string must be POSTed. Up to MAX_ITEMS_PER_GET items can be requested at once. Example:
{
    "release_mbids": [
        "13dd61c7-ce73-4e97-9f0c-9f0e53144411",
        "22ad712e-ce73-9f0c-4e97-9f0e53144411"
    ]
}
The response maintains the order of the release mbids supplied and also includes any releases for which the data was not found with counts set to null. Example:
[
    {
        "release_mbid": "13dd61c7-ce73-4e97-9f0c-9f0e53144411",
        "total_listen_count": 1000,
        "total_user_count": 10
    },
    {
        "release_mbid": "22ad712e-ce73-9f0c-4e97-9f0e53144411",
        "total_listen_count": null,
        "total_user_count": null
    }
]
Status Codes:
- 200 OK – you have data!
- 400 Bad Request – invalid release_mbid(s)

### POST /1/popularity/release-group
Get the total listen count and total unique listeners count for a given release group.
A JSON document with a list of release groups and inc string must be POSTed. Up to MAX_ITEMS_PER_GET items can be requested at once. Example:
{
    "release_group_mbids": [
        "13dd61c7-ce73-4e97-9f0c-9f0e53144411",
        "22ad712e-ce73-9f0c-4e97-9f0e53144411"
    ]
}
The response maintains the order of the release group mbids supplied and also includes any release groups for which the data was not found with counts set to null. Example:
[
    {
        "release_group_mbid": "13dd61c7-ce73-4e97-9f0c-9f0e53144411",
        "total_listen_count": 1000,
        "total_user_count": 10
    },
    {
        "release_group_mbid": "22ad712e-ce73-9f0c-4e97-9f0e53144411",
        "total_listen_count": null,
        "total_user_count": null
    }
]
Status Codes:
- 200 OK – you have data!
- 400 Bad Request – invalid release_group_mbid(s)
