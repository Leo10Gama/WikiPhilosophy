# WikiPhilosophy
There's an old internet adage that, if you click on the first non-parenthesized, non-italicized link on a Wikipedia page, ignoring external links or links that don't lead to existing pages (red links), you'll eventually end up on the Wikipedia page for [Philosophy](https://en.wikipedia.org/wiki/Philosophy). In fact, there's even a [Wikipedia page](https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy) describing this exact game!

**I know it's not proper "GitHub etiquette" to write a long-winded README, but since this is just a side-project that I don't intend to scale beyond my own entertainment, I'm going to use this file as a way to document my process.**

Given the nature of the method, I wanted to try my hand at coding a way to automatically compute the path from a given page to "Philosophy", if it exists. However, I wanted to take it one step further and preprocess everything. While Wikipedia is an everchanging database of information, constantly being updated, with new pages being created and deleted, new links being added or removed, I wanted to at least make an effort to capture the results at one given time (which turned out to be between December 9 to December 15). As such, the "cache" folder of this project is representative of Wikipedia articles of that timespan. I would love to have it consistently update with the correct information, but parsing over six million Wikipedia articles on a ThinkPad laptop isn't exactly *efficient*, even using multiprocessing. In fact, it took me about a day to retrieve a list of all the articles, and over a week to get the first link they point to!

