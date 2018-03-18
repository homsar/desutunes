# desutunes - a [Neko Desu](http://nekodesu.co.uk) library manager for desktop

desutunes is designed to replicate all features of iTunes that are relied on to manage the Neko Desu library, but more easily.

## Replicated features

* Reads metadata from MP3s and MP4s
* Imports them into a database ([feat. TAKUMA](https://nkd.su/database-feattakuma-10-feet/9B11E2BF18BDD27E/))
* Allows metadata to be edited
* Allows using the 'Description' field on audio files
* Has the same awkward mapping of 'Subtitle' in ID3 tags to the 'Description' field
* Uses 16-digit hex persistent IDs for tracks
* Can play songs on request
* Imports iTunes XML
* Exports XML to be read by [nkd.su](https://nkd.su)

## Additional features:

* Stores anime, role, and role qualifier separately, so that going forward they could be separated consistently rather than using a stack of regexes to guess
* Allows for a separate Inu Desu library to be stored
* Colour-codes tracks that are missing on disk and that are yet to be imported into [The Cat](https://thisisthecat.com)'s playout system
* Runs on recent versions of macOS
* Cool icons
* Minimalist UI


## Installation

Clone the repository, install Python 3.6 and the dependencies in `requirements.txt`. (I use Anaconda for this.)

## Usage

To run desutunes:

```bash
python -m desutunes.desutunes
```

To run in Inu Desu mode use the Tools menu to switch the library over.

To dump the library XML out, choose "Dump XML..." from the Tools menu.

If the Tools menu isn't clickable, defocus and refocus the desutunes window. This is a limitation of Qt on macOS.


To import audio:

* Place the audio file(s) where you want it/them to live on disk
* Drag it/them into the table view. Folders work too!

To import iTunes XML:

* Drag it into the table view

To play a track:

* Double-click a read-only field (ID or filename)