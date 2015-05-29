import pandas as pd
import string

## Once scraping is done, this script compares two different forum scrapings for largest differences in n-gram counts.
## For instance, could find buzzwords present in conservative but not liberal forums and vice versa.

def ngrams(wordlst, n):
	"""Returns dictionary of all n-grams counts taken from wordlst."""
	counts = {}
	for i in range(len(wordlst)  + 1 - n):
		key = wordlst[i]
		for j in range(i + 1, i + n):
			key += " " + wordlst[j]
		key = key.lower()
		if key in counts.keys():
			counts[key] += 1
		else:
			counts[key] = 1
	return counts


def countsDF(bigstring):
	"""Returns DataFrame of 1, 2 and 3-grams stripped from the large string of all forum text."""
	bigstring = bigstring.lower()

	bigwordlist = bigstring.split()
	bigwordlist = [word.strip(string.punctuation) for word in bigwordlist]
	grams1 = ngrams(bigwordlist, 1)
	grams2 = ngrams(bigwordlist, 2)
	grams3 = ngrams(bigwordlist, 3)

	df1 = pd.DataFrame(grams1, index = [1]).transpose()
	df2 = pd.DataFrame(grams2, index = [1]).transpose()
	df3 = pd.DataFrame(grams3, index = [1]).transpose()

	df = df1.append(df2)
	df = df.append(df3)
	df = df.sort([1], ascending = False)
	return df


### read in string of all forum text from two different forums, outer join the two count data frames
cbbfile = open("C:/Users/Harry/Dropbox/BACKUP/Fall14/Misc/DataFun/CBBbigstring.txt", 'rb')
cbbbigstring = cbbfile.read().decode()

bbtfile = open("C:/Users/Harry/Dropbox/BACKUP/Fall14/Misc/DataFun/BBTbigstring.txt", 'rb')
bbtbigstring = bbtfile.read().decode()

cbb = countsDF(cbbbigstring)
bbt = countsDF(bbtbigstring)

both = pd.concat([cbb, bbt], axis = 1, join = 'outer')
both.columns = ["cbb", "bbt"]

onlybbt = both[pd.isnull(both["cbb"]).as_matrix()].sort('bbt', ascending = False)
onlycbb = both[pd.isnull(both["bbt"]).as_matrix()].sort('cbb', ascending = False)

### Calculate standardized difference between word counts to find n-grams specific to one forum.
bothz = both.fillna(0)
sub = bothz["cbb"] - bothz["bbt"] * bothz["cbb"].sum()/bothz["bbt"].sum()
sub.columns = ["diff"]
sub.sort("diff", ascending = False)
