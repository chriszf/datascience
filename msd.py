#!/bin/env python
import tables
import sys
import pymongo

client = pymongo.MongoClient()

class Song(object):
    def __init__(self, filename):
        self.h5 = tables.openFile(filename, mode="r")

    @property
    def title(self):
        return self.h5.root.metadata.songs.cols.title[0]

    @property
    def artist_name(self):
        return self.h5.root.metadata.songs.cols.artist_name[0]

    @property
    def duration(self):
        return self.h5.root.analysis.songs.cols.duration[0]

    @property
    def energy(self):
        return self.h5.root.analysis.songs.cols.energy[0]

    @property
    def danceability(self):
        return self.h5.root.analysis.songs.cols.danceability[0]

    @property
    def key(self):
        return int(self.h5.root.analysis.songs.cols.key[0])

    @property
    def mode(self):
        return int(self.h5.root.analysis.songs.cols.mode[0])

    @property
    def terms(self):
        term_words = list(self.h5.root.metadata.artist_terms)
        freqs = list(self.h5.root.metadata.artist_term_freq)
        weight = list(self.h5.root.metadata.artist_term_weight)

        combined = zip(terms, freqs, weight)
        term_list = [ dict(zip(["term", "freq", "weight"], t)) for t in combined ]

        return term_list

    @property
    def json(self):
        return {"title": self.title,
                "artist_name": self.artist_name,
                "duration": self.duration,
                "energy": self.energy,
                "danceability": self.danceability,
                "key": self.key,
                "mode": self.mode
                }

    def close(self):
        self.h5.close()

def save_to_db(song):
    json = song.json
    print json
    client.datascience.songs.insert(json)

def main():
    songs = client.datascience.songs
    songs.remove()

    for line in sys.stdin:
        filename = line.strip()
        s = Song(filename)
        save_to_db(s)
        s.close()

if __name__ == "__main__":
    main()
