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

### Our Tools
Our first tool of choice in the matter will be python. You'll need to install a version [appropriate for your system](http://docs.python-guide.org/en/latest/#getting-started), so take a moment to do that. You'll also need a working copy of [MongoDB](http://www.mongodb.org/) and [NumPy](http://stackoverflow.com/questions/11114225/installing-scipy-and-numpy-using-pip) as well. Get these installed, 

Python is a great language for data science, it's not the fastest sprinter on the block, but it has a lot of tools that make the manipulation of large datasets less painful than they would be otherwise. NumPy is one of those. Python has long been used by the science community to deal with scientific data sets. Although the nature of the analysis in those situations tends to be different, both in terms of method and scale, usage of Python for data science is a natural extension of using it for traditional science.

HDF5 is quickly becoming a common standard for storing large amounts of structured data. Backed by NASA as the format of choice for managing enormous amounts of satellite data, it has a lot of nice features for manipulating and organizing data in a meaningful way. You can think of it as a sort of an on-disk database without a requirement (or capability, if you prefer) to handle parallel access over a network, like an offline database.

...

Which is unfortunately why we can't use it. The features for storing and indexing the data are amazing, but for our nefarious purposes, the inability to run it in a multi-user environment is a bit of a deal breaker. For most purposes, 'faster' and 'realtime' are strictly better, so exporting our data to HDF5, processing it, then reloading it into a database that can integrate with an online dashboard has two steps too many. Instead, we're going to load our data into a database that can cope with being a data store for our application as well as a platform for our analysis, hence MongoDB. This guide will be focused on this first step, extracting our data from its source and moving it somewhere manageable.

## The Process
The process will be broken up into three parts, 
