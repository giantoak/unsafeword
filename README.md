# Unsafeword
## What?
A minimal program for checking MEMEX advertisements for mentions of one of a number of known spam / porn / malware 
websites. (This could be generalized to more checks and analyses, but let's keep it simple for everyone's sake.)
 
## Current Implementation

At present, Unsafeword runs as a Flask app with two endpoints:
* `isi/[uri]` takes a URI in ISI's Elasticsearch database (generally a complete URL), queries the DB to get back the 
text associaed with the add, and parses and returns any located spam entries.
* `raw/[text]` takes a string and parses and returns any located spam entries.

Output is formatted as a JSON. The basic structure is:
```
{
  'identifier': [Dictionary of identifiers fed to Unsafeword]
  'matches': { 'spam_flag': [True or False],
               [spam/porn url in ad]: [blacklists on which the spam/porn url appears],
               [spam/porn url in ad]: [blacklists on which the spam/porn url appears],
               ...
             }
}
```

## Designing for the future...
**This may change.** At present, the plan is to:

### Get historic data
* Get the ISI clustering of ads-by-identical-bags-of-words
* Get an ad for each cluster, and mark whether or not it contains a bad URL
* Throw that cluster into a database, tagging it as bad/good.
* Throw that ad into a database tagging it as bad/good.

### Streaming in new data
* Periodically query the ISI endpoint for advertisements that have been recently added.
* If the new ads fall into a known cluster, either ignore (lazy analysis) or put the ad into the DB.
* If the new ads fall into a new cluster, parse the ad text and throw the cluster (and the ad) into the DB.

### Returning results
* If the ad is in the DB, return the result.
* If the ad isn't in the DB, check the list of clusters.
 * If it's in the list of clusters, get the cluster's value and return that.
 * If it isn't in the list of clusters, parse the text and return that. Save it to the DB?
 
## Potential Design Changes
* Do we really need an ad DB? Can we just track clusters and rely on ISI's front end?


## Current sources of Porn / Malware listings
### Malware, spam, etc.
* [Spamhaus](https://www.spamhaus.org/)?
* [SURBL](http://www.surbl.org/)?
* [Spamdex](http://www.spamdex.co.uk/)
* [jwSpamSpy](http://joewein.net/bl-log/bl-log.htm)
* [URLBlacklist.com](http://urlblacklist.com/) (This list can be downloaded *once* for free; for future downloads, 
we'll need to pay a token fee.)
* [Shalla's blacklists](http://www.shallalist.de/) (Commercial usage requires a signed contract)
* [MESD Blacklists](http://www.squidguard.org/blacklists.html)
* [MalwareDomains.com](http://www.malwaredomains.com/)

### Porn site aggregators
* gotblop.com
* iwantporn.net
* joespornlist.com
* mypornbible.com
* sexpornlist.com
* sexpornlist.net
* tblop.com
* theporndude.com
* thepornlist.com
* thesafeporn.com
* toppornsites.com
* zwei.in


## Things to do before taking this repo public:
This repository **includes passwords for MEMEX elasticsearch endpoints.** Those should be stripped out.