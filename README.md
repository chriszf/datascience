# Intro to Data Science -- A Prelude
Greetings, data scientist of tomorrow! So you've decided to become a data scientist, dissecting data, dissolving it in reagents and then collecting the precipitate into vials to be used in a double-blind study... wait.

It's not _that_ kind of science? Really? Then wha... like _computer_ science, but with data? Okay. I guess let me start over from the beginning.

Greetings, data scientist of tomorrow. So, you've decided to totally nerd out about all the hidden insights to be gleaned from the vast tracts of data available to you. You want to tease secrets out of your data, such as which color blue makes the most people buy your product, or what your purchasing habits say about your pregnancy due date, or whether or not the players of your mobile game have _Parkinson's_. All these things and more are possible with modern data science techniques.

## An Overview
Data science falls at an interesting intersection of computer science and statistics. Succinctly, data science is the process of extracting information from data. Chew on that for a little bit. Data is largely composed of singular facts, often (but not strictly) temporal in nature: a user clicked on this link at this time, a user closed their browser, this user likes cats, this user likes dogs. The information we're looking for is an amalgamation of all these facts, summarized across time and individuals. Users who like cats almost always click on this link, spend 3 minutes staring at the page that comes up, then close their browsers. These are the large-scale patterns we're looking for that can't be found by looking at a table full of numbers, we'll have to use science!

