## Biblioterra
A complete middle ground API for LibraryGenesis data, built for educational purposes.
LibraryGenesis has a simple API, but it doesn't meet the developers demand for searching yet.
A forum member, "Librarian" contacted me about the possibility of a new API being developed, so i hereby invite everyone 
that is interested in developing something on the core of the libgen data to give the thread a read.
It's here:  
[[call for developers!] A new API is on its way](https://forum.mhut.org/viewtopic.php?f=17&t=11192)


Biblioterra uses my fork of [grab-convert-from-libgen](https://github.com/willmeyers/grab-convert-from-libgen), from `Willmeyers`.  
Find out more about the fork:  
https://github.com/Lamarcke/grab-fork-from-libgen

`Willmeyers` laid out an incredible foundation on his library, so he's part of the reason this project is possible.

Right now, the project is in a "completed" state, where everything that we wanted is implemented.
Still, some pieces of code can be improved and there's always bugs to fix.
PRs are very welcome.

**See the docs:**  
https://biblioterra.herokuapp.com/v1/docs


## Disclaimer

Biblioterra is **NOT** populating any databases with sensitive LibraryGenesis data.  
Instead, we save cover *links*, search results *text*, download *links* and description *text*.
These are only used for caching porpuses.
All links redirect to their LibraryGenesis counterpart. (e.g. Download links redirect to librarylol)

No files, images etc. are being saved.

With this in mind, i hereby ask that this project is not modified to be used as an database populating tool.

#### Something to keep in mind:
LibraryGenesis **will** temporarily block you if you abuse their servers. So please use this with care.
The default limit for Biblioterra's endpoints is 1 request every 1,5 seconds.

`v2` routes are/will be more specific to Bibliomar's demands.  
`v1` are still unrelated to it, and this won't change anytime soon.  

### What can it do?
Right now, Biblioterra can do most of what you would expect from a book suite backend/API.
You can search books, articles, and everything that's on LibraryGenesis.  
You can then filter your search using queries, and while you're at it, why not add a book to a user's library, so he may download it and keep track of it later?

### How do i use it?
The docs are your friend:
https://biblioterra.herokuapp.com/v1/docs  

Biblioterra is hosted on Heroku's free tier and only allows request from `localhost:3000`.  
If you want to use Biblioterra in your website/app/service/production, please host it yourself.  

Just keep in mind you are using a free service that doesn't demand an api key.  

### A bit of context
This is a huge text, full of rambling and honest thoughts about programming in general.  
Please don't mind the language, i refrain from speaking like this anywhere else other than this piece of text. Thanks for your time.

Please pay the [original project](http://bibliomar.herokuapp.com/) a visit while you are reading this.

The original project had a backend written in Python, using FlaskAPI. It was good to work it, mainly because of Flask's simplicity.  
After some time, problems in the project design started to arise. I will cite some that were most relevant:
- A user's request would put too much strain on the server.
At the time, Bibliomar (it was backend and frontend in one project) was being hosted on Heroku Free Tier. This tier gives you one 
free web dyno to work it. So i had a simple application, that would do 10-25 requests everytime the user searched for something.

- The `/cover/:md5` route accepted one md5 string as a path parameter, and returned a single url string after scraping for metadata.  
So, if a user searches for something that returns 20 results, and for every result there is, a request is made for a new cover url, in a restrained enviroment with one single worker
and limited bandwitch.


Guess what happens when you try to do anything while the app is doing it's thing on that starved single worker?  
Exactly, everything breaks. You can't access book pages because the server is overloaded. The frontend was designed in a way that you had to wait 1,5s for each entry to appear on screen.  
Why is everything purple? What was i thinking?

Well, i will stop rambling.  
You only need to know that there was this thing, called error 500, that neither Flask nor Heroku could point me out what was the actual cause.  
I spent days trying to solve it, telling people "I'm sorry, you need to reload the page several times, it works after that but i don't know why!!"  
Until it hit me, while looking at those desperate attempts of fixing the mess i made, i started thinking:  
"Well, maybe i'm just looking at the tree, and not the whole forest..."

After all this time, i can say that i was wrong, even when i was looking at the whole forest, that one tree was so big that i couldn't see nothing.  
For starters, i could possibly solve that error issue simply refactoring some of my functions to be async. 
It was a big letdown to finally announce my first project, which i built from scratch, with the help of my wife, and thinking about my soon-to-be-born son to gather resolve, simply not working.

When i was looking at how much work had to be done, to even start looking at possible results, i gave up.
Not on programming, mind you, i fucking love doing this.
I gave up because that project sucked. I couldn't look at the whole forest at that time because how is a lumberjack supposed to know how to chop a tree before even touching an axe?
It was a beginner's mistake. And one i'm really proud of.
That's why i started everything from scratch, with new technology and a new mindset, this time actually planning what would be done beforehand.

Still, life is a car with no breaks, so while i was working on this project, my wife was 7-months pregnant, and we were dealing
with life problems and trying to get by.  
Biblioterra took 1-2 months to make. Not much of actual coding, but almost 2 months in time.  
Bibliomar, the frontend, was out in like 15-20 days. I found learning React to be quite pleasant, 
it simplified some things, overcomplicated some others, but still gave me much freedom in how to tackle user interfaces.
I also have more stability these days, so focusing on coding has been easier.

Wrapping up, this is a portion of the story behind my ~~first~~ second actual project. One i'm really proud of.  

### A bit of thanking
I learned a great ton of Python from messing around in [Willmeyers](https://github.com/willmeyers) codebase, and it's funny to me how a guy that never once saw me was a bridge in my learning process.  

Thank you, the amazing people at LibraryGenesis, and the amazing people on my country, Brazil, who have had nothing but love to show for this project.  
I do hope it goes way beyond the scope it has now, because it's a project i've been wanting to see since my first days of reading on a screen.   


Developers aside, there are three people i couldn't thank enough, and are the reason this was made possible.
**My son**  
How can something so small have this much impact on someone's life?  
You still don't know what you want, or when you want it, the only thing you do most of the day is sleep.  
But seeing you learn one thing a day, everyday, showing us the most beautiful smile on Earth, is what gives me the strength to go on.  
You will always be my treasure, and i hope that i can show what i was doing while you were sleeping on your first year soon. I love you.

**My wife**  
The most important person on this project, and yet, she didn't write a single line of code.  
If it wasn't for you, the first Bibliomar would be just a single search bar, that returns a table with almost no content, on a white screen.  
I hope you know that you are the most important woman in my life, and the place you have in my heart can't be taken by no one else.

**My dad**  
I know that it's hard to trust a career like this in a third world country, but you've been doing it.  
I thank you very much for everything you have done, not only for me, but for your grandson as well.

## The whys and the hows

Read on if you are interested in reading about my 
choices in this stack, if not, please jump to the docs and start working :)


### Why Python?
The main reason is that python is just so powerful for web-scraping.
And that's what we're doing.

### Why FastAPI?
So, i had to search for a solution that:
- Native async requests  
The main reason for the rewrite was writing async code from the ground up. I knew i would be restricted to a single worker dyno in my
hosting solution, so i had to make do with what i had.


- Is fast  
I can't really understand how a project that is on a single worker with limited bandwitch can work so fast.  
Seriously, i've come to appreciate FlaskAPI response times more and more as i work with it. 
Bibliomar, the frontend portion of this project, is fast for a reason. 


- Had well-documented code  
Well, FastAPI docs are more of a big tutorial than the docs i'm used to, but it works, when you know what you are looking for.  
It has simple language, and it showed me important concepts such as password hashing and JWT.  


- Autodocs  
This was the icing on the top, not really something i was looking for at first, but when i started messing around with it, i found it was really simple
to build a well documented codebase integrated directly in your code.  

### Why Redis?
This is the main piece of the caching part of the application, and it makes it dead simple to store values that your requests even more fast.

FastAPI and Redis have made it really simple to build and scale a backend that doesn't drag the frontend down.

## Caching Implementation

Biblioterra uses Redis for caching all search, cover and metadata requests.
This helps reduce the strain on LibraryGenesis servers, making new requests only when necessary.
You may check if a request is cached by checking the `cached` header on responses.


### Search
By default, search results are cached for 24 hours.  
The cache works like this:  
`search:{search_parameters}`  
Where `search_parameters` is a json string of the search_parameters used in the query.  
This means cache is absolute query specific. e.g.: Searching for "Pride and prejudice" with "epub" format uses a different cache than searching "Pride and prejudice"
with "pdf" format, and so on.  
The value is a json string of the search_parameters.

### Cover  
By default, cover results are cached for 14 days.  
The cache works like this:  
`cover:{md5}`  
Where `md5` is the given file's md5. 
The value is a link in string format.  
There's no need to specify a topic, and we save a few bytes of memory by reducing the string size.  

### Metadata
By default, metadata results are cached for 3 days.  
The cache works like this:  
`metadata:{md5}`  
Where `md5` is the given file's md5.  
The value is a json string of the metadata results.  
There's no need to specify a topic, and we save a few bytes of memory by reducing the string size.  

#### Why not use Cache-Control?
Because letting the user decide if they want to use the cache or not is not a planned feature.  

