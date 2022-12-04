[![VS Code Container](https://img.shields.io/static/v1?label=VS+Code&message=Container&logo=visualstudiocode&color=007ACC&logoColor=007ACC&labelColor=2C2C32)](https://open.vscode.dev/microsoft/vscode)

## Biblioterra

A complete middle ground API for LibraryGenesis data, built for educational purposes.
LibraryGenesis has a simple API, but it doesn't meet the developers demand for searching yet.
A forum member, "Librarian" contacted me about the possibility of a new API being developed, so i hereby invite everyone
that is interested in developing something on the core of the libgen data to give the thread a read.
It's here:  
[[call for developers!] A new API is on its way](https://forum.mhut.org/viewtopic.php?f=17&t=11192)

Biblioterra uses my fork of [grab-convert-from-libgen](https://github.com/willmeyers/grab-convert-from-libgen), from `Willmeyers`.  
Find out more about the fork:  
<https://github.com/Lamarcke/grab-fork-from-libgen>

`Willmeyers` laid out an incredible foundation on his library, so he's part of the reason this project is possible.

Right now, the project is in a "completed" state, where everything that we wanted is implemented.
Still, some pieces of code can be improved and there's always bugs to fix.
PRs are very welcome.

**See the docs:**  
<https://biblioterra.herokuapp.com/v1/docs>

## Disclaimer

Biblioterra is **NOT** populating any databases with sensitive LibraryGenesis data.  
Instead, we save cover *links*, search results *text*, download *links* and description *text*.
All links redirect to their LibraryGenesis counterpart. (e.g. Download links redirect to librarylol)

No files, images etc. are being saved.

With this in mind, i ask that this project is not modified to be used as an database populating tool.

#### Something to keep in mind

LibraryGenesis **will** temporarily block you if you abuse their servers. So please use this with care.
The default limit for Biblioterra's endpoints is 1 request every 1,5 seconds.

**Important**:  
Metadata routes now return actual relevant metadata.  
Download links has been moved to it's own route.  
Please check the docs for more info.

Bugs in this project are mostly related to [grab-fork-from-libgen](https://github.com/Lamarcke/grab-fork-from-libgen)  
So if a route is not returning what you expect it should, it's probably a change on Libgen side that wasn't reflected on the scraping library.

### What can it do?

Right now, Biblioterra can do most of what you would expect from a book suite backend/API.
You can search books, articles, and everything that's on LibraryGenesis.  
You can then filter your search using queries, and while you're at it, why not add a book to a user's library, so he may download it and keep track of it later?

## **Installation**

### **Automatic**

This is the recommended method. It ensures you have a consistent development enviroment with the rest of the
contributors.  
This method is powered by VS Code's Dev Containers.

Using this method you:
- Can be sure your development experience will be seamless
- Reduce the number of problems related to enviroment setup
- Can get working in a matter of minutes

First, install [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed in your machine.  
If you are on Windows, it's highly recommended to enable [WSL](https://learn.microsoft.com/en-us/windows/wsl/install)

Then, simply open this project using [VS Code](https://code.visualstudio.com/).  
The editor will prompt you to install "Remote - Dev Containers" and to "Reopen in Dev Container".

This installation provides you with a clean Python3.10 image, with Poetry, MySQL, MongoDB and Redis pre-installed.  
It also features default env variables so you can get running as soon as you open the container.

### **Manual**

You need to have the following dependencies installed before starting:  
Python 3.10  
Poetry (a dependency manager)  

MySQL 8.1  
MongoDB  
Redis  

There's plenty of articles about how to install each one.  

After you have everything installed:  
*Make sure you have Poetry installed.*  
`cd biblioterra`  
`poetry install`  

Now, you will need to set up the enviroment variables. They are as follows:  
`REDIS_URL`: The url to your redis instance.  
`MONGODB_URL`: The url to your mongoDB instance.  
`JWT_SECRET`: The string which will be your JWT secret, make sure to use a cryptography library.  
`JWT_ALGORITHM`: The algorithm you are going to use for JWT token generation.
`EMAIL`: The email account from which Biblioterra will send it's password recovery emails.  
`EMAILPASS`: The email's password.  
`SITE_URL`: The url at which your frontend is deployed, this is only used in password recovery emails.  

### A bit of thanking

I learned a great ton of Python from messing around in [Willmeyers](https://github.com/willmeyers) codebase, and it's funny to me how a guy that never once saw me was a bridge in my learning process.  

Thank you, the amazing people at LibraryGenesis, and the amazing people on my country, Brazil, who have had nothing but love to show for this project.  
I do hope it goes way beyond the scope it has now, because it's a project i've been wanting to make since my first days of reading on a screen.

Developers aside, there are three people i couldn't thank enough, and are the reason this was made possible.  

**My son**  
How can something so small have this much impact on someone's life?  
You still don't know what you want, or when you want it, the only thing you do most of the day is sleep.  
But seeing you learn one thing a day, everyday, showing us the most beautiful smile on Earth, is what gives me the strength to go on.  
You will always be my treasure, and i hope that i can show what i was doing while you were sleeping on your first year soon. I love you.  

**My dearest friend**
The most important person on this project, and yet, she didn't write a single line of code.  
If it wasn't for you, the first Bibliomar would be just a single search bar, that returns a table with almost no content, on a white screen.  
I hope you know that you are the most important woman in my life, and the place you have in my heart can't be taken by no one else.  

**My dad**  
I know that it's hard to trust a career like this in a third world country, but you've been doing it.
I thank you very much for everything you have done, not only for me, but for your grandson as well.  

## Caching Implementation  

Biblioterra uses Redis for caching all search, cover and metadata requests.
This helps reduce the strain on LibraryGenesis servers, making new requests only when necessary.
You may check if a request is cached by checking the `cached` header on responses.

### Search Cache  

By default, search results are cached for 24 hours.  
The cache works like this:  
`search:{search_parameters}`  
Where `search_parameters` is a json string of the search_parameters used in the query.  
This means cache is absolute query specific. e.g.: Searching for "Pride and prejudice" with "epub" format uses a different cache than searching "Pride and prejudice"
with "pdf" format, and so on.  
The value is a json string of the search_parameters.

### Cover Cache  

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
