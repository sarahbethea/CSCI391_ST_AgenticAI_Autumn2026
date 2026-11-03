<!-- source: https://musicbrainz.org/doc/MusicBrainz_API/Search -->
<!-- site: MusicBrainz documentation -->

# MusicBrainz API: Search
| Status: This includes features to be released soon as part of the MusicBrainz 2025 Q2 schema change.
The MusicBrainz API search requests provide a way to search for MusicBrainz entities based on different sorts of queries. The results are returned in either XML (matching the MMD) or JSON format, and are provided by a search server built using Lucene technology.
This sections lists the parameters common to all resources.
| type | Selects the entity index to be searched: annotation, area, artist, cdstub, event, instrument, label, place, recording, release, release-group, series, tag, work, url
| fmt | Selects the representation of the results. Defaults to xml, but can also be set to json.
| query | Lucene search query. This is mandatory
| limit | An integer value defining how many entries should be returned. Only values between 1 and 100 (both inclusive) are allowed. If not given, this defaults to 25.
| offset | Return search results starting at a given offset. Used for paging through more than one page of results.
| dismax | If set to "true", switches the Solr query parser from edismax to dismax, which will escape certain special query syntax characters by default for ease of use. This is equivalent to switching from the "Indexed search with advanced query syntax" method to the plain "Indexed search" method on the website. Defaults to "false".
| version | MMD version, defaults to 2, version 1 is no longer supported since search overhaul in 2018.
The query field supports the full Lucene Search syntax; you can find a detailed guide at Lucene Search Syntax. For example, you can set conditions while searching for a name with the AND operator.
Example: https://musicbrainz.org/ws/2/recording?query=%22we%20will%20rock%20you%22%20AND%20arid:0383dadf-2a4e-4d10-a46a-e9e041da8eb3 will find any recordings of "We Will Rock You" by Queen.
To search for fields that are unknown or null, use the following syntax -
-search_field:*
Example: For releases with no format set can be searched via: -format:*
Numeric count based fields can be searched for by looking for 0
Example: https://musicbrainz.org/ws/2/release-group/?query=releases:0
To perform a literal search, you'll need to escape characters special to Lucene. This is in addition to any URL encoding.
Example: https://musicbrainz.org/ws/2/artist/?query=ac%5C%2Fdc

## Annotation

#### Example
http://musicbrainz.org/ws/2/annotation/?query=entity:bdb24cb5-404b-4f60-bba4-7b730325ae47

#### Search Fields
The Annotation index contains the following fields you can search
| Field | Description
| entity | the annotated entity's MBID
| id | the numeric ID of the annotation (e.g. 703027)
| name | the annotated entity's name or title (diacritics are ignored)
| text | the annotation's content (includes wiki formatting)
| type | the annotated entity's entity type
If you don't specify a field, the terms will be searched for in the name, text and type fields.

#### Xml
<metadata created="2013-02-05T04:41:32.273Z" xmlns="http://musicbrainz.org/ns/mmd-2.0#" xmlns:ext="http://musicbrainz.org/ns/ext#-2.0">
    <annotation-list count="1" offset="0">
        <annotation type="release" ext:score="100">
            <entity>bdb24cb5-404b-4f60-bba4-7b730325ae47</entity>
            <name>Pieds nus sur la braise</name>
            <text>Lyrics and music by Merzhin except:
