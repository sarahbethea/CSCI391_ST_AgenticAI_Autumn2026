<!-- source: https://listenbrainz.readthedocs.io/en/latest/users/api/metadata.html -->
<!-- site: ListenBrainz documentation -->

# Metadata

The metadata API looks up MusicBrainz metadata for recordings

### GET /1/metadata/recording/
This endpoint takes in a list of recording_mbids and returns an array of dicts that contain recording metadata suitable for showing in a context that requires as much detail about a recording and the artist. Using the inc parameter, you can control which portions of metadata to fetch.
The data returned by this endpoint can be seen here:
{
   "e97f805a-ab48-4c52-855e-07049142113d": {
      "tag": {
         "recording": [
            {
               "count": 8,
               "genre_mbid": "45eb1d9c-588c-4dc8-9394-a14b7c8f02bc",
               "tag": "trip hop"
            },
            {
               "count": 3,
               "genre_mbid": "89255676-1f14-4dd8-bbad-fca839d6aff4",
               "tag": "electronic"
            },
            {
               "count": 4,
               "tag": "trip-hop"
            }
         ],
         "artist": [
            {
               "artist_mbid": "8f6bd1e4-fbe1-4f50-aa9b-94c450ec0f11",
               "count": 13,
               "genre_mbid": "45eb1d9c-588c-4dc8-9394-a14b7c8f02bc",
               "tag": "trip hop"
            },
            {
               "artist_mbid": "8f6bd1e4-fbe1-4f50-aa9b-94c450ec0f11",
               "count": 7,
               "tag": "trip-hop"
            }
         ],
         "release_group": [
            {
               "count": 18,
               "genre_mbid": "45eb1d9c-588c-4dc8-9394-a14b7c8f02bc",
               "tag": "trip hop"
            },
            {
               "count": 6,
               "tag": "trip-hop"
            },
            {
               "count": 1,
               "tag": "mysterious"
            }
         ]
      },
      "recording": {
         "rels": [
            {
               "artist_name": "Beth Gibbons",
               "instrument": null,
               "artist_mbid": "5adcb9d9-5ea2-428d-af46-ef626966e106",
               "type": "vocal"
            },
            {
               "artist_mbid": "5082a11f-7203-4ff3-ae04-2a0150d3bbb6",
               "type": "instrument",
               "instrument": "Rhodes piano",
               "artist_name": "Geoff Barrow"
            },
            {
               "type": "instrument",
               "artist_mbid": "619b1116-740e-42e0-bdfe-96af274f79f7",
               "instrument": "guitar",
               "artist_name": "Adrian Utley"
            },
            {
               "artist_name": "Clive Deamer",
               "instrument": "drums (drum set)",
               "type": "instrument",
               "artist_mbid": "d576e6be-03d1-489c-8c3e-692c6fbfb7ca"
            }
         ]
      },
      "release": {
         "album_artist_name": "Portishead",
         "caa_id": 829521842,
         "caa_release_mbid": "76df3287-6cda-33eb-8e9a-044b5e15ffdd",
         "mbid": "76df3287-6cda-33eb-8e9a-044b5e15ffdd",
         "name": "Dummy",
         "release_group_mbid": "48140466-cff6-3222-bd55-63c27e43190d",
         "year": 1994
      },
      "artist": {
         "artist_credit_id": 65,
         "name": "Portishead",
         "artists": [
            {
               "area": "United Kingdom",
               "artist_mbid": "8f6bd1e4-fbe1-4f50-aa9b-94c450ec0f11",
               "begin_year": 1991,
               "join_phrase": "",
               "name": "Portishead",
               "rels": {
                  "free streaming": "https://www.deezer.com/artist/1069",
                  "lyrics": "https://muzikum.eu/en/122-6105/portishead/lyrics.html",
                  "official homepage": "http://www.portishead.co.uk/",
                  "purchase for download": "https://www.junodownload.com/artists/Portishead/releases/",
                  "social network": "https://www.facebook.com/portishead",
                  "streaming": "https://tidal.com/artist/27441",
                  "wikidata": "https://www.wikidata.org/wiki/Q191352",
                  "youtube": "https://www.youtube.com/user/portishead1002"
               },
               "type": "Group"
            }
         ]
      }
   }
}
Parameters:
- recording_mbids (str) – A comma separated list of recording_mbids
- inc (str) – A space separated list of “artist”, “tag” and/or “release” to indicate which portions of metadata you’re interested in fetching. We encourage users to only fetch the data they plan to consume.
Status Codes:
- 200 OK – you have data!
- 400 Bad Request – invalid recording_mbid arguments