One way to approach this problem is by classification through machine learning. In a process not unlike throwing spaghetti at a wall and seeing what sticks, we can run our data through a variety of tools that splits into two or more categories. Sometimes the resultant categories are unintuitive and surprising, a customer who buys zinc supplements followed by unscented lotions 3 to 6 months later is also [likely to buy baby goods shortly after](http://www.forbes.com/sites/kashmirhill/2012/02/16/how-target-figured-out-a-teen-girl-was-pregnant-before-her-father-did/).

The tools we have for doing these classifications are varied, including scary-sounding things like support vector machines, euclidean distance correlations, and k-means clustering. They're not nearly as terrifying as they sound, but all the data science tools in the world area meaningless unless we have some data to work with.

### Our Data
For this exercise, we'll be using the [million song dataset](http://labrosa.ee.columbia.edu/millionsong/). There are indeed a million songs in this dataset (reflected in the 280gb download size). In the interest of practicality, we'll be using the 10,000 song subset, which still weighs in at a hefty 1.8gb _compressed_ file. You're gonna need a lot of room, so now's the time to delete all those movies you've downloaded and uninstall some games. The data comes in a mysterious new format called HDF5, which we'll be explaining shortly.

We'll also need the some supplemental information, [the echo nest taste profile subset](http://labrosa.ee.columbia.edu/millionsong/tasteprofile), which includes user preference data which can be exploited for building a recommendation engine. Grab the full subset, which runs about 500mb.

### Our Tools
Our first tool of choice in the matter will be python. You'll need to install a version [appropriate for your system](http://docs.python-guide.org/en/latest/#getting-started), so take a moment to do that. You'll also need a working copy of [MongoDB](http://www.mongodb.org/) and [Tables](http://www.pytables.org/moin) as well. You'll also need pymongo. Get all of these installed and clone this repository to get started. As a shortcut, you can install most of these with the following command after you've cloned:

    pip install -r requirements.txt

Python is a great language for data science, it's not the fastest sprinter on the block, but it has a lot of tools that make the manipulation of large datasets less painful than they would be otherwise. NumPy is one of those. Python has long been used by the science community to deal with scientific data sets. Although the nature of the analysis in those situations tends to be different, both in terms of method and scale, usage of Python for data science is a natural extension of using it for traditional science.

HDF5 is quickly becoming a common standard for storing large amounts of structured data. Backed by NASA as the format of choice for managing enormous amounts of satellite data, it has a lot of nice features for manipulating and organizing data in a meaningful way. You can think of it as a sort of an on-disk database without a requirement (or capability, if you prefer) to handle parallel access over a network, like an offline database.

...

Which is unfortunately why we can't use it. The features for storing and indexing the data are amazing, but for our nefarious purposes, the inability to run it in a multi-user environment is a bit of a deal breaker. For most purposes, 'faster' and 'realtime' are strictly better, so exporting our data to HDF5, processing it, then reloading it into a database that can integrate with an online dashboard has two steps too many. Instead, we're going to load our data into a database that can cope with being a data store for our application as well as a platform for our analysis, hence MongoDB. This guide will be focused on this process, extracting our data from its source and moving it somewhere manageable.

## The Process
The process will be broken up into three parts, assessing our data, reading our data, then writing our data to our data store.

### Part One - Assessing our Data
The first step is to take a look at the data we have and decide what we want out of it. The MSD includes a lot of metadata about each song, but it also includes a lot of heavily-processed audio data per song. In theory, some of this information could be used to reconstruct the original song, or at least, an approximation thereof, but that's another story altogether.

Because we want to build a recommendation engine, we need to collect information that may tell us things about user's tastes. This includes obvious 'features' of a song, like genre and artist. It may also include surprising things, like BPM, danceability and song length, things which may only emerge after analysis is done. (Potentially our users could be divided cleanly, separating the world into those who like long dubstep songs and those who don't.) 

Starting with the full [field list](http://labrosa.ee.columbia.edu/millionsong/pages/example-track-description), there are a few pieces of information which seem like a good idea to grab right off the bat.

* `artist_name` - The artist name
* `title` - The song title
* `year` - The year of the song's release
* `release` - The album the song is generally considered to be from
* `artist_mbid` - A guid for this artist from the musicbrainz service
* `song_id` - A guid for this song from the EchoNest service
* `track_id` - A guid for this song (as a track) from the EchoNest service

There are a few additional terms included as descriptive tags for the artist of a given song. They apply to the artist, not the song itself, so they're quite as useful as they could be, but we'll include them just in case.

* `artist_mbtags` - Tags coming from the musicbrain service
* `artist_terms` - Tags coming from the EchoNest service
* `artist_terms_freq` - The frequency with which these tags are used to describe the artist, normalized between 0 and 1. There is a one-to-one mapping with the entries in `artist_terms`
* `artist_terms_weight` - The relevance of each tag, independent of frequency (ie: 'british invasion' is more important in describing The Beatles, but 'rock' is used more often. [Discussion here](https://developer.echonest.com/forums/thread/353).)

The next couple are statements about the musical nature of the song, what mode is it in, what key is it in. Some statements are calculated from the audio data itself, not extracted from the original score, so they come with a confidence number. We'll discard the confidence number for now, although you can always add it back later.

* `duration` - song length
* `key` - the estimated key of a song
* `mode` - song mode, major or minor
* `tempo` - estimated song tempo in BPM
* `time_signature` - estimate of the number of beats per bar

The last few numbers are calculated as aggregates of the statements from the previous statements. They're machine estimates of subjective ideas. They are potentially useful for reducing a song to a fingerprint, and we'll include them here.

* `danceability` - an algorithmic estimation of the song's danceability
* `energy` - 'energy from a listener's point of view', unknown but potentially interesting
* `loudness` - overall loudness of a track in decibels
* `song_hotttness` - a measure of a song's social/online activity, at the time the dataset was created

We'll also need a sense of user ratings for the tracks we're analyzing. These aren't part of the primary MSD dataset, these come from the taste profile subset. This dataset is very simple, it is a single file with three fields separated by tabs

* `user_id` - a guid representing a user
* `song` - the EchoNest Song ID for the song in question
* `play_count` - the number of times the song has been played by that user

This data will be packed into two collections in Mongo: one with a single document per song, containing all the fields we have highlighted above. The second collection will be for users, each document containing the user id and a subdocument containing each song and their play counts.

### Part Two - Reading our Data from HDF5
Reading from HDF5 is not as straightforward as reading from a regular file, or even iterating through a SQL database query. We'll start with a test file to start exploring the data, `h5_test.py`.

Start by opening `h5_test.py` in an editor and change the filename variable to point to an actual file in your local copy of the MSD, it doesn't matter which. Now, run the file in python with the `-i` flag:

    $ python -i h5_test.py
    >>>

The file gives us a variable, h5, which is an open file handle to the record for "I Didn't Mean To" by "Casual". If we try to print the `repr()` of the handle, we get a lot of information of the heirarchical data of the h5 file. You'll notice that it displays very much like a directory tree, which is a pretty reasonable way to organize the heterogeneous information we're trying to process.

    >>> print repr(h5)
    File(filename=/Users/guest/src/datascience/MillionSongSubset/data/A/A/A/TRAAAAW128F429D538.h5, title='H5 Song File', mode='r', root_uep='/', filters=Filters(complevel=1, complib='zlib', shuffle=True, fletcher32=False))
    / (RootGroup) 'H5 Song File'
    /analysis (Group) 'Echo Nest analysis of the song'
    /analysis/bars_confidence (EArray(83,), shuffle, zlib(1)) 'array of confidence of bars'
      atom := Float64Atom(shape=(), dflt=0.0)
      maindim := 0
      flavor := 'numpy'
      byteorder := 'little'
      chunkshape := (1024,)
    /analysis/bars_start (EArray(83,), shuffle, zlib(1)) 'array of start times of bars'
      atom := Float64Atom(shape=(), dflt=0.0)
      maindim := 0
      flavor := 'numpy'
      byteorder := 'little'
      chunkshape := (1024,)
    ...

The data is organized into 'groups', such as the the `/ (RootGroup)` and `/analysis (Group)` in the above example. You can access the groups by their path using dot notation. To access the `analysis` group, type the following:

    >>> print repr(h5.root.analysis)
    /analysis (Group) 'Echo Nest analysis of the song'
      children := ['beats_start' (EArray), 'segments_pitches' (EArray), 'segments_confidence' (EArray), 'sections_start' (EArray), 'tatums_confidence' (EArray), 'segments_timbre' (EArray), 'segments_loudness_start' (EArray), 'sections_confidence' (EArray), 'bars_confidence' (EArray), 'segments_loudness_max_time' (EArray), 'bars_start' (EArray), 'tatums_start' (EArray), 'beats_confidence' (EArray), 'segments_start' (EArray), 'segments_loudness_max' (EArray), 'songs' (Table)]

This tells us that the `analysis` group has a number of different children, such as `beats_start` which is an `EArray` and the `songs` element, which is a `Table`. To access elements of a `Table` element, we refer to it by its path, then access the `.cols.<COLUMN_NAME>` attribute, followed by a subscript referring to a specific row in the table. For example, to access the `songs` table and the `danceability` in it, we type the following:

    >>> print h5.root.analysis.songs.cols.danceability[0]

For most of the tables in our dataset, there will be only one row.

What we need to do is find all of the fields we listed above, and identify the paths to each of them. Every column path you need is listed in the primary listing we did earlier, by printing the `repr()` of the entire h5 file. Close the `h5_test.py` file and open up `msd.py`.

The paths to the different parts of the data are aggravating to access. We'll make things easier by encapsulating them in a class named `Song`. The initializer is provided for you, as well as a `close` method which you should call when you're done with a file. They simply open the file using the `tables` module and saves it as an instance attribute, and closes it, respectively. It is from this attribute we will extract the rest of the data. We'll first make `@property` for our danceability field from earlier.

    class Song(object):
        def __init__(self, filename):
            self.h5 = tables.openFile(filename, mode="r")

        @property
        def danceability(self):
            d = h5.root.analysis.songs.cols.danceability[0]
            if d == 0:
                return None
            else:
                return d

        def close(self):
            self.h5.close()

In the documentation, a value of `0.0` for this field indicates that the value was not calculated (or unable to be calculated). We'll translate this to a `None` value in python, to remain idiomatic. Now, in our `main` function, let's try out our new property:

    def main():
        s = Song("MillionSongSubset/data/A/A/A/TRAAAAW128F429D538.h5")
        print s.danceability
        s.close()

Running our program, we get the following output:

    (env)$ python msd.py 
    None

I think you've guessed the next step. We need to add a property for every single field we've listed above. Go ahead and do that now. Be sure to pay attention to the potential values for each field and make sure that 'empty' values are correctly set to None.

We'll need to make a special dispensation for `artist terms`. The terms from EchoNest include both a `frequency` and `weight`. Rather than keep them as separate fields, we can combine them into a single json structure, like so:

    terms = [
        {"term": "rock",
         "frequency": 1.0,
         "weight": 0.8},
        {"term": "british invasion",
         "frequency": 0.7,
         "weight": 0.9}
    ]

We'll make this dictionary creation a part of the `terms` @property on our object, returning it instead of a single list of words. Tip: calling the `list()` function on the h5 element will return a regular python list that you can enumerate over.

#### A Note about NumPy and MongoDB
Some of the record fields appear to be integers, but will be returned as `numpy.int32` objects. MongoDB will choke when trying to insert these fields, so be sure to cast them as integers when returning them from their `@property` methods.

### Part Two The Sequel - Creating a unix style tool
Now we're going to attend to the main function. We can read individual songs by filename, and we need to process all the songs on disk. Normally, we would write a function that walks the entire directory tree and finds all files that match our patterns, then create an object out of each of these files.

There's nothing wrong with this, but there's not a lot to recommend this process either, when we have a perfectly good unix utility to do this. The following command does the finding and pattern matching for us:

    $ find /path/to/MSD -name "*.h5"

The output of the find command can be piped into our `msd.py` program and we can consume the results one filename at a time, like so:

    $ find . -name "*.h5" | python msd.py

For the purposes of testing, we'll limit the number of files we pipe into our program, as processing all 10,000 songs will take a long time, so we'll use the following command instead:

    $ find . -name "*.h5" | head -5 | python msd.py

If we run this now, nothing will happen, as we don't use any of the data that's piped into our program. We'll fix that now. Open up msd.py, and add the following to the top:

    import sys

We're going to grab sys.stdin, which is a file handle referencing stdin, where unix pipes data to. Now, in our main function, we're going to loop through all the lines piped into stdin. Go ahead and erase the old contents of main:

    def main():
        for line in sys.stdin:
            filename = line.strip()
            print filename
            song = Song(filename)
            print song.title
            song.close()

If we ran our program now, it would sit there and never quit. We need to pipe filenames into it:

    (env)$ find MillionSongSubset -name "*.h5" | head -5 | python msd.py 
    MillionSongSubset/AdditionalFiles/subset_msd_summary_file.h5
    Deep Sea Creature
    MillionSongSubset/data/A/A/A/TRAAAAW128F429D538.h5
    I Didn't Mean To
    MillionSongSubset/data/A/A/A/TRAAABD128F429CF47.h5
    Soul Deep
    MillionSongSubset/data/A/A/A/TRAAADZ128F9348C2E.h5
    Amor De Cabaret
    MillionSongSubset/data/A/A/A/TRAAAEF128F4273421.h5
    Something Girls

Now we can put all of these records in our database.

### Part Three - The Database
The general strategy for database usage goes like this:

1. Read the file
2. Create a `Song` object
3. Convert the song object into a json object
4. Insert the json object into the database

Mongo uses json as its storage format of choice, which is why we're using it. We've already figured out how to read the file and create a `Song` out of it, so now we just need to serialize the object into json.

This is easier than it sounds, because we don't really need to turn the object into json, we just need to turn the object into a python dictionary, and as long as we don't use any odd data types in it, pymongo will serialize it just fine. Let's look at an example. We'll add a property on the `Song` class called `json` as follows:

    @property
    def json(self):
        return {'artist': self.artist_name,
                'title': self.title}

This returns a dictionary representing the song title and name. When we try to insert this into the database, everything will be hunky dory.

We've now arrived at the character building portion of this exercise. Go ahead and build out the rest of the dictionary using all of the fields from part 1... Yep. Go. Get. I'll wait.

...

....

Done? Okay. Moving on.

Let's address our Mongo database. At the beginning of our file, after the existing import statements, we'll import pymongo and immediately connect to the database. Creating a `MongoClient` object with no arguments connects to the default Mongo engine on localhost using the standard port.

    import pymongo

    client = pymongo.MongoClient()

That's it, no fuss no muss. In Mongo, there is a notion of 'databases', and inside each database is a series of 'collections', essentially the equivalent of SQL tables. To create them, we just insert documents (rows) into them, referencing the collection by name when we do.

    collection = client.my_database.my_collection
    document_key = collection.insert({"new": "record"})

This inserts a new record into the collection named `my_collection` in the database named `my_database`. When you insert a record, it must have a special field named `_id`, which is the primary key used to refer to the record. If you don't include one, it Mongo assigns an `_id` and returns it as the value from the `insert` method. Here, we store the returned key in the variable `document_key`. We don't really need it, but it's good to know about. You may be tempted to use the EchoNest song id as a primary key in our collection, but be warned: Mongo has a number of restrictions on what can be an `_id`, so unless you're careful, it's best to use the automatically assigned ones.

Let's write a function that tries to insert a row into the database:

    def save_to_db(song):
        client.datascience.songs.insert(song.json)

And that's it. Unless you've fiddled with Mongo's settings, you don't need to commit a transaction or anything, the song is saved to the database. Since we'll be fiddling with the database repeatedly and you don't want to insert the same song twice, you may be tempted to first check the collection to see if the song exists prior to the insert. This is cautioned against, as the database grows in size, it will take longer and longer to search for a particular record, making the process take forever. Instead, we recommend that you destroy the collection each time you run the process. The final `main` function looks like this:

    def main():
        client.datascience.songs.remove()
        for line in sys.stdin:
            filename = line.strip()
            song = Song(filename)
            save_to_db(song)
            song.close()

### Part 4 - User Data, yes I lied to you there are more parts
Using the same techniques, we'll do the same thing for our user data. Unzip your `train_triplets.txt.zip` file now.

One snag here is that we've decided to combine multiple lines into a single document to be inserted, so our loop will be a little bit different. Remember, our file looks like this:

    user_id     song_id     number_of_plays

Each field is separated by tabs. Because of the limitations of CSV, much of the data will be repeated, as evidenced by the first few lines:

    b80344d063b5ccb3212f76538f3d9e43d87dca9e        SOAKIMP12A8C130995      1
    b80344d063b5ccb3212f76538f3d9e43d87dca9e        SOAPDEY12A81C210A9      1
    b80344d063b5ccb3212f76538f3d9e43d87dca9e        SOBBMDR12A8C13253B      2
    b80344d063b5ccb3212f76538f3d9e43d87dca9e        SOBFNSP12AF72A0E22      1
    b80344d063b5ccb3212f76538f3d9e43d87dca9e        SOBFOVM12A58A7D494      1

Fortunately, the data is grouped by the user, so we don't need to keep every user record in memory. When we encounter a new user id, we can relinquish the data structure holding the previous user.

The only thing in question is the shape of our json document to be inserted. We have a `user_id` which is uninteresting except that it is unique per user in our system. We also have a `song_id` which references the `song_id` from EchoNest. We'll use this field to reference the `songs` collection we created earlier. Last, we have an integer, the number of times this song has been played. Using the above 5 lines, this recommends a data structure which looks like this:

    { "user_id": "b80344d063b5ccb3212f76538f3d9e43d87dca9e",
      "songs": [ {"song_id": "SOAKIMP12A8C130995", "plays": 1},
                 {"song_id": "SOAPDEY12A81C210A9", "plays": 1},
                 {"song_id": "SOBBMDR12A8C13253B", "plays": 2},
                 {"song_id": "SOBFNSP12AF72A0E22", "plays": 1},
                 {"song_id": "SOBFOVM12A58A7D494", "plays": 1} ]}

We've provided a file, `user.py` which has a base upon which to build the mechanism provided above. Loop through all the lines in `train_triplets.txt`, when you encounter a new `user_id`, construct a new dictionary to be inserted into the collection. 

Similar to the `songs` collection, you may want to erase the collection before inserting records, starting afresh when you run the program.

## What's Next
From this tutorial, you should now have a mongo database named `datascience` filled with two collections, `users` and `songs`, containing all the information you need to explore the dataset. You also have enough experience building different views of the dataset, should you need to organize it differently. As a further exercise, you might try building an index of songs by the artist or album they're on. Now you're ready to attempt clustering techniques to create a recommendation system, but that's a topic for another tutorial...