### Table of Contents
* [Methodology](#methodology)
* [Pitfalls](#pitfalls)
* [Functionality](#functionality)
  * [Getting to Philosophy](#getting-to-philosophy)
  * [Distance to Philosophy](#distance-to-philosophy)

## Methodology
The first step of this process was finding a consisent way to get a list of all existing English Wikipedia articles. This was difficult at first, but fortunately there is a Wikipedia page for [all English articles](https://en.wikipedia.org/w/index.php?title=Special:AllPages). Each page contains about 200 or so links, with some being redirects (those in italics). Unfortunately for me, I could not use multiprocessing to scrape these pages, as the links that show on the next page are dependent on the current page (evidenced by the nature of the title, adding the extension `&from="page"`). While the exact amount of pages on Wikipedia differs from day to day, I had scraped it when there were 6,583,099 articles. The actual number for this project is likely smaller, as some articles that had been listed no longer exist, and newer articles were not added.

To store these articles in the most useful way, I kept them in a **dictionary** format, with the key being the title of the article, and the value being the link to the article. When this process was completed, I exported the result in JSON format to a file called `articles.json`. This file is not visible in the repository, as the resulting JSON was about **533 MB large**, and GitHub has a 100 MB file upload limit. Thus, I broke the file into 28 separate JSON files, each corresponding to the starting letter of the article, from letters A-Z, as well as files for articles starting with numbers and articles starting with anything else.

After each article was parsed, I had to create an "edge" to connect it to the first article it links to. This was done by creating yet another dictionary, this one linking the title of the article in question to the title of the first article it links to. This was by far the most tedious process; while the articles could be scraped in bundles between 50-200 in size, the edges have to be created by visiting each article *one at a time*, which means one server request per article, instead of one per batch of up to 200. However, since I had the list of articles already created (and sorted into separate files), I was able to use multiprocessing to parallelize the process. *Side note: it also let me see that over 25% of articles on Wikipedia start with either the letter A, C, M, or S, with S having the most articles!*

Since this had to be done over a long stretch of time, and I still have final assignments to complete for school, I needed to ensure there was a consistent way to stop and start this process. Initially, I tried placing the whole function in a try-except to catch the keyboard interrupt, but occassionally it would stop execution while one thread was mid-write. Eventually, the most consistent (and quickest) fix I could find was to turn off my computer's Internet connection, creating an HTTP connection error, which would cause each thread to write to file, and *then* use an interrupt. In addition, I kept a separate folder on-hand of each file's progress, that I would update before ending execution to make sure files didn't get overwritten with nothing (which did happen for the first few iterations).

After about a week of initial testing (currently 12/21/22), I decided to make one more pull to try getting any new articles that may have been created, as well as renaming any articles that could have been renamed. Pulling every article a second time took an afternoon, but updating everything took a surprising 20 minutes to complete, which I believe goes to show the remarkable effort put forth by Wikipedians to keep information on the site updated, accurate, and relevant.

## Pitfalls
There were various issues that I encountered trying to get the parser to work, as it's impossible to account for absolutely every edge case in a project like this.

My first issue was that some articles with valid, non-parenthesized links, wouldn't get picked up by the parser. This was a quick and easy fix, since previously the script would only iterate through `<p>` tags, while those links were embedded in `<li>` tags. As such, I took the main functionality of the parsing method and generalized it to deal with a batch of tags. That way, I could call it for both `<p>` tags, as well as `<li>` tags.

Another issue I ran into after finishing up the primary functionality was that a lot of articles had their first link set to the page for [Geographic coordinate system](https://en.wikipedia.org/wiki/Geographic_coordinate_system). After doing some investigation, I found that this was because, for Wikipedia pages about locations, a small paragraph tag is included at the very top right corner of the page, indicating the location's global coordinates. Fortunately, this was a quick fix. Since the tags contained a `<span>` with the ID "coordinates," I could just skip over any tag that had a child tag with this ID. Making use of my cleanup method, I was also able to remove the faulty connections by name, and running the main algorithm one more time (for about 15 minutes or so), I was able to refresh those connections.

In addition, some articles along the critical path to Philosophy (namely, articles for [Logic](https://en.wikipedia.org/wiki/Logic) and [Reason](https://en.wikipedia.org/wiki/Reason)) would point to the incorrect article [Religious philosophy](https://en.wikipedia.org/wiki/Religious_philosophy). Looking into this, I found that they were scraping these values from the infobox table, as it had a single paragraph tag inside of it that was appearing first in the hierarchy. Since I'm not looking for links in tables anyways, I simply removed all table tags before beginning parsing, which seemed to fix the issue. However, to go back and rescrape every article again would likely take another week, so I'll tweak these on a case by case basis as I test pages. Interestingly, this issue also seemed to affect some pages that contained presidential or otherwise notable signatures, as they would be contained in `<a>` tags, with a proper title, though that title would simply read "\[Person\]'s signature", and would cause an error when trying to traverse the data, as those pages do not exist.

## Functionality
Below are some of the functions and fun games I've made using this dataset.

### Getting to Philosophy
Contained in `get_to_philosophy.py` are the necessary methods to enter in a Wikipedia article's title, and have a path found from that article to reach either Philosophy, or loop around somewhere. Most articles will eventually reach Philosophy, though there are some that will end up looping back in on themselves (interestingly, [Mathematics](https://en.wikipedia.org/wiki/Mathematics) (as of 12/15/22) loops in on itself, with its path going to [Number theory](https://en.wikipedia.org/wiki/Number_theory), [Pure mathematics](https://en.wikipedia.org/wiki/Pure_mathematics), and then back to Mathematics!). Thanks to all articles being stored in a dictionary, paths can be generated incredibly quickly, which means not waiting for dozens of requests to get back to get an answer. 

Below are some example paths generated to either get to Philosophy, or loop.
![Path from Leonardo da Vinci to Philosophy](https://user-images.githubusercontent.com/51037424/208314289-510f469f-4795-41ce-a19d-80ca7614882f.png)

![Random path from Nordic combined at the 2018 Winter Olympics - Individual large hill/10km to Philosophy](https://user-images.githubusercontent.com/51037424/208314539-6f6f98b9-e09e-44c1-95eb-9685a6d7fd8a.png)

![Path from Python to Philosophy](https://user-images.githubusercontent.com/51037424/208314479-d1b290bd-f42d-4743-a26c-1ee053a6e25e.png)

![Path from Python (programming language), looping at Mathematics](https://user-images.githubusercontent.com/51037424/208314415-10ae62bd-6bc2-4ae1-bd74-9fe523dd0639.png)

### Distance to Philosophy
In the `distance_to_philosophy.py` there are the necessary methods to compute the distances from an arbitrary article to Philosophy. This took a few iterations to get correct.

Initially, I took the naïve approach of going one by one, in a breadth-first search style function to retrieve every article that points to Philosophy, adding those to a queue, and incrementing a counter. However, going one at a time was taking a very long time, so I tried instead using *batches* of articles. That is, when I compute the articles that point to Philosophy, I instead store that list in the queue, and use list comprehension to get the correct items. While this seemed to go faster, after timing each batch, it seemed to increase exponentially, with the first batch (only Philosophy) taking 0.26s to parse, the second batch (969 articles) taking almost a minute, the third batch (3310 articles) taking over five minutes, and the fourth batch (7104 articles) taking about 12 minutes. This was clearly only going to get worse, and since there are over six million articles to parse, I needed to come up with a more efficient method.

Eventually I realized that the bottleneck of this method was the fact that accessing the *values* of a dictionary, and comparing them to the ones already seen, was likely taking O(*n*²) time, due to the fact that it was not only iterating through every item in the dictionary, but also comparing it to each item in the batch. To get around this, I created a **reverse dictionary**, which links a given article to a set of every article that links to it. Using this, access to all articles linking to a given page could take O(1) time, at the expense of using additional space to store a duplicate dictionary.

This method was looking promising initially, when it generated the first dozen or so batches in a few seconds, but when it reached "Batch 219", I started to get suspicious. As it turns out, I wasn't accounting for duplicate iterations, or loops of articles. Thus, eventually articles would loop back in on themselves, and it would continue counting forever. The simple fix to this was to remove the dictionary entry once I finished reading it, to ensure it's not read multiple times over. Once this was finished, the dictionary keeping track of distances would only be populated with those articles that linked to Philosophy, and as such, I could compare the size of this dictionary with the size of the original to see how many articles link to Philosophy. At the time of initially running this code, about 92.55% of articles linked to Philosophy, which is lower than what is stated on Wikipedia for 2011 (94.52%) and 2016 (97%). While I'm not certain what this could mean, I want to attribute this to the fact that some articles were parsed incorrectly, and while this percentage would likely be larger if I reparsed everything again with this fixed function, it would also take a very long time. As such, I'm content with cleaning out these outliers on a case-by-case basis as I test through random articles.

![Generating batches](https://user-images.githubusercontent.com/51037424/208314670-7e3b8e52-1707-4412-885b-12e50422b22b.png)

![Leonardo da Vinci distance](https://user-images.githubusercontent.com/51037424/208314717-719a8aba-7aa1-4092-8684-c3040b5cadcf.png)

Later, I wanted to implement functionality that would allow the user to move up and down a given article's path, in a way traversing the tree in a given direction to see how deep the branch goes. Upon initial implementation, I was able to move forwards through the tree (towards Philosophy) just fine, but the reverse operation was giving me a "None" output. After doing some investigation, I realized this was because, to calculate the distances, I was removing the item from the initial dictionary, which meant any time I called `compute_distances(reverse_edges="Something")`, the reversed edges would get completely wiped. The simple solution (and, admittedly, first solution I should've thought of) was to just keep a set of all seen elements. Since checking whether an element is in a set is Θ(1), it shouldn't affect runtime any more than removing an element from a dictionary.

![Traversing forward and backward from Amazon Web Services](https://user-images.githubusercontent.com/51037424/208315025-88a455ef-7040-4cf5-be63-cdc45d9514d3.png)

An interesting side-issue that I came across with this second, traversal functionality, is that if you continue approaching Philosophy, the program will not say that "Philosophy is 0 articles away from Philosophy", but instead turns into 15 (at the time of writing). This is because Philosophy has a loop with itself, where it links to [Existence](https://en.wikipedia.org/wiki/Existence), [Reality](https://en.wikipedia.org/wiki/Reality), and so on, until wrapping back around at Philosophy!

![Philosophy is 15 articles away from Philosophy](https://user-images.githubusercontent.com/51037424/208314948-cde53193-6065-4793-b548-127e823c9ca4.png)

The next part of the function I wanted to add would allow for articles to be queried by their numerical distance to Philosophy. This would let users see what types of articles are X length from Philosophy, and by tracing their paths, likely see why. Doing so was fairly simple with list comprehention: find every key in the dictionary of distances with a distance of X, and pick one at random. This actually very quickly yielded a satisfying result!

![Query article 26 away from Philosophy, Robert Stuart](https://user-images.githubusercontent.com/51037424/208526888-a062804a-937e-4c21-9c2b-6bf23928b342.png)

However, I quickly found the compounding result of my earlier ignorance to not eliminate table values entirely, as I came across the article [1995 in Denmark](https://en.wikipedia.org/wiki/1995_in_Denmark), which linked to [1994 in Denmark](https://en.wikipedia.org/wiki/1994_in_Denmark), and so on and so forth until it eventually reached a correct result. Thus, another cleanup was in order, which involved many similar articles with chronological tables of this nature.

Through this new system, I was able to see that (as of 12/19/22) the longest path to Philosophy is from the article [Parmouti 12](https://en.wikipedia.org/wiki/Parmouti_12), with a whopping length of **241 articles**. After double checking, I could see this was the real correct answer, as the series of articles about the [Coptic calendar](https://en.wikipedia.org/wiki/Coptic_calendar) begin with three unique links: one to the previous day of the calendar, one to the actual Coptic calendar article, and one to the next day of the calendar. As such, it takes the path backwards through the calendar until it reaches a link to a page that doesn't exist (Nesi 6), and then links to the Coptic calendar, which eventually takes it to Philosophy. The next longest non-Coptic calender article that leads to Philosophy is [Eochaid Gonnat](https://en.wikipedia.org/wiki/Eochaid_Gonnat), a medieval high king of Ireland, with a path of **46 articles** before reaching Philosophy. The reason for *this* also being so long is due to the fact that the series of articles for medieval nobles of Ireland tend to start with the sentence "X, son of Y", with Y being the first link to their ascendant. As such, this path goes up the lineage until reaching the page for [Origin myth](https://en.wikipedia.org/wiki/Origin_myth), which eventually connects to Philosophy.

![Parmouti 12 is 241 articles away from Philosophy](https://user-images.githubusercontent.com/51037424/208527031-8ace2b55-70eb-47e2-9338-c0c33487dd06.png)

![Eochaid Gonnat is 46 articles away from Philosophy](https://user-images.githubusercontent.com/51037424/208527133-8b537a8e-1e41-419f-abcd-b8f6a4b1fc75.png)

Next, I wanted a quick and easy way to actually select the articles instead of them being random. Since I already had an option-selecting function in my [RyuNumber](https://github.com/Leo10Gama/RyuNumber) project, I decided to reuse some of the code here to simplify the process. As such I can now list and select articles that link to a current article (if they exist), as well as list off all articles at a given distance from Philosophy!

![Moving backwards, with menu, from Justin Trudeau](https://user-images.githubusercontent.com/51037424/208974453-64b1008f-26ef-4446-b88d-927bf1db3245.png)

![Select Automatic data processing, 35 articles from Philosophy](https://user-images.githubusercontent.com/51037424/208974742-5b52e534-dcd5-4db1-990e-37ba0187a7da.png)

As a last cleanup, I went through every article that previously did not connect to Philosophy, with the hopes of getting a different outcome for most of them to clean up any incorrect paths that were the result of poor initial coding. After this new batch of cleaning up, the number of articles that linked to Philosophy increased to **94.50%**, indicating that my initial guess that the previous, lower percentage was due to articles being initially parsed incorrectly. I can also place a half-decent guess that the reason this percentage is lower than the previous recorded peak in 2017 is likely due to the loop at Mathematics, as many articles related to topics both in that field, as well as programming, end up linking there. It's possible that in previous years, this loop didn't exist, and thus more articles were able to reach Philosophy through Mathematics.

### Race to Philosophy
Enclosed in the `race_to_philosophy.py` file are methods for the primary reason I wanted to go about this project: betting which article out of a list would reach Philosophy first! 

The setup for this method was fairly simple, since it mostly just involved getting a random article and marching along the pre-computed edges of that article until either Philosophy is reached, or all articles in the race loop. With the straightforward implementation completed, all that was left to do was run a few races and try looking for patterns in the winners.

![Race between Beat Rhythm News and Personal finance](https://user-images.githubusercontent.com/51037424/209398889-3a360c18-693d-4867-b1b2-ffbc6d8582f2.png)

![Tie between Jesús Conde and Māori loan affair](https://user-images.githubusercontent.com/51037424/209398744-396ca6a1-08a1-485d-8bda-40b110456d84.png)

With the base implementation complete, I also wanted to add the flexibility to have as many racers as the user wanted, which was surprisingly easy to do thanks to early design decisions in my implementation.

**TODO: pic of race with multiple people**

Interestingly, in the above image, all paths eventually converged at [Science](https://en.wikipedia.org/wiki/Science), which meant that one could see the result of the race as soon as all of the racing articles reached it. In addition, the more racers there are, the quicker one seems to reach a winner, which I suppose makes sense given that more articles leads to a higher chance that one article is naturally closer to Philosophy than the others.