### POST /1/metadata/recording/
This endpoint is the POST verson for fetching recording metadata, since it allows up to the max number of items allowed. (MAX_ITEMS_PER_GET items)
A JSON document with a list of recording_mbids and inc string must be POSTed to this endpoint to returns an array of dicts that contain recording metadata suitable for showing in a context that requires as much detail about a recording and the artist. Using the inc parameter, you can control which portions of metadata to fetch.
{
     "recording_mbids": [ "25d47b0c-5177-49db-b740-c166e4acebd1", "..." ],
     "inc": "artist tag"
}
To see what data this endpoint returns, please look at the data above for the GET version.
Status Codes:
- 200 OK – you have data!
- 400 Bad Request – invalid recording_mbid arguments

### GET /1/metadata/release_group/
This endpoint takes in a list of release_group_mbids and returns an array of dicts that contain release_group metadata suitable for showing in a context that requires as much detail about a release_group and the artist. Using the inc parameter, you can control which portions of metadata to fetch.
The data returned by this endpoint can be seen here:
{
   "48140466-cff6-3222-bd55-63c27e43190d": {
      "artist": {
         "artist_credit_id": 65,
         "name": "Portishead",
         "artists": [
            {
               "area": "United Kingdom",
               "artist_mbid": "8f6bd1e4-fbe1-4f50-aa9b-94c450ec0f11",
               "begin_year": 1991,
               "join_phrase": "",
               "name": "Portishead",
               "rels": {
                  "free streaming": "https://www.deezer.com/artist/1069",
                  "lyrics": "https://muzikum.eu/en/122-6105/portishead/lyrics.html",
                  "official homepage": "http://www.portishead.co.uk/",
                  "purchase for download": "https://www.junodownload.com/artists/Portishead/releases/",
                  "social network": "https://www.facebook.com/portishead",
                  "streaming": "https://tidal.com/artist/27441",
                  "wikidata": "https://www.wikidata.org/wiki/Q191352",
                  "youtube": "https://www.youtube.com/user/portishead1002"
               },
               "type": "Group"
            }
         ]
      },
      "release": {
         "caa_id": 829521842,
         "caa_release_mbid": "76df3287-6cda-33eb-8e9a-044b5e15ffdd",
         "date": "1994-08-22",
         "name": "Dummy",
         "rels": [],
         "type": "Album"
      },
      "release_group": {
         "caa_id": 829521842,
         "caa_release_mbid": "76df3287-6cda-33eb-8e9a-044b5e15ffdd",
         "date": "1994-08-22",
         "name": "Dummy",
         "rels": [],
         "type": "Album"
      },
      "tag": {
         "artist": [
            {
               "artist_mbid": "8f6bd1e4-fbe1-4f50-aa9b-94c450ec0f11",
               "count": 7,
               "tag": "trip-hop"
            },
            {
               "artist_mbid": "8f6bd1e4-fbe1-4f50-aa9b-94c450ec0f11",
               "count": 13,
               "genre_mbid": "45eb1d9c-588c-4dc8-9394-a14b7c8f02bc",
               "tag": "trip hop"
            },
            {
               "artist_mbid": "8f6bd1e4-fbe1-4f50-aa9b-94c450ec0f11",
               "count": 6,
               "genre_mbid": "cc38aba3-48ed-439a-83b9-f81a34a66598",
               "tag": "downtempo"
            },
            {
               "artist_mbid": "8f6bd1e4-fbe1-4f50-aa9b-94c450ec0f11",
               "count": 5,
               "genre_mbid": "65c97e89-b42b-45c2-a70e-0eca1b8f0ff7",
               "tag": "experimental rock"
            }
         ],
         "release_group": [
            {
               "count": 6,
               "tag": "trip-hop"
            },
            {
               "count": 4,
               "genre_mbid": "cc38aba3-48ed-439a-83b9-f81a34a66598",
               "tag": "downtempo"
            },
            {
               "count": 18,
               "genre_mbid": "45eb1d9c-588c-4dc8-9394-a14b7c8f02bc",
               "tag": "trip hop"
            }
         ]
      }
   }
}
Parameters:
- release_group_mbids (str) – A comma separated list of release_group_mbids
- inc (str) – A space separated list of “artist”, “tag” and/or “release” to indicate which portions of metadata you’re interested in fetching. We encourage users to only fetch the data they plan to consume.
Status Codes:
- 200 OK – you have data!
- 400 Bad Request – invalid release_group_mbid arguments

### GET /1/metadata/lookup/
This endpoint looks up mbid metadata for the given artist, recording and optionally a release name. The total number of characters in the artist name, recording name and release name query arguments should be less than or equal to MAX_MAPPING_QUERY_LENGTH.
The data returned by this endpoint can be seen here:
{
   "artist_credit_name": "Rick Astley",
   "artist_mbids": [
      "db92a151-1ac2-438b-bc43-b82e149ddd50"
   ],
   "recording_mbid": "8f3471b5-7e6a-48da-86a9-c1c07a0f47ae",
   "recording_name": "Never Gonna Give You Up",
   "release_mbid": "18550a84-4ede-451c-a91a-dd9b3af9f71d",
   "release_name": "Red Hot"
}
Request Headers:
- Authorization – Token <user token>
Parameters:
- artist_name (str) – artist name of the listen
- recording_name (str) – track name of the listen
- release_name (str) – release name of the listen
- metadata (bool) – should extra metadata be also returned if a match is found, see /metadata/recording for details.
- inc (str) – same as /metadata/recording endpoint
Status Codes:
- 200 OK – lookup succeeded, does not indicate whether a match was found or not
- 400 Bad Request – invalid arguments
Note: Because of possible abuse by AI scrapers, this endpoint now requires an auth token.

