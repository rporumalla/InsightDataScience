#!/usr/bin python

# Do pip install python-dateutil before execution

import sys
import os
import json
import calendar
import itertools
from dateutil import parser
from operator import itemgetter

class Hashtag:
  """ Represents each hashtag(vertex) in the graph.
  Uses a List to keep track of the other hashtags(vertices)
  to which it is connected. For each neighbor added, the degree
  is incremented by 1. For each neighbor removed, the degree is
  decremented by 1.
  """
  def __init__(self, hashtag):
    self.hashtag = hashtag
    self.neighbors = []
    self.degree = 0

  # string representation of the hashtag and it's neighbors
  def __str__(self):
    return str(self.hashtag) + ": " + str(self.neighbors)

  # this is to add neighbor to a hashtag and increment degree by 1
  # for each new neighbor added
  def add_neighbor(self, hashtag):
    if self.check_neighbor_not_present(hashtag):  # check if neighbor is already present
      self.neighbors.append(hashtag)
      self.degree = self.degree + 1

  # this is to remove neighbor of a hashtag and decrement degree by 1
  # for each neighbor removed
  def remove_neighbor(self, hashtag):
    if not(self.check_neighbor_not_present(hashtag)): # check if neighbor is already removed
      self.neighbors.remove(hashtag)
      self.degree = self.degree - 1

  # this is to check if a particular neighbor is present or not
  # and returns a boolean value
  def check_neighbor_not_present(self, hashtag):
    if hashtag in self.neighbors:
      return False
    else:
      return True

  # gets the list of neighbors of the hashtag
  def get_neighbors(self):  
    return self.neighbors

  # gets the current hashtag
  def get_hashtag(self):
    return self.hashtag

  # gets the degree of the hashtag
  def get_degree(self):
    return self.degree
 
class Edge:
  """ Holds the master list of hashtags.
  Also provides methods for adding and connecting one hashtag to another.
  Provides method to remove disconnected nodes
  """
  def __init__(self):
    self.hashtag_dict = {}
    self.num_hashtags = 0

  def __iter__(self):
    return iter(self.hashtag_dict.values())

  # adds a new hashtag into the dictionary
  def add_hashtag(self, hashtag):
    if hashtag not in self.hashtag_dict:
      self.num_hashtags = self.num_hashtags + 1
      new_hashtag = Hashtag(hashtag)
      self.hashtag_dict[hashtag] = new_hashtag

  # remove hashtag from dictionary
  def remove_hashtag(self, hashtag):
    if hashtag in self.hashtag_dict:
      self.num_hashtags = self.num_hashtags - 1
      del self.hashtag_dict[hashtag]

  # adds a new edge from 'frm' hashtag to 'to' hashtag
  # and viceversa
  def add_edge(self, frm, to):
    if frm not in self.hashtag_dict:  # checks if the hashtag is already present in the dictionary
      self.add_hashtag(frm)
    if to not in self.hashtag_dict:   # checks if the hashtag is already present in the dictionary
      self.add_hashtag(to)

    # checks for hashtag self pointers before adding neighbors
    if frm != to:     
      self.hashtag_dict[frm].add_neighbor(to)
      self.hashtag_dict[to].add_neighbor(frm)

  # removes edge for tweets outside 60-second window
  def remove_edge(self, frm, to):
    if frm != to:    # checks for self pointer hashtags
      tags = self.get_hashtags()
      if (frm in tags and to in tags):   # check if the hashtags in the edge were already added
        # removes the neighbors of the hashtags in the edge
        self.hashtag_dict[frm].remove_neighbor(to)  
        self.hashtag_dict[to].remove_neighbor(frm)
        if len(self.hashtag_dict[frm].get_neighbors()) == 0: 
          self.remove_hashtag(frm)       # remove hashtag if neighbor count is 0
        if len(self.hashtag_dict[to].get_neighbors()) == 0:
          self.remove_hashtag(to)        # remove hashtag if neighbor count is 0
    
  # calculates the average degree for each tweet
  def average_degree(self):
    # initialize values
    sum = 0
    count = 0
    for tag in self.hashtag_dict:
      if len(self.hashtag_dict[tag].neighbors) > 0:
        sum += self.hashtag_dict[tag].get_degree()
        count += 1
    if count == 0:
      avg = 0.00
    else:
      avg = sum/float(count)   # calculate average degree

      # to get precision of 2 digits after decimal place with truncation
      before_dec, after_dec = str(avg).split('.')
      avg = float('.'.join((before_dec, after_dec[:2])))
    
    return "%0.2f" % avg

  # gets the hashtags added to dictionary so far
  def get_hashtags(self):
    return self.hashtag_dict.keys()

