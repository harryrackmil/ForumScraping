from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import string
from datetime import datetime, date, timedelta
import pylab
import csv


def replacePcts(url):
	"""Handles encoding error in urls."""
	return url.replace("%E2%80%94", "---")

def toDateTime(datestr):
	"""Returns datetime object based on forum posting time.""" 
	if ("minutes ago" in datestr):
		datestr = "Today, " + (datetime.now() - timedelta(minutes = 1)).strftime("%I:%M %p")
	if ("Today," in datestr):
		datestr = date.today().strftime("%d %B %Y - ") + datestr[7:]
	if ("Yesterday," in datestr):
		datestr = (date.today() - timedelta(1)).strftime("%d %B %Y - ") + datestr[11:]
	return datetime.strptime(datestr, "%d %B %Y - %I:%M %p")

def wordlistTopic(topicUrl):
	"""Returns list of all words occuring in a specific topic within a web forum."""
	url = topicUrl
	allwords = []
	page = 1

	while len(url) > 0:
		r = requests.get(url)
		data = r.text
		soup = BeautifulSoup(data)
		for post in soup.find_all('div', class_ = "post_wrap"):
			usertag = post.find("a", class_="url")
			if usertag == None:
				user = ""
			else:
				user = usertag.text
			date = toDateTime(post.find("abbr", class_="published").text)
			posttext = post.find("div", class_="post entry-content ")
			t = [cit.clear() for cit in posttext.find_all("p", class_="citation")]
			t = [quo.clear() for quo in posttext.find_all("div", class_="blockquote")]
			allwords += [[user, date, posttext.text.strip()]]
		nextbutton = soup.find("a", rel = "next")
		if (nextbutton == None):
			url = ""
		else:
			url = replacePcts(nextbutton.get("href"))
		print(page)
		page += 1
	return allwords


def forumSection(url):
	"""Returns list of all words in all topics in a section of a web forum."""
	totalWords = []
	topicurlz = [url]
	while len(url) > 0:
		r = requests.get(url)
		data = r.text
		soup = BeautifulSoup(data)

		links = soup.find_all("a", class_="topic_title")
		for link in links:
			topicurl = link.get("href")
			if topicurl != None and topicurl not in topicurlz:
				topicurlz += topicurl
				totalWords += wordlistTopic(replacePcts(topicurl))
		nextbutton = soup.find("a", rel="next")
		if (nextbutton != None):
			url = replacePcts(nextbutton.get("href"))
		else:
			url = ""
	return totalWords

def maxovermed(x):
	"""Returns ratio of max monthly count to median monthly count of a given word.

	Intended as a stable, population size independent measure of a word's 'splashiness'.
	"""
	return np.max(x)/max(np.median(x), 1)

def aftminbef(monthsAgo):
	"""Returns a function to calculate the difference between the sum of a word's count
	before and the sum of a word's count after a given month.

	Intended as a measure of words entering or leaving the forum's vocabulary over time.
	"""
    return lambda x: sum(x[-monthsAgo:]) - sum(x[:-monthsAgo]) 

### Constructs a dataframe with word counts by month. Used to find and analyze words with time trends.

biglist = forumSection("http://forum.earwolf.com/forum/4-how-did-this-get-made/")
bigdf = pd.DataFrame(biglist)
bigdf.columns = ["_user", "_time", "_full_text"]

for post in range(len(bigdf["_full_text"])):
   postlst = [word.lower().strip(string.punctuation) for word in bigdf["_full_text"][post].split()]
   for word in postlst:
      if (word in bigdf.columns):
         bigdf[word][post] = True
      else:
         bigdf[word] = False
         bigdf[word][post] = True


wordsdf = bigdf.drop("_full_text", 1)
wordsdf = wordsdf.drop("_user", 1)
wordsdf.index = wordsdf["_time"]
wordsdf = wordsdf.drop("_time", 1)
bymonth = wordsdf.resample("m", "sum")

year = bymonth.apply(aftminbef(12), 0)
year.sort(ascending = False)