### POST /1/metadata/lookup/
This endpoint is the POST version for looking up recording mbids and associated MusicBrainz data. It allows up to max number of items allowed. (MAX_LOOKUPS_PER_POST items)
A JSON document with a list of dicts each of which contain metadata (artist_name, recording_name and optionally a release name) for the recording to be looked up. The total number of characters in the artist name, recording name and release name for each recording should be less than or equal to MAX_MAPPING_QUERY_LENGTH.
{
  "recordings": [
    {
      "recording_name": "Never Gonna Give You Up",
      "artist_name": "Rick Astley",
      "release_name": "Red Hot"
    },
    {
      "recording_name": "Blinding Lights",
      "artist_name": "The Weeknd"
    }
  ]
}
To see what data this endpoint returns, please look at the data above for the GET version. Note that this endpoint does not support metadata and incs parameters.
Request Headers:
- Authorization – Token <user token>
Status Codes:
- 200 OK – lookup succeeded, does not indicate whether a match was found or not
- 400 Bad Request – invalid arguments
Note: Because of possible abuse by AI scrapers, this endpoint now requires an auth token.

### POST /1/metadata/submit_manual_mapping/
Submit a manual mapping of a recording messybrainz ID to a musicbrainz recording id.
The format of the JSON to be POSTed to this endpoint is:
{
    "recording_msid": "d23f4719-9212-49f0-ad08-ddbfbfc50d6f",
    "recording_mbid": "8f3471b5-7e6a-48da-86a9-c1c07a0f47ae"
}
Request Headers:
- Authorization – Token <user token>
- Content-Type – application/json
Status Codes:
- 200 OK – Mapping added, or already exists.
- 400 Bad Request – invalid JSON sent, see error message for details.
- 401 Unauthorized – invalid authorization. See error message for details.
Response Headers:
- Content-Type – application/json

### GET /1/metadata/get_manual_mapping/
Get the manual mapping of a recording messybrainz ID that a user added.
Request Headers:
- Authorization – Token <user token>
- Content-Type – application/json
Status Codes:
- 200 OK – The response of the mapping.
- 404 Not Found – No such mapping for this user/recording msid
Response Headers:
- Content-Type – application/json

### GET /1/metadata/artist/
This endpoint takes in a list of artist_mbids and returns an array of dicts that contain recording metadata suitable for showing in a context that requires as much detail about a recording and the artist. Using the inc parameter, you can control which portions of metadata to fetch.
The data returned by this endpoint can be seen here:
[
   {
      "area": "United Kingdom",
      "artist_mbid": "8f6bd1e4-fbe1-4f50-aa9b-94c450ec0f11",
      "begin_year": 1991,
      "mbid": "8f6bd1e4-fbe1-4f50-aa9b-94c450ec0f11",
      "name": "Portishead",
      "type": "Group",
      "rels": {
         "free streaming": "https://www.deezer.com/artist/1069",
         "lyrics": "https://muzikum.eu/en/122-6105/portishead/lyrics.html",
         "official homepage": "http://www.portishead.co.uk/",
         "purchase for download": "https://www.junodownload.com/artists/Portishead/releases/",
         "social network": "https://www.facebook.com/portishead",
         "streaming": "https://tidal.com/artist/27441",
         "wikidata": "https://www.wikidata.org/wiki/Q191352",
         "youtube": "https://www.youtube.com/user/portishead1002"
      },
      "tag": {
         "artist": [
            {
               "artist_mbid": "8f6bd1e4-fbe1-4f50-aa9b-94c450ec0f11",
               "count": 6,
               "genre_mbid": "cc38aba3-48ed-439a-83b9-f81a34a66598",
               "tag": "downtempo"
            },
            {
               "artist_mbid": "8f6bd1e4-fbe1-4f50-aa9b-94c450ec0f11",
               "count": 13,
               "genre_mbid": "45eb1d9c-588c-4dc8-9394-a14b7c8f02bc",
               "tag": "trip hop"
            },
            {
               "artist_mbid": "8f6bd1e4-fbe1-4f50-aa9b-94c450ec0f11",
               "count": 7,
               "tag": "trip-hop"
            }
         ]
      }
   }
]
Parameters:
- artist_mbids (str) – A comma separated list of recording_mbids
- inc (str) – A space separated list of “artist”, “tag” and/or “release” to indicate which portions of metadata you’re interested in fetching. We encourage users to only fetch the data they plan to consume.
Status Codes:
- 200 OK – you have data!
- 400 Bad Request – invalid recording_mbid arguments
