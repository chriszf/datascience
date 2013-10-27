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

We'll also need the some supplemental information, [the echo nest taste profile subset](http://labrosa.ee.columbia.edu/millionsong/tasteprofile), which includes user preference data which can be exploited for building a recommendation engine.

### Our Tools
Our first tool of choice in the matter will be python. You'll need to install a version [appropriate for your system](http://docs.python-guide.org/en/latest/#getting-started), so take a moment to do that. You'll also need a working copy of [MongoDB](http://www.mongodb.org/) and [NumPy](http://stackoverflow.com/questions/11114225/installing-scipy-and-numpy-using-pip) as well. Get all of these installed and clone this repository to get started.

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
* `artist_mbid` - A guid for this song from the musicbrainz service.
* `song_id` - A guid for this song from the EchoNest service.
* `track_id` - A guid for this song (as a track) from the EchoNest service.

After that, there are a few fields which are useful in terms of organization, basically user-applied categories from different music services:

* `artist_mbtags` - user applied tags from musicbrainz
* `artist_terms` - 'terms' from echonest, another source of tags
* `artist_terms_freq` - the frequency with which those tags are applied
* `artist_terms_weight` - something? (FIGURE THIS OUT)

The next couple are statements about the musical nature of the song, what mode is it in, what key is it in. Some statements are calculated from the audio data itself, not extracted from the original score, so they come with a confidence number.

* `duration` - song length
* `key` - the estimated key of a song
* `key_confidence` - confidence of the estimated key
* `mode` - song mode, major or minor
* `mode_confidence` - confidence of the estimated mode
* `tempo` - estimated song tempo in BPM
* `time_signature` - estimate of the number of beats per bar
* `time_signature_confidence` - confidence of the estimated time signature

The last few numbers are calculated as aggregates of the statements from the previous statements. They're machine estimates of subjective ideas. They are potentially useful for reducing a song to a fingerprint, and we'll include them here.

* `danceability` - an algorithmic estimation of the song's danceability
* `energy` - 'energy from a listener's point of view', unknown but potentially interesting
* `loudness` - overall loudness of a track in decibels
* `song_hotttness` - a measure of a song's social/online activity, at the time the dataset was created

We'll also need a sense of user ratings for the tracks we're analyzing. These aren't part of the primary MSD dataset, these come from the taste profile subset. This dataset is very simple, it is a single file with three fields separated by tabs

* `user_id` - a guid representing a user
* `song` - the EchoNest Song ID for the song in question
* `play_count` - the number of times the song has been played by that user

This data will be packed into two collections in mongo: one with a single document per song, containing all the fields we have highlighted above. The second collection will be for users, each document containing the user id and a subdocument containing each song and their play counts.
