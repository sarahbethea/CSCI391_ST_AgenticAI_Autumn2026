<!-- source: https://musicbrainz.org/doc/Release -->
<!-- site: MusicBrainz documentation -->

# Release
A MusicBrainz release represents the unique release (i.e. issuing) of a product containing at least one audio medium (a disc, for example, on a CD release). Each release has one or more identifying properties, such as a release date and country, a label, a barcode, a specific type of packaging or a specific cover art.
If you walk into (or digitally browse) a store and see the standard edition of an album next to a deluxe edition of that same album, you're looking at two different MusicBrainz releases, which are grouped as part of the same release group.
Mediums have a format (such as CD, DVD, vinyl or cassette) and can optionally also have a title. For physical releases, each medium is the actual physical medium that stores the audio content. This means that each CD in a multi-disc release will be entered as separate mediums within the release, and that both sides of a vinyl record or cassette will exist on one medium. For digital releases, mediums are a more fluid concept, and should generally just follow the structure set by the artist or label. For example, a digital album that claims to include "disc 1" and "disc 2" should be added with two digital mediums, even if it can be purchased as one single folder of files or streamed in a single sitting.
Keep in mind there are some exceptional cases where the one disc to one medium equivalence does not apply. For example, the two sides of a hybrid SACD (the CD side and the SACD side) should be entered as two mediums. These exceptions are indicated in the release guidelines.
Every medium can (and should ideally have) a tracklist, which represents the set and ordering of tracks included in the medium, as listed on a liner, a digital store page, or any other official source. A medium can be empty (missing its tracklist) if its contents are not yet known to MusicBrainz users.

## Examples
- CD single: Creep
- 2× CD album: The Fragile
- Vinyl single: Feel the Music
- 2× vinyl album: Blonde on Blonde
- 4x digital media album: Terraria: Official Soundtrack
- Digital audiobook: Der Schattenkrieg

## Style guidelines
Please see the guidelines for releases.

## Release properties

### Title
The title of the release.

### Artist
The artist(s) that the release is primarily credited to, as credited on the release.

### Date
The date the release was issued.

### Country
The country the release was issued in.

### Label
The label which issued the release. There may be more than one.

### Catalog number
This is a catalog number assigned to the release by the label which can often be found on the spine or near the barcode. There may be more than one, especially when multiple labels are involved. This is not the ASIN — there is a relationship for that — nor the label code.

### Barcode
The barcode, if the release has one. The most common types found on releases are 12-digit UPCs and 13-digit EANs.

### Status
The status describes how "official" a release is. Possible values are:
|
official
Any release officially sanctioned by the artist and/or their record company. Most releases will fit into this category.
promotion
A give-away release or a release intended to promote an upcoming official release (e.g. pre-release versions, releases included with a magazine, versions supplied to radio DJs for air-play).
bootleg
An unofficial/underground release that was not sanctioned by the artist and/or the record company. This includes unofficial live recordings and pirated releases.
pseudo-release
An alternate version of a release where the titles have been changed. These don't correspond to any real release and should be linked to the original release using the transl(iter)ation relationship.
withdrawn
An official release that was actively withdrawn from circulation by the artist and/or their record company after being released, whether to replace it with a new version or to retire it altogether. This does not include releases that have reached the end of their “natural” life cycle, such as being sold out and out of print.
expunged
A previously official release that was actively expunged from an artist or records company’s discography. This should not be used in cases where the release was just withdrawn, there needs to be known artist or label intent to disown the release and no longer consider it part of their discography. If it is unclear, use Withdrawn.
cancelled
A planned official release that was cancelled before being released, but for which enough info is known to still confidently list it (e.g. it was available for preorder).

### Packaging
The outermost physical packaging that the release is sold or distributed in. See the list of packaging for more information.

### Language
The language the release title and track titles are written in. The possible values are taken from the ISO 639-3 standard.

### Script
The script used to write the release title and track titles. The possible values are taken from the ISO 15924 standard.
| Guide to common scripts
|
Latin (also known as Roman or, incorrectly, "English")
Latin is the most common script, and usually the correct choice. It is used for all Western European languages, and many others. It is also the most common script used for transliterations.Arabic العربية
The Arabic script is used for languages in the Middle East and Central Asia such as Arabic, Persian and Urdu.Cyrillic Кириллица
Cyrillic is used for languages in Eastern Europe such as Russian, Ukrainian, Belarusian and Bulgarian.Greek Ελληνικά
The Greek script is used for Greek, but several characters have also been adopted for mathematical uses.Han 漢字/汉字
Han characters are used by Chinese, Japanese and Korean. Han (simplified), Han (traditional), Japanese, or Korean should be used instead when the variant is known.Han (simplified) 简体字
The simplified variant of Han characters is used to write Chinese in mainland China, Malaysia and Singapore.Han (traditional) 繁體字/正體字
The traditional variant of Han characters is used to write Chinese in Hong Kong, Macao and Taiwan.Korean 한글
This covers any combination of Hangul and Hanja for Korean.Hebrew עברית
The Hebrew script is used for Hebrew, but a few characters have also been adopted for mathematical uses.Japanese 漢字 & ひらがな & カタカナ
This covers any combination of Kanji, Hiragana and Katakana for Japanese.Katakana カタカナ
Katakana should only be used for transliterations into Japanese (example, English->Japanese). Japanese language titles with words written in Katakana should use Japanese.Thai ไทย
The Thai script is used for Thai, as well as some minor languages in south-east Asia.

### MBID
See the page about MBIDs for more information.

### Disambiguation comment
See the page about comments for more information.

### Annotation
See the page about annotations for more information.

### Data quality
Data quality indicates how good the data for a release is. It is not a mark of how good or bad the music itself is - for that, use ratings.
High quality
All available data has been added (including relationships, works, etc.), if possible alongside cover art with liner info that proves it.
Default quality
This is the default setting - technically "unknown" if the quality has never been modified, "normal" if it has.
Low quality
The release needs serious fixes, or its existence is hard to prove (but it's not clearly fake).
Currently, data quality has no further effect than helping users know what to expect from the data. Until 2012, data quality also used to influence the voting requirements for edits made to the release. While this is no longer the case, we mention it here because it can explain the notes and voting results of some very old edits.

## Medium properties

### Title
The title of this particular medium.

### Format
The format of the medium.
This page is transcluded from revision #78324 of Release.
