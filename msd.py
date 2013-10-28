#!/bin/env python

class Song(object):
    def __init__(self, filename):
        self.h5 = tables.openFile(filename, mode="r")

    def close(self):
        self.h5.close()

def main():
    s = Song("MillionSongSubset/data/A/A/A/TRAAAAW128F429D538.h5")

if __name__ == "__main__":
    main()