04, 08, 09, 10 (V. L'hour - Merzhin),
03 (V. L'hour - P. Le Bourdonnec - Merzhin),
05 & 13 (P. Le Bourdonnec - Merzhin),
06 ([http://musicbrainz.org/artist/38cfa519-21bb-4e79-8388-3bf798b8c076.html|JM. Poisson] - Merzhin),
07 ([http://musicbrainz.org/artist/f2d7c07c-a8e7-45c9-a888-0b2e6e3a240d.html|Ignatus] - V. L'hour - Merzhin),
11 ([http://musicbrainz.org/artist/f2d7c07c-a8e7-45c9-a888-0b2e6e3a240d.html|Ignatus] - Merzhin),
12 ([http://musicbrainz.org/artist/38cfa519-21bb-4e79-8388-3bf798b8c076.html|JM. Poisson]).</text>
        </annotation>
    </annotation-list>
</metadata>

#### Json
{
  "created": "2017-03-12T16:27:16.317Z",
  "count": 1,
  "offset": 0,
  "annotations": [
    {
      "type": "release",
      "score": "100",
      "entity": "bdb24cb5-404b-4f60-bba4-7b730325ae47",
      "name": "Pieds nus sur la braise",
      "text": "Lyrics and music by Merzhin except:\r\n04, 08, 09, 10 (V. L'hour - Merzhin),\r\n03 (V. L'hour - P. Le Bourdonnec - Merzhin),\r\n05 & 13 (P. Le Bourdonnec - Merzhin),\r\n06 ([http://musicbrainz.org/artist/38cfa519-21bb-4e79-8388-3bf798b8c076.html|JM. Poisson] - Merzhin),\r\n07 ([http://musicbrainz.org/artist/f2d7c07c-a8e7-45c9-a888-0b2e6e3a240d.html|Ignatus] - V. L'hour - Merzhin),\r\n11 ([http://musicbrainz.org/artist/f2d7c07c-a8e7-45c9-a888-0b2e6e3a240d.html|Ignatus] - Merzhin),\r\n12 ([http://musicbrainz.org/artist/38cfa519-21bb-4e79-8388-3bf798b8c076.html|JM. Poisson])."
    }
  ]
}

## Area

#### Example
http://musicbrainz.org/ws/2/area/?query=%22%C3%8Ele-de-France%22

#### Search Fields
The Area index contains the following fields you can search
| Field | Description
| aid | the area's MBID
| alias | (part of) any alias attached to the artist (diacritics are ignored)
| area | (part of) the area's name (diacritics are ignored)
| areaaccent | (part of) the area's name (with the specified diacritics)
| begin | the area's begin date (e.g. "1980-01-22")
| comment | (part of) the area's disambiguation comment
| end | the area's end date (e.g. "1980-01-22")
| ended | a boolean flag (true/false) indicating whether or not the area has ended (is no longer current)
| iso | an ISO 3166-1, 3166-2 or 3166-3 code attached to the area
| iso1 | an ISO 3166-1 code attached to the area
| iso2 | an ISO 3166-2 code attached to the area
| iso3 | an ISO 3166-3 code attached to the area
| sortname | equivalent to name (areas no longer have separate sort names)
| tag | (part of) a tag attached to the area
| type | the area's type
If you don't specify a field, the terms will be searched for in the area field.

#### Xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<metadata created="2013-06-12T10:51:14.668Z" xmlns="http://musicbrainz.org/ns/mmd-2.0#" xmlns:ext="http://musicbrainz.org/ns/ext#-2.0">
    <area-list count="1" offset="0">
        <area id="d79e4501-8cba-431b-96e7-bb9976f0ae76" type="Subdivision" ext:score="100">
            <name>Île-de-France</name>
            <sort-name>Île-de-France</sort-name>
            <iso-3166-2-code-list>
                <iso-3166-2-code>FR-J</iso-3166-2-code>
            </iso-3166-2-code-list>
            <life-span>
                <ended>false</ended>
            </life-span>
            <alias-list>
                <alias locale="nl" sort-name="Île-de-France" type="Area name" primary="primary">Île-de-France</alias>
                <alias locale="en" sort-name="Île-de-France" type="Area name" primary="primary">Île-de-France</alias>
                <alias locale="fr" sort-name="Île-de-France" type="Area name" primary="primary">Île-de-France</alias>
                <alias locale="it" sort-name="Île-de-France" type="Area name" primary="primary">Île-de-France</alias>
                <alias locale="fi" sort-name="Île-de-France" type="Area name" primary="primary">Île-de-France</alias>
                <alias locale="et" sort-name="Île-de-France" type="Area name" primary="primary">Île-de-France</alias>
                <alias locale="de" sort-name="Île-de-France" type="Area name" primary="primary">Île-de-France</alias>
                <alias locale="no" sort-name="Île-de-France" type="Area name" primary="primary">Île-de-France</alias>
                <alias locale="es" sort-name="Isla de Francia" type="Area name" primary="primary">Isla de Francia</alias>
                <alias locale="ja" sort-name="イル＝ド＝フランス地域圏" type="Area name" primary="primary">イル＝ド＝フランス地域圏</alias>
            </alias-list>
        </area>
    </area-list>
</metadata>

#### Json
{
  "created": "2017-03-12T16:59:34.096Z",
  "count": 1,
  "offset": 0,
  "areas": [
    {
      "id": "d79e4501-8cba-431b-96e7-bb9976f0ae76",
      "type": "Subdivision",
      "score": "100",
      "name": "Île-de-France",
      "sort-name": "Île-de-France",
      "iso-3166-2-codes": [
        "FR-J"
      ],
      "life-span": {
        "ended": null
      },
      "aliases": [
        {
          "sort-name": "Île-de-France",
          "name": "Île-de-France",
          "locale": "no",
          "type": "Area name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Île-de-France",
          "name": "Île-de-France",
          "locale": "de",
          "type": "Area name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Île-de-France",
          "name": "Île-de-France",
          "locale": "en",
          "type": "Area name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Île-de-France",
          "name": "Île-de-France",
          "locale": "et",
          "type": "Area name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Île-de-France",
          "name": "Île-de-France",
          "locale": "fi",
          "type": "Area name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Île-de-France",
          "name": "Île-de-France",
          "locale": "fr",
          "type": "Area name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Île-de-France",
          "name": "Île-de-France",
          "locale": "it",
          "type": "Area name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Île-de-France",
          "name": "Île-de-France",
          "locale": "nl",
          "type": "Area name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Isla de Francia",
          "name": "Isla de Francia",
          "locale": "es",
          "type": "Area name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "イル＝ドフランス地域圏",
          "name": "イル＝ド＝フランス地域圏",
          "locale": "ja",
          "type": "Area name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        }
      ],
      "relation-list": [
        {
          "relations": [
            {
              "type": "part of",
              "type-id": "de7cc874-8b1b-3a05-8272-f3834c968fb7",
              "target": "08310658-51eb-3801-80de-5a0739207115",
              "direction": "backward",
              "area": {
                "id": "08310658-51eb-3801-80de-5a0739207115",
                "type": "Country",
                "name": "France",
                "sort-name": "France",
                "life-span": {
                  "ended": null
                }
              }
            }
          ]
        }
      ]
    }
  ]
}

## Artist

#### Example
http://musicbrainz.org/ws/2/artist/?query=artist:fred%20AND%20type:group%20AND%20country:US

#### Search Fields
The Artist index contains the following fields you can search
| Field | Description
| alias | (part of) any alias attached to the artist (diacritics are ignored)
| primary_alias | (part of) any primary alias attached to the artist (diacritics are ignored)
| area | (part of) the name of the artist's main associated area
| arid | the artist's MBID
| artist | (part of) the artist's name (diacritics are ignored)
| artistaccent | (part of) the artist's name (with the specified diacritics)
| begin | the artist's begin date (e.g. "1980-01-22")
| beginarea | (part of) the name of the artist's begin area
| comment | (part of) the artist's disambiguation comment
| country | the 2-letter code (ISO 3166-1 alpha-2) for the artist's main associated country
| end | the artist's end date (e.g. "1980-01-22")
| endarea | (part of) the name of the artist's end area
| ended | a boolean flag (true/false) indicating whether or not the artist has ended (is dissolved/deceased)
| gender | the artist's gender (“male”, “female”, “other” or “not applicable”)
| ipi | an IPI code associated with the artist
| isni | an ISNI code associated with the artist
| sortname | (part of) the artist's sort name
| tag | (part of) a tag attached to the artist
| type | the artist's type (“person”, “group”, etc.)
If you don't specify a field, the terms will be searched for in the alias, artist and sortname fields.

#### Xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<metadata created="2017-03-12T16:54:57.165Z" xmlns="http://musicbrainz.org/ns/mmd-2.0#" xmlns:ext="http://musicbrainz.org/ns/ext#-2.0">
  <artist-list count="11" offset="0">
    <artist id="e56fd97e-c18f-4e5e-9b4d-f9fc21b4973f" type="Group" ext:score="100">
      <name>Fred</name>
      <sort-name>Fred</sort-name>
      <country>US</country>
      <area id="489ce91b-6658-3307-9877-795b68554c98">
        <name>United States</name>
        <sort-name>United States</sort-name>
      </area>
      <begin-area id="489ce91b-6658-3307-9877-795b68554c98">
        <name>United States</name>
        <sort-name>United States</sort-name>
      </begin-area>
      <disambiguation>US progressive rock band</disambiguation>
      <life-span>
        <begin>1969</begin>
        <end>1974</end>
        <ended>true</ended>
      </life-span>
    </artist>
    <artist id="4a024fd4-305e-4fea-9d3f-4ec858766e6e" type="Group" ext:score="100">
      <name>Fred</name>
      <sort-name>Fred</sort-name>
      <country>US</country>
      <area id="489ce91b-6658-3307-9877-795b68554c98">
        <name>United States</name>
        <sort-name>United States</sort-name>
      </area>
      <disambiguation>US comic barbershop quartet</disambiguation>
      <life-span>
        <ended>false</ended>
      </life-span>
    </artist>
    <artist id="1065e6e0-b6b3-4224-9121-4502e52b9f9e" type="Group" ext:score="61">
      <name>A Halo Called Fred</name>
      <sort-name>A Halo Called Fred</sort-name>
      <country>US</country>
      <area id="489ce91b-6658-3307-9877-795b68554c98">
        <name>United States</name>
        <sort-name>United States</sort-name>
      </area>
      <life-span>
        <ended>false</ended>
      </life-span>
    </artist>
    <artist id="6c843bf3-a854-47ea-b1cf-ba40675710b7" type="Group" ext:score="61">
      <name>Fred Sherry String Quartet</name>
      <sort-name>Fred Sherry String Quartet</sort-name>
      <country>US</country>
      <area id="489ce91b-6658-3307-9877-795b68554c98">
        <name>United States</name>
        <sort-name>United States</sort-name>
      </area>
      <life-span>
        <ended>false</ended>
      </life-span>
    </artist>
    <artist id="be136e58-ccf5-47f0-a000-6e8d7eb3bae0" type="Group" ext:score="61">
      <name>The Color Fred</name>
      <sort-name>Color Fred, The</sort-name>
      <country>US</country>
      <area id="489ce91b-6658-3307-9877-795b68554c98">
        <name>United States</name>
        <sort-name>United States</sort-name>
      </area>
      <life-span>
        <begin>2003</begin>
        <ended>false</ended>
      </life-span>
    </artist>
    <artist id="2cea1456-daef-4bb1-b63c-4b6df03ebbd5" type="Group" ext:score="61">
      <name>The Fred Hersch Group</name>
      <sort-name>Hersch, Fred, The, Group</sort-name>
      <country>US</country>
      <area id="489ce91b-6658-3307-9877-795b68554c98">
        <name>United States</name>
        <sort-name>United States</sort-name>
      </area>
      <life-span>
        <ended>false</ended>
      </life-span>
    </artist>
    <artist id="28b020fa-d9b8-4d92-805c-54cd1b0197b7" type="Group" ext:score="61">
      <name>Jacob Fred Jazz Odyssey</name>
      <sort-name>Jacob Fred Jazz Odyssey</sort-name>
      <country>US</country>
      <area id="489ce91b-6658-3307-9877-795b68554c98">
        <name>United States</name>
        <sort-name>United States</sort-name>
      </area>
      <life-span>
        <begin>1994</begin>
        <ended>false</ended>
      </life-span>
      <alias-list>
        <alias sort-name="JFJO">JFJO</alias>
      </alias-list>
      <tag-list>
        <tag count="1">
          <name>jazz</name>
        </tag>
        <tag count="1">
          <name>jazz fusion</name>
        </tag>
        <tag count="1">
          <name>free jazz</name>
        </tag>
        <tag count="1">
          <name>oklahoma</name>
        </tag>
        <tag count="1">
          <name>us</name>
        </tag>
        <tag count="1">
          <name>tulsa</name>
        </tag>
      </tag-list>
    </artist>
    <artist id="4a903390-4381-4c32-90d0-803bd4f9ce34" type="Group" ext:score="56">
      <name>Fred Waring & His Pennsylvanians</name>
      <sort-name>Waring, Fred & His Pennsylvanians</sort-name>
      <country>US</country>
      <area id="489ce91b-6658-3307-9877-795b68554c98">
        <name>United States</name>
        <sort-name>United States</sort-name>
      </area>
      <life-span>
        <ended>false</ended>
      </life-span>
      <alias-list>
        <alias sort-name="Fred Waring and the Pennsylvanians">Fred Waring and the Pennsylvanians</alias>
        <alias sort-name="Fred Waring & Pennsylvanians">Fred Waring & Pennsylvanians</alias>
        <alias sort-name="Fred Waring's Pennsylvanians">Fred Waring's Pennsylvanians</alias>
        <alias sort-name="Fred Waring's Pennyslvanians">Fred Waring's Pennyslvanians</alias>
        <alias sort-name="Fred Waring & the Pennsylvanians">Fred Waring & the Pennsylvanians</alias>
        <alias sort-name="Waring, Fred & Pennsylvanians, The">Fred Waring & The Pennsylvanians</alias>
        <alias sort-name="Fred Warring & His Pennsylvanians">Fred Warring & His Pennsylvanians</alias>
        <alias sort-name="Waring's Pensylvanians">Waring's Pensylvanians</alias>
      </alias-list>
    </artist>
    <artist id="0980008b-f9cd-412e-b062-84212b756f4a" type="Group" ext:score="51">
      <name>Fred Williams & The Jewels Band</name>
      <sort-name>Williams, Fred & Jewels Band, The</sort-name>
      <country>US</country>
      <area id="489ce91b-6658-3307-9877-795b68554c98">
        <name>United States</name>
        <sort-name>United States</sort-name>
      </area>
      <life-span>
        <ended>false</ended>
      </life-span>
    </artist>
    <artist id="985bdbe7-ebf2-42b1-8ad6-5bb619385e67" type="Group" ext:score="51">
      <name>Fred Wesley and The J.B.’s</name>
      <sort-name>Wesley, Fred and J.B.’s, the</sort-name>
      <country>US</country>
      <area id="489ce91b-6658-3307-9877-795b68554c98">
        <name>United States</name>
        <sort-name>United States</sort-name>
      </area>
      <life-span>
        <ended>false</ended>
      </life-span>
      <alias-list>
        <alias sort-name="Fred and the New J.B.'s">Fred and the New J.B.'s</alias>
        <alias sort-name="Fred Wesley & The J.B.'s">Fred Wesley & The J.B.'s</alias>
        <alias sort-name="Fred Wesley & The JB's">Fred Wesley & The JB's</alias>
        <alias sort-name="Fred Wesley & The New J.B.'s">Fred Wesley & The New J.B.'s</alias>
        <alias sort-name="Fred Wesley & The New JB's">Fred Wesley & The New JB's</alias>
      </alias-list>
    </artist>
    <artist id="05cfb5c7-0152-41f4-a9c9-622e8f710dfa" type="Group" ext:score="51">
      <name>John Fred & His Playboy Band</name>
      <sort-name>Fred, John & His Playboy Band</sort-name>
      <country>US</country>
      <area id="489ce91b-6658-3307-9877-795b68554c98">
        <name>United States</name>
        <sort-name>United States</sort-name>
      </area>
      <begin-area id="34f02dc4-3173-4c68-86d1-c82504759342">
        <name>Baton Rouge</name>
        <sort-name>Baton Rouge</sort-name>
      </begin-area>
      <life-span>
        <begin>1956</begin>
        <end>1969</end>
        <ended>true</ended>
      </life-span>
      <alias-list>
        <alias sort-name="John Fred">John Fred</alias>
        <alias sort-name="John Fred and His Playboyband">John Fred and His Playboyband</alias>
        <alias sort-name="John Fred and His Play Boy Band">John Fred and His Play Boy Band</alias>
        <alias sort-name="John Fred And His Playboy Band">John Fred And His Playboy Band</alias>
        <alias sort-name="John Fred and His Playboys">John Fred and His Playboys</alias>
        <alias sort-name="John Fred and the Play Boy Band">John Fred and the Play Boy Band</alias>
        <alias sort-name="John Fred and the Playboys">John Fred and the Playboys</alias>
        <alias sort-name="John Fred & His Playboyband">John Fred & His Playboyband</alias>
        <alias sort-name="John Fred & His Playboys">John Fred & His Playboys</alias>
        <alias sort-name="John Fred & Hiss Playboy Band">John Fred & Hiss Playboy Band</alias>
        <alias sort-name="John Fred & Playboyband">John Fred & Playboyband</alias>
        <alias sort-name="John Fred & Playboy Band">John Fred & Playboy Band</alias>
        <alias sort-name="John Fred & the Play Boy Band">John Fred & the Play Boy Band</alias>
        <alias sort-name="John Fred & The Playboyband">John Fred & The Playboyband</alias>
        <alias sort-name="John Fred & The Playboy Band">John Fred & The Playboy Band</alias>
        <alias sort-name="John Fred & The Playboys">John Fred & The Playboys</alias>
      </alias-list>
    </artist>
  </artist-list>
</metadata>

#### Json
{
  "created": "2017-03-12T16:54:57.165Z",
  "count": 11,
  "offset": 0,
  "artists": [
    {
      "id": "e56fd97e-c18f-4e5e-9b4d-f9fc21b4973f",
      "type": "Group",
      "score": "100",
      "name": "Fred",
      "sort-name": "Fred",
      "country": "US",
      "area": {
        "id": "489ce91b-6658-3307-9877-795b68554c98",
        "name": "United States",
        "sort-name": "United States"
      },
      "begin-area": {
        "id": "489ce91b-6658-3307-9877-795b68554c98",
        "name": "United States",
        "sort-name": "United States"
      },
      "disambiguation": "US progressive rock band",
      "life-span": {
        "begin": "1969",
        "end": "1974",
        "ended": true
      }
    },
    {
      "id": "4a024fd4-305e-4fea-9d3f-4ec858766e6e",
      "type": "Group",
      "score": "100",
      "name": "Fred",
      "sort-name": "Fred",
      "country": "US",
      "area": {
        "id": "489ce91b-6658-3307-9877-795b68554c98",
        "name": "United States",
        "sort-name": "United States"
      },
      "disambiguation": "US comic barbershop quartet",
      "life-span": {
        "ended": null
      }
    },
    {
      "id": "1065e6e0-b6b3-4224-9121-4502e52b9f9e",
      "type": "Group",
      "score": "61",
      "name": "A Halo Called Fred",
      "sort-name": "A Halo Called Fred",
      "country": "US",
      "area": {
        "id": "489ce91b-6658-3307-9877-795b68554c98",
        "name": "United States",
        "sort-name": "United States"
      },
      "life-span": {
        "ended": null
      }
    },
    {
      "id": "6c843bf3-a854-47ea-b1cf-ba40675710b7",
      "type": "Group",
      "score": "61",
      "name": "Fred Sherry String Quartet",
      "sort-name": "Fred Sherry String Quartet",
      "country": "US",
      "area": {
        "id": "489ce91b-6658-3307-9877-795b68554c98",
        "name": "United States",
        "sort-name": "United States"
      },
      "life-span": {
        "ended": null
      }
    },
    {
      "id": "be136e58-ccf5-47f0-a000-6e8d7eb3bae0",
      "type": "Group",
      "score": "61",
      "name": "The Color Fred",
      "sort-name": "Color Fred, The",
      "country": "US",
      "area": {
        "id": "489ce91b-6658-3307-9877-795b68554c98",
        "name": "United States",
        "sort-name": "United States"
      },
      "life-span": {
        "begin": "2003",
        "ended": null
      }
    },
    {
      "id": "2cea1456-daef-4bb1-b63c-4b6df03ebbd5",
      "type": "Group",
      "score": "61",
      "name": "The Fred Hersch Group",
      "sort-name": "Hersch, Fred, The, Group",
      "country": "US",
      "area": {
        "id": "489ce91b-6658-3307-9877-795b68554c98",
        "name": "United States",
        "sort-name": "United States"
      },
      "life-span": {
        "ended": null
      }
    },
    {
      "id": "28b020fa-d9b8-4d92-805c-54cd1b0197b7",
      "type": "Group",
      "score": "61",
      "name": "Jacob Fred Jazz Odyssey",
      "sort-name": "Jacob Fred Jazz Odyssey",
      "country": "US",
      "area": {
        "id": "489ce91b-6658-3307-9877-795b68554c98",
        "name": "United States",
        "sort-name": "United States"
      },
      "life-span": {
        "begin": "1994",
        "ended": null
      },
      "aliases": [
        {
          "sort-name": "JFJO",
          "name": "JFJO",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        }
      ],
      "tags": [
        {
          "count": 1,
          "name": "jazz"
        },
        {
          "count": 1,
          "name": "jazz fusion"
        },
        {
          "count": 1,
          "name": "free jazz"
        },
        {
          "count": 1,
          "name": "oklahoma"
        },
        {
          "count": 1,
          "name": "us"
        },
        {
          "count": 1,
          "name": "tulsa"
        }
      ]
    },
    {
      "id": "4a903390-4381-4c32-90d0-803bd4f9ce34",
      "type": "Group",
      "score": "56",
      "name": "Fred Waring & His Pennsylvanians",
      "sort-name": "Waring, Fred & His Pennsylvanians",
      "country": "US",
      "area": {
        "id": "489ce91b-6658-3307-9877-795b68554c98",
        "name": "United States",
        "sort-name": "United States"
      },
      "life-span": {
        "ended": null
      },
      "aliases": [
        {
          "sort-name": "Fred Waring and the Pennsylvanians",
          "name": "Fred Waring and the Pennsylvanians",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Fred Waring & Pennsylvanians",
          "name": "Fred Waring & Pennsylvanians",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Fred Waring's Pennsylvanians",
          "name": "Fred Waring's Pennsylvanians",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Fred Waring's Pennyslvanians",
          "name": "Fred Waring's Pennyslvanians",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Fred Waring & the Pennsylvanians",
          "name": "Fred Waring & the Pennsylvanians",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Waring, Fred & Pennsylvanians, The",
          "name": "Fred Waring & The Pennsylvanians",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Fred Warring & His Pennsylvanians",
          "name": "Fred Warring & His Pennsylvanians",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Waring's Pensylvanians",
          "name": "Waring's Pensylvanians",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        }
      ]
    },
    {
      "id": "0980008b-f9cd-412e-b062-84212b756f4a",
      "type": "Group",
      "score": "51",
      "name": "Fred Williams & The Jewels Band",
      "sort-name": "Williams, Fred & Jewels Band, The",
      "country": "US",
      "area": {
        "id": "489ce91b-6658-3307-9877-795b68554c98",
        "name": "United States",
        "sort-name": "United States"
      },
      "life-span": {
        "ended": null
      }
    },
    {
      "id": "985bdbe7-ebf2-42b1-8ad6-5bb619385e67",
      "type": "Group",
      "score": "51",
      "name": "Fred Wesley and The J.B.’s",
      "sort-name": "Wesley, Fred and J.B.’s, the",
      "country": "US",
      "area": {
        "id": "489ce91b-6658-3307-9877-795b68554c98",
        "name": "United States",
        "sort-name": "United States"
      },
      "life-span": {
        "ended": null
      },
      "aliases": [
        {
          "sort-name": "Fred and the New J.B.'s",
          "name": "Fred and the New J.B.'s",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Fred Wesley & The J.B.'s",
          "name": "Fred Wesley & The J.B.'s",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Fred Wesley & The JB's",
          "name": "Fred Wesley & The JB's",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Fred Wesley & The New J.B.'s",
          "name": "Fred Wesley & The New J.B.'s",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Fred Wesley & The New JB's",
          "name": "Fred Wesley & The New JB's",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        }
      ]
    },
    {
      "id": "05cfb5c7-0152-41f4-a9c9-622e8f710dfa",
      "type": "Group",
      "score": "51",
      "name": "John Fred & His Playboy Band",
      "sort-name": "Fred, John & His Playboy Band",
      "country": "US",
      "area": {
        "id": "489ce91b-6658-3307-9877-795b68554c98",
        "name": "United States",
        "sort-name": "United States"
      },
      "begin-area": {
        "id": "34f02dc4-3173-4c68-86d1-c82504759342",
        "name": "Baton Rouge",
        "sort-name": "Baton Rouge"
      },
      "life-span": {
        "begin": "1956",
        "end": "1969",
        "ended": true
      },
      "aliases": [
        {
          "sort-name": "John Fred",
          "name": "John Fred",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "John Fred and His Playboyband",
          "name": "John Fred and His Playboyband",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "John Fred and His Play Boy Band",
          "name": "John Fred and His Play Boy Band",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "John Fred And His Playboy Band",
          "name": "John Fred And His Playboy Band",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "John Fred and His Playboys",
          "name": "John Fred and His Playboys",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "John Fred and the Play Boy Band",
          "name": "John Fred and the Play Boy Band",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "John Fred and the Playboys",
          "name": "John Fred and the Playboys",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "John Fred & His Playboyband",
          "name": "John Fred & His Playboyband",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "John Fred & His Playboys",
          "name": "John Fred & His Playboys",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "John Fred & Hiss Playboy Band",
          "name": "John Fred & Hiss Playboy Band",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "John Fred & Playboyband",
          "name": "John Fred & Playboyband",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "John Fred & Playboy Band",
          "name": "John Fred & Playboy Band",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "John Fred & the Play Boy Band",
          "name": "John Fred & the Play Boy Band",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "John Fred & The Playboyband",
          "name": "John Fred & The Playboyband",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "John Fred & The Playboy Band",
          "name": "John Fred & The Playboy Band",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "John Fred & The Playboys",
          "name": "John Fred & The Playboys",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        }
      ]
    }
  ]
}

## CDStubs

#### Example
http://musicbrainz.org/ws/2/cdstub/?query=title:Doo

#### Search Fields
The CD stub index contains the following fields you can search:
| Field | Description
| added | the date the CD stub was added (e.g. "2020-01-22")
| artist | (part of) the artist name set on the CD stub
| barcode | the barcode set on the CD stub
| comment | (part of) the comment set on the CD stub
| discid | the CD stub's Disc ID
| title | (part of) the release title set on the CD stub
| tracks | the number of tracks on the CD stub
If you don't specify a field, the terms will be searched for in the artist and title fields.

#### Xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<metadata created="2013-02-05T08:20:53.231Z" xmlns="http://musicbrainz.org/ns/mmd-2.0#" xmlns:ext="http://musicbrainz.org/ns/ext#-2.0">
    <cdstub-list count="1" offset="0">
        <cdstub id="NKpg6j_S6swmiKYEYsFhYrSwgQA-" ext:score="100">
            <title>Stupid Doo Doo Dumb</title>
            <artist>Mac Dre</artist>
            <barcode>618763105025</barcode>
            <comment>CD Baby id:macdremusic5</comment>
            <track-list count="15"/>
        </cdstub>
    </cdstub-list>
</metadata>

#### Json
{
    "created": "2017-02-14T11:00:32.046Z",
    "count": 53,
    "offset": 0,
    "cdstubs": [
        {
            "id": "NKpg6j_S6swmiKYEYsFhYrSwgQA-",
            "score": "100",
            "count": 15,
            "title": "Stupid Doo Doo Dumb",
            "artist": "Mac Dre",
            "barcode": "618763105025",
            "comment": "CD Baby id:macdremusic5"
        }
    ]
}

## Event

#### Example
https://musicbrainz.org/ws/2/event/?query=unique

#### Search Fields
The Event index contains the following fields you can search
| Field | Description
| alias | (part of) any alias attached to the artist (diacritics are ignored)
| aid | the MBID of an area related to the event
| area | (part of) the name of an area related to the event
| arid | the MBID of an artist related to the event
| artist | (part of) the name of an artist related to the event
| begin | the event's begin date (e.g. "1980-01-22")
| comment | (part of) the artist's disambiguation comment
| end | the event's end date (e.g. "1980-01-22")
| ended | a boolean flag (true/false) indicating whether or not the event has an end date set
| eid | the MBID of the event
| event | (part of) the event's name (diacritics are ignored)
| eventaccent | (part of) the event's name (with the specified diacritics)
| pid | the MBID of a place related to the event
| place | (part of) the name of a place related to the event
| tag | (part of) a tag attached to the event
| type | the event's type
If you don't specify a field, the terms will be searched for in the alias, artist and event fields.

### Xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<metadata created="2017-03-12T18:04:50.830Z" xmlns="http://musicbrainz.org/ns/mmd-2.0#" xmlns:ext="http://musicbrainz.org/ns/ext#-2.0">
  <event-list count="1" offset="0">
    <event id="bc58d881-0b8e-45de-bee7-5d4a03d71190" type="Concert" ext:score="100">
      <name>Dominique A at Le Lieu Unique, April 2012</name>
      <life-span>
        <begin>2012-04-12</begin>
        <end>2012-04-12</end>
      </life-span>
      <time>20:30:00</time>
      <relation-list target-type="artist">
        <relation type="main performer">
          <direction>backward</direction>
          <artist id="8ae5648d-d9b7-4083-b538-17f71672990f">
            <name>Dominique A</name>
            <sort-name>A, Dominique</sort-name>
          </artist>
        </relation>
      </relation-list>
      <relation-list target-type="place">
        <relation type="held at">
          <direction>backward</direction>
          <place id="ab7fd308-da33-4d01-8bdb-d8238bb3842a">
            <name>Le Lieu Unique</name>
          </place>
        </relation>
      </relation-list>
    </event>
  </event-list>
</metadata>

### Json
{
  "created": "2017-03-12T18:04:50.83Z",
  "count": 1,
  "offset": 0,
  "events": [
    {
      "id": "bc58d881-0b8e-45de-bee7-5d4a03d71190",
      "type": "Concert",
      "score": "100",
      "name": "Dominique A at Le Lieu Unique, April 2012",
      "life-span": {
        "begin": "2012-04-12",
        "end": "2012-04-12"
      },
      "time": "20:30:00",
      "relations": [
        {
          "type": "main performer",
          "direction": "backward",
          "artist": {
            "id": "8ae5648d-d9b7-4083-b538-17f71672990f",
            "name": "Dominique A",
            "sort-name": "A, Dominique"
          }
        },
        {
          "type": "held at",
          "direction": "backward",
          "place": {
            "id": "ab7fd308-da33-4d01-8bdb-d8238bb3842a",
            "name": "Le Lieu Unique"
          }
        }
      ]
    }
  ]
}

## Instrument

#### Example
https://musicbrainz.org/ws/2/instrument/?query=Nose

#### Search Fields
The instrument index contains these fields you can search:
| Field | Description
| alias | (part of) any alias attached to the instrument (diacritics are ignored)
| comment | (part of) the instrument's disambiguation comment
| description | (part of) the description of the instrument (in English)
| iid | the MBID of the instrument
| instrument | (part of) the instrument's name (diacritics are ignored)
| instrumentaccent | (part of) the instrument's name (with the specified diacritics)
| tag | (part of) a tag attached to the instrument
| type | the instrument's type
If you don't specify a field, the terms will be searched for in the alias, description and instrument fields.

### Xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<metadata created="2017-03-12T18:06:29.271Z" xmlns="http://musicbrainz.org/ns/mmd-2.0#" xmlns:ext="http://musicbrainz.org/ns/ext#-2.0">
  <instrument-list count="2" offset="0">
    <instrument id="e2e7de25-20d5-4c3f-8a23-2b99d3e44730" type="Wind instrument" ext:score="100">
      <name>nose flute</name>
      <description>The nose flute is a flute played by the nose commonly found in countries in and around the Pacific.</description>
      <alias-list>
        <alias locale="es" sort-name="flauta nasal" type="Instrument name" primary="primary">flauta nasal</alias>
        <alias locale="fr" sort-name="flûte à nez" type="Instrument name" primary="primary">flûte à nez</alias>
        <alias locale="de" sort-name="Nasenflöte (traditionell)" type="Instrument name" primary="primary">Nasenflöte (traditionell)</alias>
        <alias locale="fi" sort-name="nenähuilu" type="Instrument name" primary="primary">nenähuilu</alias>
        <alias locale="nl" sort-name="neusfluit" type="Instrument name" primary="primary">neusfluit</alias>
        <alias locale="et" sort-name="ninaflööt" type="Instrument name" primary="primary">ninaflööt</alias>
        <alias locale="en" sort-name="nose flute" type="Instrument name" primary="primary">nose flute</alias>
        <alias locale="ja" sort-name="鼻笛" type="Instrument name" primary="primary">鼻笛</alias>
      </alias-list>
    </instrument>
    <instrument id="3d082a7d-e8d9-4c7b-b8d0-513883a7d586" type="Wind instrument" ext:score="100">
      <name>nose whistle</name>
      <description>The nose whistle (also known as the Humanatone) is a simple instrument played with the nose. The stream of air is directed over an edge in the instrument and the frequency of the notes produced is controlled by the volume of air.</description>
      <alias-list>
        <alias sort-name="Humanatone">Humanatone</alias>
        <alias locale="de" sort-name="Nasenflöte" type="Instrument name" primary="primary">Nasenflöte</alias>
        <alias locale="nl" sort-name="neusfluitje" type="Instrument name" primary="primary">neusfluitje</alias>
        <alias locale="et" sort-name="ninavile" type="Instrument name" primary="primary">ninavile</alias>
        <alias locale="en" sort-name="nose whistle" type="Instrument name" primary="primary">nose whistle</alias>
        <alias locale="fr" sort-name="sifflet à nez" type="Instrument name" primary="primary">sifflet à nez</alias>
        <alias locale="ja" sort-name="鼻ホイッスル" type="Instrument name" primary="primary">鼻ホイッスル</alias>
      </alias-list>
    </instrument>
  </instrument-list>
</metadata>

### Json
{
  "created": "2017-03-12T18:06:29.271Z",
  "count": 2,
  "offset": 0,
  "instruments": [
    {
      "id": "e2e7de25-20d5-4c3f-8a23-2b99d3e44730",
      "type": "Wind instrument",
      "score": "100",
      "name": "nose flute",
      "description": "The nose flute is a flute played by the nose commonly found in countries in and around the Pacific.",
      "aliases": [
        {
          "sort-name": "flauta nasal",
          "name": "flauta nasal",
          "locale": "es",
          "type": "Instrument name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "flûte à nez",
          "name": "flûte à nez",
          "locale": "fr",
          "type": "Instrument name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Nasenflöte (traditionell)",
          "name": "Nasenflöte (traditionell)",
          "locale": "de",
          "type": "Instrument name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "nenähuilu",
          "name": "nenähuilu",
          "locale": "fi",
          "type": "Instrument name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "neusfluit",
          "name": "neusfluit",
          "locale": "nl",
          "type": "Instrument name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "ninaflööt",
          "name": "ninaflööt",
          "locale": "et",
          "type": "Instrument name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "nose flute",
          "name": "nose flute",
          "locale": "en",
          "type": "Instrument name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "鼻笛",
          "name": "鼻笛",
          "locale": "ja",
          "type": "Instrument name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        }
      ]
    },
    {
      "id": "3d082a7d-e8d9-4c7b-b8d0-513883a7d586",
      "type": "Wind instrument",
      "score": "100",
      "name": "nose whistle",
      "description": "The nose whistle (also known as the Humanatone) is a simple instrument played with the nose. The stream of air is directed over an edge in the instrument and the frequency of the notes produced is controlled by the volume of air.",
      "aliases": [
        {
          "sort-name": "Humanatone",
          "name": "Humanatone",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Nasenflöte",
          "name": "Nasenflöte",
          "locale": "de",
          "type": "Instrument name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "neusfluitje",
          "name": "neusfluitje",
          "locale": "nl",
          "type": "Instrument name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "ninavile",
          "name": "ninavile",
          "locale": "et",
          "type": "Instrument name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "nose whistle",
          "name": "nose whistle",
          "locale": "en",
          "type": "Instrument name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "sifflet à nez",
          "name": "sifflet à nez",
          "locale": "fr",
          "type": "Instrument name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "鼻ホイッスル",
          "name": "鼻ホイッスル",
          "locale": "ja",
          "type": "Instrument name",
          "primary": true,
          "begin-date": null,
          "end-date": null
        }
      ]
    }
  ]
}

## Label

#### Example
http://musicbrainz.org/ws/2/label/?query=%22Devil's%20Records%22

#### Search Fields
The Label index contains the following fields you can search
| Field | Description
| alias | (part of) any alias attached to the label (diacritics are ignored)
| area | (part of) the name of the label's main associated area
| begin | the label's begin date (e.g. "1980-01-22")
| code | the label code for the label (only the numbers, without "LC")
| comment | (part of) the label's disambiguation comment
| country | the 2-letter code (ISO 3166-1 alpha-2) for the label's associated country
| end | the label's end date (e.g. "1980-01-22")
| ended | a boolean flag (true/false) indicating whether or not the label has ended (is dissolved)
| ipi | an IPI code associated with the label
| isni | an ISNI code associated with the label
| label | (part of) the label's name (diacritics are ignored)
| labelaccent | (part of) the label's name (with the specified diacritics)
| laid | the label's MBID
| release_count | the amount of releases related to the label
| sortname | equivalent to name (labels no longer have separate sort names)
| tag | (part of) a tag attached to the label
| type | the label's type
If you don't specify a field, the terms will be searched for in the alias and label fields.

#### Xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<metadata created="2017-03-12T16:59:29.160Z" xmlns="http://musicbrainz.org/ns/mmd-2.0#" xmlns:ext="http://musicbrainz.org/ns/ext#-2.0">
  <label-list count="1" offset="0">
    <label id="d2c296e3-10a4-4ba9-97b9-5620ff8a3ce0" type="Original Production" ext:score="100">
      <name>Devil's Records</name>
      <sort-name>Devil's Records</sort-name>
      <country>FR</country>
      <area id="08310658-51eb-3801-80de-5a0739207115">
        <name>France</name>
        <sort-name>France</sort-name>
      </area>
      <life-span>
        <ended>false</ended>
      </life-span>
      <alias-list>
        <alias sort-name="Devil Records">Devil Records</alias>
        <alias sort-name="Devils Records">Devils Records</alias>
      </alias-list>
    </label>
  </label-list>
</metadata>

#### Json
{
  "created": "2017-03-12T17:31:38.969Z",
  "count": 1,
  "offset": 0,
  "labels": [
    {
      "id": "d2c296e3-10a4-4ba9-97b9-5620ff8a3ce0",
      "type": "Original Production",
      "score": "100",
      "name": "Devil's Records",
      "sort-name": "Devil's Records",
      "country": "FR",
      "area": {
        "id": "08310658-51eb-3801-80de-5a0739207115",
        "name": "France",
        "sort-name": "France"
      },
      "life-span": {
        "ended": null
      },
      "aliases": [
        {
          "sort-name": "Devil Records",
          "name": "Devil Records",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        },
        {
          "sort-name": "Devils Records",
          "name": "Devils Records",
          "locale": null,
          "type": null,
          "primary": null,
          "begin-date": null,
          "end-date": null
        }
      ]
    }
  ]
}

## Place

#### Example
http://musicbrainz.org/ws/2/place/?query=chipping

#### Search Fields
The Place index contains the following fields you can search
| Field | Description
| address | (part of) the physical address for this place
| alias | (part of) any alias attached to the place (diacritics are ignored)
| area | (part of) the name of the place's main associated area
| begin | the place's begin date (e.g. "1980-01-22")
| comment | (part of) the place's disambiguation comment
| end | the place's end date (e.g. "1980-01-22")
| ended | a boolean flag (true/false) indicating whether or not the place has ended (is closed)
| lat | the (WGS 84) latitude of the place's coordinates (e.g. "58.388226")
| long | the (WGS 84) longitude of the place's coordinates (e.g. "26.702817")
| place | (part of) the place's name (diacritics are ignored)
| placeaccent | (part of) the place's name (with the specified diacritics)
| pid | the place's MBID
| type | the place's type
If you don't specify a field, the terms will be searched for in the address, alias, area and place fields.

#### Xml
<metadata created="2015-02-02T17:29:02.301Z">
    <place-list count="1" offset="0">
        <place id="d1ab65f8-d082-492a-bd70-ce375548dabf" type="Studio" ext:score="100">
            <name>Chipping Norton Recording Studios</name>
            <address>28–30 New Street, Chipping Norton</address>
            <area id="44e5e20e-8fbc-4b07-b3f2-22f2199186fd">
                <name>Oxfordshire</name>
                <sort-name>Oxfordshire</sort-name>
            </area>
        <life-span>
            <begin>1971</begin>
            <end>1999-10</end>
            <ended>true</ended>
        </life-span>
        </place>
    </place-list>
</metadata>

#### Json
{
  "created": "2017-03-12T16:59:39.959Z",
  "count": 1,
  "offset": 0,
  "places": [
    {
      "id": "d1ab65f8-d082-492a-bd70-ce375548dabf",
      "type": "Studio",
      "score": "100",
      "name": "Chipping Norton Recording Studios",
      "address": "28–30 New Street, Chipping Norton",
      "coordinates": {
        "latitude": "51.9414",
        "longitude": "-1.548"
      },
      "area": {
        "id": "716234d3-b8ed-45ac-8983-e7219eb85956",
        "name": "Chipping Norton",
        "sort-name": "Chipping Norton"
      },
      "life-span": {
        "begin": "1971",
        "end": "1999-10",
        "ended": true
      }
    }
  ]
}

## Recording

#### Example
http://musicbrainz.org/ws/2/recording/?query=isrc:GBAHT1600302

#### Search Fields
The Recording index contains the following fields you can search
| Field | Description
| alias | (part of) any alias attached to the recording (diacritics are ignored)
| arid | the MBID of any of the recording artists
| artist | (part of) the combined credited artist name for the recording, including join phrases (e.g. "Artist X feat.")
| artistname | (part of) the name of any of the recording artists
| comment | (part of) the recording's disambiguation comment
| country | the 2-letter code (ISO 3166-1 alpha-2) for the country any release of this recording was released in
| creditname | (part of) the credited name of any of the recording artists on this particular recording
| date | the release date of any release including this recording (e.g. "1980-01-22")
| dur | the recording duration in milliseconds
| firstreleasedate | the release date of the earliest release including this recording (e.g. "1980-01-22")
| format | the format of any medium including this recording (insensitive to case, spaces, and separators)
| isrc | any ISRC associated to the recording
| number | the free-text number of the track on any medium including this recording (e.g. "A4")
| position | the position inside its release of any medium including this recording (starts at 1)
| primarytype | the primary type of any release group including this recording
| qdur | the recording duration, quantized (duration in milliseconds / 2000)
| recording | (part of) the recording's name, or the name of a track connected to this recording (diacritics are ignored)
| recordingaccent | (part of) the recordings's name, or the name of a track connected to this recording (with the specified diacritics)
| reid | the MBID of any release including this recording
| release | (part of) the name of any release including this recording
| rgid | the MBID of any release group including this recording
| rid | the recording's MBID
| secondarytype | any of the secondary types of any release group including this recording
| status | the status of any release including this recording
| tag | (part of) a tag attached to the recording
| tid | the MBID of a track connected to this recording
| tnum | the position of the track on any medium including this recording (starts at 1, pre-gaps at 0)
| tracks | the number of tracks on any medium including this recording
| tracksrelease | the number of tracks on any release (as a whole) including this recording
| type | legacy release group type field that predates the ability to set multiple types (see calculation code)
| video | a boolean flag (true/false) indicating whether or not the recording is a video recording
If you don't specify a field, the terms will be searched for in the recording field.

#### Xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<metadata created="2017-02-23T14:31:36.889Z" xmlns="http://musicbrainz.org/ns/mmd-2.0#" xmlns:ext="http://musicbrainz.org/ns/ext#-2.0">
  <recording-list count="1" offset="0">
    <recording id="026fa041-3917-4c73-9079-ed16e36f20f8" ext:score="100">
      <title>Blow Your Mind (Mwah)</title>
      <length>178000</length>
      <artist-credit id="4af83e24-f886-35c8-831f-5dde0163a6a0">
        <name-credit>
          <artist id="6f1a58bf-9b1b-49cf-a44a-6cefad7ae04f">
            <name>Dua Lipa</name>
            <sort-name>Lipa, Dua</sort-name>
          </artist>
        </name-credit>
      </artist-credit>
      <first-release-date>2016-08-26</first-release-date>
      <release-list>
        <release id="383be31c-37a0-4e08-8cda-cbcbbc587ae5">
          <title>Blow Your Mind (Mwah)</title>
          <status id="4e304316-386d-3409-af2e-78857eec5cfe">Official</status>
          <release-group id="4a45bfa5-eb1e-49eb-a20c-1021389b2121" type="Single">
            <primary-type>Single</primary-type>
          </release-group>
          <date>2016-08-26</date>
          <country>XW</country>
          <release-event-list>
            <release-event>
              <date>2016-08-26</date>
              <area id="525d4e18-3d00-31b9-a58b-a146a916de8f">
                <name>[Worldwide]</name>
                <sort-name>[Worldwide]</sort-name>
                <iso-3166-1-code-list>
                  <iso-3166-1-code>XW</iso-3166-1-code>
                </iso-3166-1-code-list>
              </area>
            </release-event>
          </release-event-list>
          <medium-list>
            <track-count>1</track-count>
            <medium>
              <position>1</position>
              <format>Digital Media</format>
              <track-list count="1" offset="0">
                <track id="0ef6e647-4aeb-438e-8c8a-50c22c511203">
                  <number>1</number>
                  <title>Blow Your Mind (Mwah)</title>
                  <length>179000</length>
                </track>
              </track-list>
            </medium>
          </medium-list>
        </release>
        <release id="8bd42e63-46cb-43e3-8294-c9c3b9793581">
          <title>Now That’s What I Call Music! 95</title>
          <status id="4e304316-386d-3409-af2e-78857eec5cfe">Official</status>
          <artist-credit id="949a7fd5-fe73-3e8f-922e-01ff4ca958f7">
            <name-credit>
              <artist id="89ad4ac3-39f7-470e-963a-56509c546377">
                <name>Various Artists</name>
                <sort-name>Various Artists</sort-name>
              </artist>
            </name-credit>
          </artist-credit>
          <release-group id="071a007b-b9cf-4e22-8646-03c30fc8dd87" type="Compilation">
            <primary-type>Album</primary-type>
            <secondary-type-list>
              <secondary-type>Compilation</secondary-type>
            </secondary-type-list>
          </release-group>
          <date>2016-11-18</date>
          <country>GB</country>
          <release-event-list>
            <release-event>
              <date>2016-11-18</date>
              <area id="8a754a16-0027-3a29-b6d7-2b40ea0481ed">
                <name>United Kingdom</name>
                <sort-name>United Kingdom</sort-name>
                <iso-3166-1-code-list>
                  <iso-3166-1-code>GB</iso-3166-1-code>
                </iso-3166-1-code-list>
              </area>
            </release-event>
          </release-event-list>
          <medium-list>
            <track-count>45</track-count>
            <medium>
              <position>1</position>
              <format>Digital Media</format>
              <track-list count="45" offset="35">
                <track id="e43cfb2f-fdd3-40a7-9396-25c9435ca8cb">
                  <number>36</number>
                  <title>Blow Your Mind (Mwah)</title>
                  <length>178000</length>
                </track>
              </track-list>
            </medium>
          </medium-list>
        </release>
        <release id="72a240b0-ca08-4d35-a15d-c1eded21c0ce">
          <title>Now That’s What I Call Music! 95</title>
          <status id="4e304316-386d-3409-af2e-78857eec5cfe">Official</status>
          <artist-credit id="949a7fd5-fe73-3e8f-922e-01ff4ca958f7">
            <name-credit>
              <artist id="89ad4ac3-39f7-470e-963a-56509c546377">
                <name>Various Artists</name>
                <sort-name>Various Artists</sort-name>
              </artist>
            </name-credit>
          </artist-credit>
          <release-group id="071a007b-b9cf-4e22-8646-03c30fc8dd87" type="Compilation">
            <primary-type>Album</primary-type>
            <secondary-type-list>
              <secondary-type>Compilation</secondary-type>
            </secondary-type-list>
          </release-group>
          <date>2016-11-18</date>
          <country>GB</country>
          <release-event-list>
            <release-event>
              <date>2016-11-18</date>
              <area id="8a754a16-0027-3a29-b6d7-2b40ea0481ed">
                <name>United Kingdom</name>
                <sort-name>United Kingdom</sort-name>
                <iso-3166-1-code-list>
                  <iso-3166-1-code>GB</iso-3166-1-code>
                </iso-3166-1-code-list>
              </area>
            </release-event>
          </release-event-list>
          <medium-list>
            <track-count>45</track-count>
            <medium>
              <position>2</position>
              <format>CD</format>
              <track-list count="24" offset="14">
                <track id="8c193afa-a867-46fb-8745-5168a8e16a75">
                  <number>15</number>
                  <title>Blow Your Mind (Mwah)</title>
                  <length>178213</length>
                </track>
              </track-list>
            </medium>
          </medium-list>
        </release>
        <release id="6313b666-6042-486b-b2aa-614e7542ff68">
          <title>Life Is Music 2016.2</title>
          <status id="4e304316-386d-3409-af2e-78857eec5cfe">Official</status>
          <artist-credit id="949a7fd5-fe73-3e8f-922e-01ff4ca958f7">
            <name-credit>
              <artist id="89ad4ac3-39f7-470e-963a-56509c546377">
                <name>Various Artists</name>
                <sort-name>Various Artists</sort-name>
              </artist>
            </name-credit>
          </artist-credit>
          <release-group id="406d765d-c5ca-43e9-b268-a33878927ff5" type="Compilation">
            <primary-type>Album</primary-type>
            <secondary-type-list>
              <secondary-type>Compilation</secondary-type>
            </secondary-type-list>
          </release-group>
          <date>2016-12-02</date>
          <country>BE</country>
          <release-event-list>
            <release-event>
              <date>2016-12-02</date>
              <area id="5b8a5ee5-0bb3-34cf-9a75-c27c44e341fc">
                <name>Belgium</name>
                <sort-name>Belgium</sort-name>
                <iso-3166-1-code-list>
                  <iso-3166-1-code>BE</iso-3166-1-code>
                </iso-3166-1-code-list>
              </area>
            </release-event>
          </release-event-list>
          <medium-list>
            <track-count>39</track-count>
            <medium>
              <position>1</position>
              <format>CD</format>
              <track-list count="20" offset="7">
                <track id="7e93e73c-e8f2-4218-af5e-baae4ce98882">
                  <number>8</number>
                  <title>Blow Your Mind (Mwah)</title>
                  <length>177266</length>
                </track>
              </track-list>
            </medium>
          </medium-list>
        </release>
        <release id="b3a2bca0-faec-4e67-8cf3-fd3d01755a2d">
          <title>Hits 2016</title>
          <status id="4e304316-386d-3409-af2e-78857eec5cfe">Official</status>
          <artist-credit id="949a7fd5-fe73-3e8f-922e-01ff4ca958f7">
            <name-credit>
              <artist id="89ad4ac3-39f7-470e-963a-56509c546377">
                <name>Various Artists</name>
                <sort-name>Various Artists</sort-name>
              </artist>
            </name-credit>
          </artist-credit>
          <release-group id="7678ff0a-9446-4d5f-b46e-56c84fc68654" type="Compilation">
            <primary-type>Album</primary-type>
            <secondary-type-list>
              <secondary-type>Compilation</secondary-type>
            </secondary-type-list>
          </release-group>
          <date>2016-12-23</date>
          <country>MX</country>
          <release-event-list>
            <release-event>
              <date>2016-12-23</date>
              <area id="3e08b2cd-69f3-317c-b1e4-e71be581839e">
                <name>Mexico</name>
                <sort-name>Mexico</sort-name>
                <iso-3166-1-code-list>
                  <iso-3166-1-code>MX</iso-3166-1-code>
                </iso-3166-1-code-list>
              </area>
            </release-event>
          </release-event-list>
          <medium-list>
            <track-count>23</track-count>
            <medium>
              <position>1</position>
              <format>Digital Media</format>
              <track-list count="23" offset="22">
                <track id="3b466997-8bda-410f-82aa-02b703c931c5">
                  <number>23</number>
                  <title>Blow Your Mind (Mwah)</title>
                  <length>178583</length>
                </track>
              </track-list>
            </medium>
          </medium-list>
        </release>
        <release id="d02cce98-98fe-430c-b3c9-951c94f4fb1d">
          <title>Now That's What I Call Music! 95</title>
          <status id="4e304316-386d-3409-af2e-78857eec5cfe">Official</status>
          <artist-credit id="949a7fd5-fe73-3e8f-922e-01ff4ca958f7">
            <name-credit>
              <artist id="89ad4ac3-39f7-470e-963a-56509c546377">
                <name>Various Artists</name>
                <sort-name>Various Artists</sort-name>
              </artist>
            </name-credit>
          </artist-credit>
          <release-group id="071a007b-b9cf-4e22-8646-03c30fc8dd87" type="Compilation">
            <primary-type>Album</primary-type>
            <secondary-type-list>
              <secondary-type>Compilation</secondary-type>
            </secondary-type-list>
          </release-group>
          <date>2016-11-18</date>
          <country>GB</country>
          <release-event-list>
            <release-event>
              <date>2016-11-18</date>
              <area id="8a754a16-0027-3a29-b6d7-2b40ea0481ed">
                <name>United Kingdom</name>
                <sort-name>United Kingdom</sort-name>
                <iso-3166-1-code-list>
                  <iso-3166-1-code>GB</iso-3166-1-code>
                </iso-3166-1-code-list>
              </area>
            </release-event>
          </release-event-list>
          <medium-list>
            <track-count>45</track-count>
            <medium>
              <position>2</position>
              <format>CD</format>
              <track-list count="24" offset="14">
                <track id="4ae11ffe-5ac8-42ae-a321-1535136ff05c">
                  <number>15</number>
                  <title>Blow Your Mind (Mwah)</title>
                  <length>178213</length>
                </track>
              </track-list>
            </medium>
          </medium-list>
        </release>
        <release id="5496dc5f-a282-422e-b7c6-78575e5f7944">
          <title>Dua Lipa (Deluxe)</title>
          <status id="518ffc83-5cde-34df-8627-81bff5093d92">Promotion</status>
          <release-group id="abbc4905-c25f-4c67-8e2d-19329ec48b1f" type="Album">
            <primary-type>Album</primary-type>
          </release-group>
          <date>2017-06-02</date>
          <country>XW</country>
          <release-event-list>
            <release-event>
              <date>2017-06-02</date>
              <area id="525d4e18-3d00-31b9-a58b-a146a916de8f">
                <name>[Worldwide]</name>
                <sort-name>[Worldwide]</sort-name>
                <iso-3166-1-code-list>
                  <iso-3166-1-code>XW</iso-3166-1-code>
                </iso-3166-1-code-list>
              </area>
            </release-event>
          </release-event-list>
          <medium-list>
            <track-count>17</track-count>
            <medium>
              <position>1</position>
              <format>Digital Media</format>
              <track-list count="17" offset="5">
                <track id="a2fcb379-7638-4f27-b2e4-5242a69ed09c">
                  <number>6</number>
                  <title>Blow Your Mind (Mwah)</title>
                  <length>178000</length>
                </track>
              </track-list>
            </medium>
          </medium-list>
        </release>
        <release id="eb66eaa0-acb6-4317-91ea-ff65b7813ec0">
          <title>Dua Lipa</title>
          <status id="518ffc83-5cde-34df-8627-81bff5093d92">Promotion</status>
          <release-group id="abbc4905-c25f-4c67-8e2d-19329ec48b1f" type="Album">
            <primary-type>Album</primary-type>
          </release-group>
          <date>2017-06-02</date>
          <country>XW</country>
          <release-event-list>
            <release-event>
              <date>2017-06-02</date>
              <area id="525d4e18-3d00-31b9-a58b-a146a916de8f">
                <name>[Worldwide]</name>
                <sort-name>[Worldwide]</sort-name>
                <iso-3166-1-code-list>
                  <iso-3166-1-code>XW</iso-3166-1-code>
                </iso-3166-1-code-list>
              </area>
            </release-event>
          </release-event-list>
          <medium-list>
            <track-count>12</track-count>
            <medium>
              <position>1</position>
              <format>Digital Media</format>
              <track-list count="12" offset="5">
                <track id="b74b2a35-900a-446c-8a63-7a5b01c82a5e">
                  <number>6</number>
                  <title>Blow Your Mind (Mwah)</title>
                  <length>178000</length>
                </track>
              </track-list>
            </medium>
          </medium-list>
        </release>
      </release-list>
      <isrc-list>
        <isrc id="GBAHT1600302"/>
      </isrc-list>
      <tag-list>
        <tag count="1">
          <name>electropop</name>
        </tag>
        <tag count="1">
          <name>dance-pop</name>
        </tag>
        <tag count="1">
          <name>contemporary r&b</name>
        </tag>
      </tag-list>
    </recording>
  </recording-list>
</metadata>
Note that if the recording belongs to a release that is a multiple-artist compilation then the release data includes an artist credit.

#### Json
{
  "created": "2017-02-23T14:31:36.889Z",
  "count": 1,
  "offset": 0,
  "recordings": [
    {
      "id": "026fa041-3917-4c73-9079-ed16e36f20f8",
      "score": "100",
      "title": "Blow Your Mind (Mwah)",
      "length": 178000,
      "video": null,
      "artist-credit": [
        {
          "artist": {
            "id": "6f1a58bf-9b1b-49cf-a44a-6cefad7ae04f",
            "name": "Dua Lipa",
            "sort-name": "Lipa, Dua"
          }
        }
      ],
      "artist-credit-id": "4af83e24-f886-35c8-831f-5dde0163a6a0",
      "first-release-date": "2016-08-26",
      "releases": [
        {
          "id": "383be31c-37a0-4e08-8cda-cbcbbc587ae5",
          "title": "Blow Your Mind (Mwah)",
          "status-id": "4e304316-386d-3409-af2e-78857eec5cfe",
          "status": "Official",
          "release-group": {
            "id": "4a45bfa5-eb1e-49eb-a20c-1021389b2121",
            "primary-type": "Single"
          },
          "date": "2016-08-26",
          "country": "XW",
          "release-events": [
            {
              "date": "2016-08-26",
              "area": {
                "id": "525d4e18-3d00-31b9-a58b-a146a916de8f",
                "name": "[Worldwide]",
                "sort-name": "[Worldwide]",
                "iso-3166-1-codes": [
                  "XW"
                ]
              }
            }
          ],
          "track-count": 1,
          "media": [
            {
              "position": 1,
              "format": "Digital Media",
              "track": [
                {
                  "id": "0ef6e647-4aeb-438e-8c8a-50c22c511203",
                  "number": "1",
                  "title": "Blow Your Mind (Mwah)",
                  "length": 179000
                }
              ],
              "track-count": 1,
              "track-offset": 0
            }
          ]
        },
        {
          "id": "8bd42e63-46cb-43e3-8294-c9c3b9793581",
          "title": "Now That’s What I Call Music! 95",
          "status-id": "4e304316-386d-3409-af2e-78857eec5cfe",
          "status": "Official",
          "artist-credit": [
            {
              "artist": {
                "id": "89ad4ac3-39f7-470e-963a-56509c546377",
                "name": "Various Artists",
                "sort-name": "Various Artists"
              }
            }
          ],
          "artist-credit-id": "949a7fd5-fe73-3e8f-922e-01ff4ca958f7",
          "release-group": {
            "id": "071a007b-b9cf-4e22-8646-03c30fc8dd87",
            "primary-type": "Album",
            "secondary-types": [
              "Compilation"
            ]
          },
          "date": "2016-11-18",
          "country": "GB",
          "release-events": [
            {
              "date": "2016-11-18",
              "area": {
                "id": "8a754a16-0027-3a29-b6d7-2b40ea0481ed",
                "name": "United Kingdom",
                "sort-name": "United Kingdom",
                "iso-3166-1-codes": [
                  "GB"
                ]
              }
            }
          ],
          "track-count": 45,
          "media": [
            {
              "position": 1,
              "format": "Digital Media",
              "track": [
                {
                  "id": "e43cfb2f-fdd3-40a7-9396-25c9435ca8cb",
                  "number": "36",
                  "title": "Blow Your Mind (Mwah)",
                  "length": 178000
                }
              ],
              "track-count": 45,
              "track-offset": 35
            }
          ]
        },
        {
          "id": "72a240b0-ca08-4d35-a15d-c1eded21c0ce",
          "title": "Now That’s What I Call Music! 95",
          "status-id": "4e304316-386d-3409-af2e-78857eec5cfe",
          "status": "Official",
          "artist-credit": [
            {
              "artist": {
                "id": "89ad4ac3-39f7-470e-963a-56509c546377",
                "name": "Various Artists",
                "sort-name": "Various Artists"
              }
            }
          ],
          "artist-credit-id": "949a7fd5-fe73-3e8f-922e-01ff4ca958f7",
          "release-group": {
            "id": "071a007b-b9cf-4e22-8646-03c30fc8dd87",
            "primary-type": "Album",
            "secondary-types": [
              "Compilation"
            ]
          },
          "date": "2016-11-18",
          "country": "GB",
          "release-events": [
            {
              "date": "2016-11-18",
              "area": {
                "id": "8a754a16-0027-3a29-b6d7-2b40ea0481ed",
                "name": "United Kingdom",
                "sort-name": "United Kingdom",
                "iso-3166-1-codes": [
                  "GB"
                ]
              }
            }
          ],
          "track-count": 45,
          "media": [
            {
              "position": 2,
              "format": "CD",
              "track": [
                {
                  "id": "8c193afa-a867-46fb-8745-5168a8e16a75",
                  "number": "15",
                  "title": "Blow Your Mind (Mwah)",
                  "length": 178213
                }
              ],
              "track-count": 24,
              "track-offset": 14
            }
          ]
        },
        {
          "id": "6313b666-6042-486b-b2aa-614e7542ff68",
          "title": "Life Is Music 2016.2",
          "status-id": "4e304316-386d-3409-af2e-78857eec5cfe",
          "status": "Official",
          "artist-credit": [
            {
              "artist": {
                "id": "89ad4ac3-39f7-470e-963a-56509c546377",
                "name": "Various Artists",
                "sort-name": "Various Artists"
              }
            }
          ],
          "artist-credit-id": "949a7fd5-fe73-3e8f-922e-01ff4ca958f7",
          "release-group": {
            "id": "406d765d-c5ca-43e9-b268-a33878927ff5",
            "primary-type": "Album",
            "secondary-types": [
              "Compilation"
            ]
          },
          "date": "2016-12-02",
          "country": "BE",
          "release-events": [
            {
              "date": "2016-12-02",
              "area": {
                "id": "5b8a5ee5-0bb3-34cf-9a75-c27c44e341fc",
                "name": "Belgium",
                "sort-name": "Belgium",
                "iso-3166-1-codes": [
                  "BE"
                ]
              }
            }
          ],
          "track-count": 39,
          "media": [
            {
              "position": 1,
              "format": "CD",
              "track": [
                {
                  "id": "7e93e73c-e8f2-4218-af5e-baae4ce98882",
                  "number": "8",
                  "title": "Blow Your Mind (Mwah)",
                  "length": 177266
                }
              ],
              "track-count": 20,
              "track-offset": 7
            }
          ]
        },
        {
          "id": "b3a2bca0-faec-4e67-8cf3-fd3d01755a2d",
          "title": "Hits 2016",
          "status-id": "4e304316-386d-3409-af2e-78857eec5cfe",
          "status": "Official",
          "artist-credit": [
            {
              "artist": {
                "id": "89ad4ac3-39f7-470e-963a-56509c546377",
                "name": "Various Artists",
                "sort-name": "Various Artists"
              }
            }
          ],
          "artist-credit-id": "949a7fd5-fe73-3e8f-922e-01ff4ca958f7",
          "release-group": {
            "id": "7678ff0a-9446-4d5f-b46e-56c84fc68654",
            "primary-type": "Album",
            "secondary-types": [
              "Compilation"
            ]
          },
          "date": "2016-12-23",
          "country": "MX",
          "release-events": [
            {
              "date": "2016-12-23",
              "area": {
                "id": "3e08b2cd-69f3-317c-b1e4-e71be581839e",
                "name": "Mexico",
                "sort-name": "Mexico",
                "iso-3166-1-codes": [
                  "MX"
                ]
              }
            }
          ],
          "track-count": 23,
          "media": [
            {
              "position": 1,
              "format": "Digital Media",
              "track": [
                {
                  "id": "3b466997-8bda-410f-82aa-02b703c931c5",
                  "number": "23",
                  "title": "Blow Your Mind (Mwah)",
                  "length": 178583
                }
              ],
              "track-count": 23,
              "track-offset": 22
            }
          ]
        },
        {
          "id": "d02cce98-98fe-430c-b3c9-951c94f4fb1d",
          "title": "Now That's What I Call Music! 95",
          "status-id": "4e304316-386d-3409-af2e-78857eec5cfe",
          "status": "Official",
          "artist-credit": [
            {
              "artist": {
                "id": "89ad4ac3-39f7-470e-963a-56509c546377",
                "name": "Various Artists",
                "sort-name": "Various Artists"
              }
            }
          ],
          "artist-credit-id": "949a7fd5-fe73-3e8f-922e-01ff4ca958f7",
          "release-group": {
            "id": "071a007b-b9cf-4e22-8646-03c30fc8dd87",
            "primary-type": "Album",
            "secondary-types": [
              "Compilation"
            ]
          },
          "date": "2016-11-18",
          "country": "GB",
          "release-events": [
            {
              "date": "2016-11-18",
              "area": {
                "id": "8a754a16-0027-3a29-b6d7-2b40ea0481ed",
                "name": "United Kingdom",
                "sort-name": "United Kingdom",
                "iso-3166-1-codes": [
                  "GB"
                ]
              }
            }
          ],
          "track-count": 45,
          "media": [
            {
              "position": 2,
              "format": "CD",
              "track": [
                {
                  "id": "4ae11ffe-5ac8-42ae-a321-1535136ff05c",
                  "number": "15",
                  "title": "Blow Your Mind (Mwah)",
                  "length": 178213
                }
              ],
              "track-count": 24,
              "track-offset": 14
            }
          ]
        },
        {
          "id": "5496dc5f-a282-422e-b7c6-78575e5f7944",
          "title": "Dua Lipa (Deluxe)",
          "status-id": "518ffc83-5cde-34df-8627-81bff5093d92",
          "status": "Promotion",
          "release-group": {
            "id": "abbc4905-c25f-4c67-8e2d-19329ec48b1f",
            "primary-type": "Album"
          },
          "date": "2017-06-02",
          "country": "XW",
          "release-events": [
            {
              "date": "2017-06-02",
              "area": {
                "id": "525d4e18-3d00-31b9-a58b-a146a916de8f",
                "name": "[Worldwide]",
                "sort-name": "[Worldwide]",
                "iso-3166-1-codes": [
                  "XW"
                ]
              }
            }
          ],
          "track-count": 17,
          "media": [
            {
              "position": 1,
              "format": "Digital Media",
              "track": [
                {
                  "id": "a2fcb379-7638-4f27-b2e4-5242a69ed09c",
                  "number": "6",
                  "title": "Blow Your Mind (Mwah)",
                  "length": 178000
                }
              ],
              "track-count": 17,
              "track-offset": 5
            }
          ]
        },
        {
          "id": "eb66eaa0-acb6-4317-91ea-ff65b7813ec0",
          "title": "Dua Lipa",
          "status-id": "518ffc83-5cde-34df-8627-81bff5093d92",
          "status": "Promotion",
          "release-group": {
            "id": "abbc4905-c25f-4c67-8e2d-19329ec48b1f",
            "primary-type": "Album"
          },
          "date": "2017-06-02",
          "country": "XW",
          "release-events": [
            {
              "date": "2017-06-02",
              "area": {
                "id": "525d4e18-3d00-31b9-a58b-a146a916de8f",
                "name": "[Worldwide]",
                "sort-name": "[Worldwide]",
                "iso-3166-1-codes": [
                  "XW"
                ]
              }
            }
          ],
          "track-count": 12,
          "media": [
            {
              "position": 1,
              "format": "Digital Media",
              "track": [
                {
                  "id": "b74b2a35-900a-446c-8a63-7a5b01c82a5e",
                  "number": "6",
                  "title": "Blow Your Mind (Mwah)",
                  "length": 178000
                }
              ],
              "track-count": 12,
              "track-offset": 5
            }
          ]
        }
      ],
      "isrcs": [
        {
          "id": "GBAHT1600302"
        },
        {
          "id": "GBAHT1600331"
        }
      ],
      "tags": [
        {
          "count": 1,
          "name": "electropop"
        },
        {
          "count": 1,
          "name": "dance-pop"
        },
        {
          "count": 1,
          "name": "contemporary r&b"
        }
      ]
    }
  ]
}

## Release Group

#### Example
http://musicbrainz.org/ws/2/release-group/?query=release:Tenance

#### Search Fields
The release group index contains the following fields you can search:
| Field | Description
| alias | (part of) any alias attached to the release group (diacritics are ignored)
| arid | the MBID of any of the release group artists
| artist | (part of) the combined credited artist name for the release group, including join phrases (e.g. "Artist X feat.")
| artistname | (part of) the name of any of the release group artists
| comment | (part of) the release group's disambiguation comment
| creditname | (part of) the credited name of any of the release group artists on this particular release group
| firstreleasedate | the release date of the earliest release in this release group (e.g. "1980-01-22")
| primarytype | the primary type of the release group
| reid | the MBID of any of the releases in the release group
| release | (part of) the title of any of the releases in the release group
| releasegroup | (part of) the release group's title (diacritics are ignored)
| releasegroupaccent | (part of) the release group's title (with the specified diacritics)
| releases | the number of releases in the release group
| rgid | the release group's MBID
| secondarytype | any of the secondary types of the release group
| status | the status of any of the releases in the release group
| tag | (part of) a tag attached to the release group
| type | legacy release group type field that predates the ability to set multiple types (see calculation code)
If you don't specify a field, the terms will be searched for in the releasegroup field.

#### Xml
<metadata xmlns="http://musicbrainz.org/ns/mmd-2.0#" xmlns:ext="http://musicbrainz.org/ns/ext#-2.0">
      <release-group-list offset="0" count="1">
          <release-group ext:score="100" type="Single" id="70664047-2545-4e46-b75f-4556f2a7b83e">
              <title>Main Tenance</title>
              <first-release-date>1998</first-release-date>
              <artist-credit id="ce1e40a1-048d-3ffb-afd7-c9d6eb6984c5">
                  <name-credit> 
                      <artist id="a8fa58d8-f60b-4b83-be7c-aea1af11596b">
                          <name>Fred Giannelli</name>
                          <sort-name>Giannelli, Fred</sort-name>
                          <disambiguation>US electronic artist</disambiguation>
                      </artist>
                  </name-credit>
              </artist-credit>
              <release-list count="1">
                  <release id="9168f4cc-a852-4ba5-bf85-602996625651">
                      <title>Main Tenance</title>
                  </release>
              </release-list>
          </release-group>
    </release-group-list>
</metadata>

#### Json
{
  "created": "2017-03-12T17:27:52.777Z",
  "count": 1,
  "offset": 0,
  "release-groups": [
    {
      "id": "70664047-2545-4e46-b75f-4556f2a7b83e",
      "score": "100",
      "count": 1,
      "title": "Main Tenance",
      "first-release-date": "1998",
      "primary-type": "Single",
      "artist-credit": [
        {
          "artist": {
            "id": "a8fa58d8-f60b-4b83-be7c-aea1af11596b",
            "name": "Fred Giannelli",
            "sort-name": "Giannelli, Fred",
            "disambiguation": "US electronic artist",
            "aliases": [
              {
                "sort-name": "Fred",
                "name": "Fred",
                "locale": null,
                "type": null,
                "primary": null,
                "begin-date": null,
                "end-date": null
              },
              {
                "sort-name": "Giannelli, Fred Domenic, II",
                "name": "Fred Domenic Giannelli II",
                "locale": null,
                "type": "Legal name",
                "primary": null,
                "begin-date": null,
                "end-date": null
              },
              {
                "sort-name": "Fred Gianelli",
                "name": "Fred Gianelli",
                "locale": null,
                "type": null,
                "primary": null,
                "begin-date": null,
                "end-date": null
              }
            ]
          }
        }
      ],
      "artist-credit-id": "ce1e40a1-048d-3ffb-afd7-c9d6eb6984c5",
      "releases": [
        {
          "id": "9168f4cc-a852-4ba5-bf85-602996625651",
          "title": "Main Tenance",
          "status": "Official"
        }
      ]
    }
  ]
}

## Release

#### Example
http://musicbrainz.org/ws/2/release/?query=release:Schneider%20AND%20Shake

#### Search Fields
The Release index contains the following fields you can search
| Field | Description
| alias | (part of) any alias attached to the release (diacritics are ignored)
| arid | the MBID of any of the release artists
| artist | (part of) the combined credited artist name for the release, including join phrases (e.g. "Artist X feat.")
| artistname | (part of) the name of any of the release artists
| asin | an Amazon ASIN for the release
| barcode | the barcode for the release
| catno | any catalog number for this release (insensitive to case, spaces, and separators)
| comment | (part of) the release's disambiguation comment
| country | the 2-letter code (ISO 3166-1 alpha-2) for any country the release was released in
| creditname | (part of) the credited name of any of the release artists on this particular release
| date | a release date for the release (e.g. "1980-01-22")
| discids | the total number of disc IDs attached to all mediums on the release
| discidsmedium | the number of disc IDs attached to any one medium on the release
| format | the format of any medium in the release (insensitive to case, spaces, and separators)
| laid | the MBID of any of the release labels
| label | (part of) the name of any of the release labels
| lang | the ISO 639-3 code for the release language
| mediumid | the MBID of any of the mediums in the release
| mediums | the number of mediums on the release
| packaging | the format of the release (insensitive to case, spaces, and separators)
| primarytype | the primary type of the release group for this release
| quality | the listed quality of the data for the release (2 for “high”, 1 for “normal”; cannot search for “low” at the moment; see the related bug report)
| reid | the release's MBID
| release | (part of) the release's title (diacritics are ignored)
| releaseaccent | (part of) the release's title (with the specified diacritics)
| rgid | the MBID of the release group for this release
| script | the ISO 15924 code for the release script
| secondarytype | any of the secondary types of the release group for this release
| status | the status of the release
| tag | (part of) a tag attached to the release
| tracks | the total number of tracks on the release
| tracksmedium | the number of tracks on any one medium on the release
| type | legacy release group type field that predates the ability to set multiple types (see calculation code)
If you don't specify a field, the terms will be searched for in the release field.

#### Xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<metadata created="2017-03-12T17:20:00.235Z" xmlns="http://musicbrainz.org/ns/mmd-2.0#" xmlns:ext="http://musicbrainz.org/ns/ext#-2.0">
  <release-list count="1" offset="0">
    <release id="62d1c4ef-fc00-37af-8df7-485f6a31fcc4" ext:score="100">
      <title>Fred Schneider & The Shake Society</title>
      <status id="4e304316-386d-3409-af2e-78857eec5cfe">Official</status>
      <packaging>Cardboard/Paper Sleeve</packaging>
      <text-representation>
        <language>eng</language>
        <script>Latn</script>
      </text-representation>
      <artist-credit id="04590110-2280-322a-a0c4-6d6bc8dc17e8">
        <name-credit>
          <artist id="43bcca8b-9edc-4997-8343-122350e790bf">
            <name>Fred Schneider</name>
            <sort-name>Schneider, Fred</sort-name>
            <alias-list>
              <alias sort-name="Schneider, Frederick William" type="Legal name">Frederick William Schneider</alias>
              <alias sort-name="Fred Schneider & the Shake Society">Fred Schneider & the Shake Society</alias>
            </alias-list>
          </artist>
        </name-credit>
      </artist-credit>
      <release-group id="0ef97d52-3f00-31bf-8413-f83ccb362675" type="Album">
        <primary-type>Album</primary-type>
      </release-group>
      <date>1984</date>
      <country>US</country>
      <release-event-list>
        <release-event>
          <date>1984</date>
          <area id="489ce91b-6658-3307-9877-795b68554c98">
            <name>United States</name>
            <sort-name>United States</sort-name>
            <iso-3166-1-code-list>
              <iso-3166-1-code>US</iso-3166-1-code>
            </iso-3166-1-code-list>
          </area>
        </release-event>
      </release-event-list>
      <barcode>07599251581</barcode>
      <label-info-list>
        <label-info>
          <catalog-number>1-25158</catalog-number>
          <label id="c595c289-47ce-4fba-b999-b87503e8cb71">
            <name>Warner Bros. Records</name>
          </label>
        </label-info>
      </label-info-list>
      <medium-list count="1">
        <track-count>9</track-count>
        <medium id="a6280646-e0be-4a35-8550-50bab13de3b8">
          <format>12" Vinyl</format>
          <disc-list count="0"/>
          <track-list count="9"/>
        </medium>
      </medium-list>
    </release>
  </release-list>
</metadata>

#### Json
{
  "created": "2017-03-12T17:20:00.235Z",
  "count": 1,
  "offset": 0,
  "releases": [
    {
      "id": "62d1c4ef-fc00-37af-8df7-485f6a31fcc4",
      "score": "100",
      "count": 1,
      "title": "Fred Schneider & The Shake Society",
      "status-id": "4e304316-386d-3409-af2e-78857eec5cfe",
      "status": "Official",
      "packaging": "Cardboard/Paper Sleeve",
      "text-representation": {
        "language": "eng",
        "script": "Latn"
      },
      "artist-credit": [
        {
          "artist": {
            "id": "43bcca8b-9edc-4997-8343-122350e790bf",
            "name": "Fred Schneider",
            "sort-name": "Schneider, Fred",
            "aliases": [
              {
                "sort-name": "Schneider, Frederick William",
                "name": "Frederick William Schneider",
                "locale": null,
                "type": "Legal name",
                "primary": null,
                "begin-date": null,
                "end-date": null
              },
              {
                "sort-name": "Fred Schneider & the Shake Society",
                "name": "Fred Schneider & the Shake Society",
                "locale": null,
                "type": null,
                "primary": null,
                "begin-date": null,
                "end-date": null
              }
            ]
          }
        }
      ],
      "artist-credit-id": "04590110-2280-322a-a0c4-6d6bc8dc17e8",
      "release-group": {
        "id": "0ef97d52-3f00-31bf-8413-f83ccb362675",
        "primary-type": "Album"
      },
      "date": "1984",
      "country": "US",
      "release-events": [
        {
          "date": "1984",
          "area": {
            "id": "489ce91b-6658-3307-9877-795b68554c98",
            "name": "United States",
            "sort-name": "United States",
            "iso-3166-1-codes": [
              "US"
            ]
          }
        }
      ],
      "barcode": "07599251581",
      "label-info": [
        {
          "catalog-number": "1-25158",
          "label": {
            "id": "c595c289-47ce-4fba-b999-b87503e8cb71",
            "name": "Warner Bros. Records"
          }
        }
      ],
      "track-count": 9,
      "media": [
        {
          "id": "a6280646-e0be-4a35-8550-50bab13de3b8",
          "format": "12\" Vinyl",
          "disc-count": 0,
          "track-count": 9
        }
      ]
    }
  ]
}

## Series

#### Example
https://musicbrainz.org/ws/2/series/?query=%22Studio%20Brussel%22

#### Search Fields
The Series index contains the following fields you can search
| Field | Description
| alias | (part of) any alias attached to the series (diacritics are ignored)
| comment | (part of) the series' disambiguation comment
| series | (part of) the series' name (diacritics are ignored)
| seriesaccent | (part of) the series' name (with the specified diacritics)
| sid | the series' MBID
| tag | (part of) a tag attached to the series
| type | the series' type
If you don't specify a field, the terms will be searched for in the alias and series fields.

### Xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<metadata created="2017-03-12T18:06:29.595Z" xmlns="http://musicbrainz.org/ns/mmd-2.0#" xmlns:ext="http://musicbrainz.org/ns/ext#-2.0">
  <series-list count="2" offset="0">
    <series id="dab51ad0-48ba-4ff3-aa77-8b13bf5f40d9" type="Release group" ext:score="100">
      <name>Studio Brussel: De Maxx</name>
      <disambiguation>radio show compilations</disambiguation>
    </series>
    <series id="9b5b8690-8cd8-4f1e-942c-c2031c59d3ff" type="Release group" ext:score="87">
      <name>Studio Brussel: Life Is Music</name>
      <disambiguation>radio show compilations</disambiguation>
      <tag-list>
        <tag count="1">
          <name>stubru</name>
        </tag>
      </tag-list>
    </series>
  </series-list>
</metadata>

### Json
{
  "created": "2017-03-12T18:06:29.595Z",
  "count": 2,
  "offset": 0,
  "series": [
    {
      "id": "dab51ad0-48ba-4ff3-aa77-8b13bf5f40d9",
      "type": "Release group",
      "score": "100",
      "name": "Studio Brussel: De Maxx",
      "disambiguation": "radio show compilations"
    },
    {
      "id": "9b5b8690-8cd8-4f1e-942c-c2031c59d3ff",
      "type": "Release group",
      "score": "87",
      "name": "Studio Brussel: Life Is Music",
      "disambiguation": "radio show compilations",
      "tags": [
        {
          "count": 1,
          "name": "stubru"
        }
      ]
    }
  ]
}

## Tag

#### Example
http://musicbrainz.org/ws/2/tag/?query=shoegaze

#### Search Fields
The tag index contains these fields you can search:
| Field | Description
| tag | (part of) the tag's name

#### Xml
<metadata xmlns="http://musicbrainz.org/ns/mmd-2.0#" xmlns:ext="http://musicbrainz.org/ns/ext#-2.0">
    <tag-list count="5" offset="0">
        <tag ext:score="100">
            <name>shoegaze</name>
        </tag>
        <tag ext:score="62">
            <name>rock shoegaze</name>
        </tag>
        <tag ext:score="62">
            <name>indie shoegaze</name>
        </tag>
        <tag ext:score="50">
            <name>doom metal ethereal shoegaze</name>
        </tag>
        <tag ext:score="31">
            <name>ambient folk classical electronic shoegaze alternative rock indie</name>
        </tag>
    </tag-list>
</metadata>

#### Json
{
  "created": "2013-02-05T08:20:52.180Z",
  "count": 5,
  "offset": 0,
  "tags": [
    {
      "score": "100",
      "name": "shoegaze"
    },
    {
      "score": "62",
      "name": "rock shoegaze"
    },
    {
      "score": "62",
      "name": "indie shoegaze"
    },
    {
      "score": "50",
      "name": "doom metal ethereal shoegaze"
    },
    {
      "score": "31",
      "name": "ambient folk classical electronic shoegaze alternative rock indie"
    }
  ]
}

## URL

#### Example
http://musicbrainz.org/ws/2/url/?query=Hello

#### Search Fields
The URL index contains the following fields you can search
| Field | Description
| relationtype | the type of a relationship the URL is in (e.g. "wikidata")
| targetid | the MBID of an entity related to the URL
| targettype | an entity type related to the URL (e.g. "artist")
| uid | the URL's MBID
| url | the actual URL string
| url_ancestor | the actual URL string, but also returns any ancestor paths (e.g. "https://example.org/some/stuff" will match "https://example.org/some")
| url_descendent | the actual URL string, but also returns any descendant paths (e.g. "https://example.org/some/stuff" will match "https://example.org/some/stuff/here")

#### Xml
<metadata created="2017-03-11T01:04:24.353Z" xmlns="http://musicbrainz.org/ns/mmd-2.0#" xmlns:ext="http://musicbrainz.org/ns/ext#-2.0">
  <url-list count="0" offset="0"/>
</metadata>

#### Json
{
  "created": "2017-03-11T01:04:24.353Z",
  "count": 0,
  "offset": 0,
  "urls": [ ]
}

## Work

#### Example
https://beta.musicbrainz.org/ws/2/work/?query=work:Frozen%20AND%20arid:4c006444-ccbf-425e-b3e7-03a98bab5997

#### Search Fields
The Work index contains the following fields you can search
| Field | Description
| alias | (part of) any alias attached to the work (diacritics are ignored)
| arid | the MBID of an artist related to the event (e.g. a composer or lyricist)
| artist | (part of) the name of an artist related to the work (e.g. a composer or lyricist)
| comment | (part of) the work's disambiguation comment
| iswc | any ISWC associated to the work
| lang | the ISO 639-3 code for any of the languages of the work's lyrics
| recording | (part of) the title of a recording related to the work
| recording_count | the number of recordings related to the work
| rid | the MBID of a recording related to the work
| tag | (part of) a tag attached to the work
| type | the work's type (e.g. "opera", "song", "symphony")
| wid | the work's MBID
| work | (part of) the work's title (diacritics are ignored)
| workaccent | (part of) the work's title (with the specified diacritics)
If you don't specify a field, the terms will be searched for in the alias and work fields.

#### Xml
<metadata xmlns="http://musicbrainz.org/ns/mmd-2.0#" xmlns:ext="http://musicbrainz.org/ns/ext#-2.0">
    <work-list offset="0" count="1">
        <work ext:score="100" id="10c1a66a-8166-32ec-a00f-540f111ce7a3">
            <title>Frozen Fred</title>
            <relation-list>
                <relation type="composer">
                    <artist id="4c006444-ccbf-425e-b3e7-03a98bab5997">
                        <name>Michiel Peters</name>             
                        <sort-name>Peters, Michiel</sort-name>
                    </artist>
                </relation>
            </relation-list>
         </work>
    </work-list>
</metadata>

#### Json
{
  "created": "2017-03-12T17:25:03.53Z",
  "count": 1,
  "offset": 0,
  "works": [
    {
      "id": "10c1a66a-8166-32ec-a00f-540f111ce7a3",
      "score": "100",
      "title": "Frozen Fred",
      "relations": [
        {
          "type": "composer",
          "direction": "backward",
          "artist": {
            "id": "4c006444-ccbf-425e-b3e7-03a98bab5997",
            "name": "Michiel Peters",
            "sort-name": "Peters, Michiel"
          }
        },
        {
          "type": "performance",
          "direction": "backward",
          "recording": {
            "id": "17b376c8-68a8-43bb-a065-ff27c04cfd5f",
            "title": "Frozen Fred",
            "video": null
          }
        }
      ]
    }
  ]
}
This page is transcluded from revision #78397 of MusicBrainz API / Search.