if __name__ == '__main__':
  input_pathname = sys.argv[1]         # input file
  output_pathname = sys.argv[2]        # output file
  tweet_list = []                      # contains list of hashtags dictionary with incoming tweets
  tweet_dict = {}                      # hashtags dictionary containing keys - hashtag and created_at
  tweet_list_out_range = []            # contains list of hashtags dictionary with tweets outside 60-second window
  e = Edge()
  fo = open(output_pathname, "w+")     # open outfile for writing results
  fo.seek(0, 0)                        # position at beginning of output file
  with open(input_pathname, "r") as f: # open input file for reading
    for line in f:                     # read the file line by line
      tweet = json.loads(line)         # load from a json string for parsing
      if ("entities" in tweet and "created_at" in tweet):    # check for presence of hashtags and created_at fields in each entry
        hashtags = []
        for index in range(len(tweet["entities"]["hashtags"])): 
          tw = tweet["entities"]["hashtags"][index]["text"]
          hashtags.append("#" + tw.encode("utf-8"))    # append all the text entries in hashtags to a list
        tweet_dict["hashtags"] = hashtags    # add the hashtags list as value to "hashtags" key in the dictionary
        timestamp = calendar.timegm(parser.parse(tweet["created_at"]).timetuple()) # convert timestamp in epoch format
        tweet_dict["created_at"] = timestamp # add the apoch timestamp as value to "created_at" key in the dictionary
        tweet_list.append(tweet_dict.copy()) # append the dictionary to a list
        
        # sort the list based on epoch timestamp. Uses Timsort algorithm (O(n logn) complexity).
        # Timsort is a hybrid algorithm, derived from merge sort and insertion sort
        tweet_list = sorted(tweet_list, key=itemgetter("created_at"))
        max = tweet_list[len(tweet_list)-1]["created_at"]   # maximum timestamp in the list of values
        tweet_list_out_range = [x for x in tweet_list if max-x["created_at"] >= 60]  # list of hashtags dictionary outside 60-second window
        tweet_list = [x for x in tweet_list if max-x["created_at"] < 60]  # list of hashtags dicitonary inside 60-second window
        if len(tweet_list_out_range) > 0:   # check if any edges need to be removed 
          for i, tweets in enumerate(d["hashtags"] for d in tweet_list_out_range): # loop through the list to determine edges to be removed 
            tweets = list(set(tweets))   # to eliminate self pointing hashtags
            if len(tweets) > 1:          # check to make sure there is more than 1 hashtag condition for edge removal
              for a, b in itertools.combinations(tweets, 2): # generate combination of edges from the hashtag list
                e.remove_edge(str(a), str(b))   # remove the edges
        for i, tweets in enumerate(d["hashtags"] for d in tweet_list): # loop through the list to determine edges to be added
          tweets = list(set(tweets))     # to eliminate self pointing hashtags
          if len(tweets) > 1:            # check to make sure there is more than 1 hashtag condition for adding an edge
            for t in tweets:
              e.add_hashtag(str(t))      # add hashtag from the entry
            for a, b in itertools.combinations(tweets, 2): # generate combination of edges from the hashtag list
              e.add_edge(str(a), str(b))     # add edge
 
        avg = str(e.average_degree())    # calculate rolling average degree
        fo.write(avg)                    # write average degree to output file
        fo.write("\n")                   # write a new line to output file 
        fo.seek(0, 2)                    # go to end of file
  f.close()                              # close the input file
  fo.close()                             # close the output file
