LibraryGenesis has no built-in API, so Biblioterra uses my fork of `grab-convert-from-libgen` instead.
Find out more about the fork:
https://github.com/Lamarcke/grab-fork-from-libgen

Right now, the project is in a "completed" state, where everything that we wanted is implemented.
Still, some pieces of code can be improved and there's always bugs to fix.
PRs are very welcome.

**See the docs:**  
https://biblioterra.herokuapp.com/v1/docs



### Can i use it anywhere?
Biblioterra was made as an api for a future React rewrite of my "Bibliomar" project, but there's no need to actually use this along with it.  
v1 routes are mostly unrelated to this other project, so you can still use it, and it will never go out of date. 
Still, with v2 and on, we will be shifting development to better answer Bibliomar's demands.  
This increase in version doesn't mean v1 is going out of date, in fact, we don't plan on updating v1 routes, because they don't need it.

# Disclaimer

Biblioterra is **NOT** populating any databases with sensitive LibraryGenesis data.  
Instead, we save cover *links*, search results *text*, download *links* and description *text*.
These are only used for caching porpuses.
All links redirect to their LibraryGenesis counterpart. (e.g. Download links redirect to librarylol)

For user libraries, we save a given file's:  
Title and topic.

No files, images etc. are being saved.

Biblioterra is a project from a System Analysis and Development's student.
It's built with my fellow alumni and college mates in mind.

#### Something to keep in mind:
LibraryGenesis **will** temporarily block you if you abuse their servers. So please use this with care.
The default limit for Biblioterra's endpoints is 1 request every 1,5 seconds.

## What can it do?
Right now, Biblioterra can do most of what you would expect from a book suite backend/API.
You can search books, articles, and everything that's on LibraryGenesis.  
You can then filter your search using queries, and then filter these results using your own
filters.
And while you're at it, why not add a book to a user's library, so he may download it and keep track of it later?

## How does it work?
There's some abstraction going on here, but Biblioterra is an API build to serve my fork of `grab-convert-from-libgen` 
over the web, which in turn is a wrapper on top of LibraryGenesis "API" (LG has no API, so we are basically web scraping.)
As the end-user, you don't need to worry about this, and all you need to use Biblioterra is to make requests to the api's
endpoints.

## How do i use it?
The docs are your friend:
https://biblioterra.herokuapp.com/v1/docs  

Biblioterra is hosted on Heroku's free tier and only allows request from `localhost:3000`.  
If you want to use Biblioterra in your website/app/service, please host it yourself.  

Just keep in mind you are using a free service that doesn't demand an api key.  

## The whys and the hows

### Why Python?
Bibliomar's original project had a backend written in python, using FlaskAPI.

## Caching Implementation

Biblioterra uses Redis for caching all search, cover and metadata requests.
This helps reduce the strain on LibraryGenesis servers, making new requests only when necessary.
You may check if a request is cached by checking the `cached` header on responses.

### Why Redis?
Because it's fast, like crazy fast.  


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

