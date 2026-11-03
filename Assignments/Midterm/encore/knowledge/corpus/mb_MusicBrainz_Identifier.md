<!-- source: https://musicbrainz.org/doc/MusicBrainz_Identifier -->
<!-- site: MusicBrainz documentation -->

# MusicBrainz Identifier
One of MusicBrainz' aims is to be the universal lingua franca for music by providing a reliable and unambiguous form of music identification; this music identification is performed through the use of MusicBrainz Identifiers (MBIDs).
In a nutshell, an MBID is a 36 character Universally Unique Identifier that is permanently assigned to each entity in the database, i.e. artists, release groups, releases, recordings, works, labels, areas, places and URLs. MBIDs are also assigned to Tracks, though tracks do not share many other properties of entities. For example, the artist Queen has an artist MBID of 0383dadf-2a4e-4d10-a46a-e9e041da8eb3, and their song Bohemian Rhapsody has a recording MBID of b1a9c0e9-d987-4042-ae91-78d6a3267d69.
An entity can have more than one MBID. When an entity is merged into another, its MBIDs redirect to the other entity.

## Using MBIDs for disambiguation
MBIDs are used to disambiguate between entities that share the same name in the MusicBrainz Database.
For example, there are two popular artists with the name "John Williams":
- John Williams, the soundtrack composer and conductor, has an artist MBID of 53b106e7-0cc6-42cc-ac95-ed8d30a3a98e
- John Williams, the classical guitar player, has an artist MBID of 8b8a38a9-a290-4560-84f6-3d4466e8d791
And there are two different singles titled "99 Red Balloons":
- 99 Red Balloons, the original by Nena, has a release MBID of 189002e7-3285-4e2e-92a3-7f6c30d407a2
- 99 Red Balloons, the cover by Goldfinger, has a release MBID of c9f91cdc-984e-4303-9a51-4ac0dfa2348f

## Using MBIDs in applications
MBIDs play an important role when managing a digital music collection and there are several applications that are MusicBrainz enabled.

### Taggers
Multiple MBIDs may be written to a file by a MusicBrainz enabled tagger application. They are commonly used to identify:
- the recording itself
- the release
- the label
- the track artist
- the release artist
For more information, see the tag documentation and the tag mappings of the MusicBrainz Picard tagger.

### Music players
Music player applications can take advantage of a file that has been tagged with MBIDs to do things such as:
- query the MusicBrainz Database for further information about the file or related entities
- reliably search for related files based on a unique string, instead of by potentially ambiguous strings such as artist name or release title

### Flickr
See Flickr Machine Tag for information about adding MBIDs to photos on Flickr.

## Uniform Resource Identifier
URIs can be constructed by prefixing the MBID with the address of the MusicBrainz server and the entity type, for example Queen's URI becomes http://musicbrainz.org/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3, and Bohemian Rhapsody's URI becomes http://musicbrainz.org/recording/ebf79ba5-085e-48d2-9eb8-2d992fbf0f6d.

## See also
There are several other identifiers that MusicBrainz uses:
- Disc ID: An ID calculated from the TOC of a CD.
- AcoustID: the open-source acoustic fingerprint system used by MusicBrainz since 2013.
- Barcode: Machine-readable numbers used as stock control mechanisms by retailers.
- ISRC: The International Standard Recording Code, an identification system for audio and music video recordings.
- ISWC: The International Standard Musical Work Code, an identification system for musical works.
- IPI, a number identifying persons connected to ISWC registered works (authors, composers, etc.).
- PUID: The IDs used in the proprietary MusicDNS audio fingerprinting system operated by MusicIP (used by MusicBrainz 2006–2013)
- ISNI: The International Standard Name Identifier, used to uniquely identify artists and/or labels.
This page is transcluded from revision #78859 of MusicBrainz Identifier.
