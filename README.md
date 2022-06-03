# Biblioterra
Biblioterra is an API/Wrapper build on top of LibraryGenesis "api". It's built for educational purposes.

LibraryGenesis has no built-in API, so Biblioterra uses my fork of `grab-convert-from-libgen` instead.
Find out more about the fork:
https://github.com/Lamarcke/grab-fork-from-libgen

**See the docs:**  
https://biblioterra.herokuapp.com/v1/docs

# Disclaimer
Biblioterra is **NOT** populating any databases with LibraryGenesis data.  
Instead, we save cover *links*, search results *text*, download *links* and description *text*.  
This data is specific to each user's library.

No files, images etc. are being saved.

Biblioterra is a project from a System Analysis and Development's student.
It's built with my fellow alumni and college mates in mind.

## Caching Implementation

Biblioterra uses Redis for caching all search, cover and metadata requests.
This helps reduce the strain on LibraryGenesis servers, making new requests only when necessary.
You may check if a request is cached by checking the `cached` header on responses.

### Why Redis?
Because it's fast, like crazy fast. We are basically limited by the HTTP request speed itself.  
It's also important that we can set TTL for entries.

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
