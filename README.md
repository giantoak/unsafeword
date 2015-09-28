# Unsafeword
## What?
A minimal program for checking MEMEX advertisements for mentions of one of a number of known spam / porn / malware 
websites. (This could be generalized to more checks and analyses, but let's keep it simple for everyone's sake.)
 
## Design
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
* [URLBlacklist.com](http://urlblacklist.com/) (should pay a fee)
* [Shalla's blacklists](http://www.shallalist.de/) (should sign a contract?)
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