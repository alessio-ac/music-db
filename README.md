# music-db
Python script that gets data through Discogs and stores it in a DB.

It is written with Linux in mind and might not work on Windows/Mac machines.

The script only works with master Discogs links, not for single releases.

Correct > https://www.discogs.com/master/29124-Dio-Holy-Diver

Incorrect > https://www.discogs.com/release/2428023-Dio-Holy-Diver

## Database example

```
entityId  albumName                   artistName     releaseDate  subGenre           genre  owned  pformat  url                                                         
--------  --------------------------  -------------  -----------  -----------------  -----  -----  -------  ------------------------------------------------------------
1         Rainbow Rising              Rainbow        1976         Classic Metal      Metal  0               https://www.discogs.com/master/40614-Blackmores-Rainbow-Rain
                                                                                                            bow-Rising                                                  

2         Black Sabbath               Black Sabbath  1970         Doom Metal         Metal  1      Vinyl    https://www.discogs.com/master/723-Black-Sabbath-Black-Sabba
                                                                                                            th                                                          

3         Painkiller                  Judas Priest   1990         Heavy Metal        Metal  0               https://www.discogs.com/master/26296-Judas-Priest-Painkiller

4         Epicus Doomicus Metallicus  Candlemass     1986         Doom Metal         Metal  1      Vinyl    https://www.discogs.com/master/42704-Candlemass-Epicus-Doomi
                                                                                                            cus-Metallicus                                              

5         Vector                      Haken          2018         Progressive Metal  Metal  0               https://www.discogs.com/master/1442580-Haken-Vector         
```

## Dependencies

- discogs_client

## First run

On the first run the script will create the files `music.db` and `id_list`. The former is the SQLite database, the latter a file that can be filled with masters links from Discogs.

The script requires an API key, it can be obtained by making a Discogs account and going to https://www.discogs.com/settings/developers.

## Usage

There are four modes to this script:

- Single link
- ID List
- Search
- Update

### Single link

By passing through a Discogs link as an argument it will be added to the database.

```
$ python3 music-db.py https://www.discogs.com/master/40614-Blackmores-Rainbow-Rainbow-Rising
```

It will now ask for a sub-genre, which can be selected either by entering correct number form the list, or by writing it yoursef. (When nothing is entered the option 0 will be automatically selected).

```
Adding Rainbow Rising...
0 - Hard Rock
1 - Heavy Metal
Which sub genre to insert? -> Classic Metal
```

Next it will ask for a genre in the same manner as before,

### ID List

By adding multiple master links from Discogs to the `id_list` file that was created upon the first run it will add the albums in succession.

```
https://www.discogs.com/master/723-Black-Sabbath-Black-Sabbath
https://www.discogs.com/master/26296-Judas-Priest-Painkiller
https://www.discogs.com/master/42704-Candlemass-Epicus-Doomicus-Metallicus
```

### Search

By using the `search` argument it will initiate a search sequence, where you can enter the name of an album and get a list of matching names, select with the correct number and the album will be added to the DB.

```
$ python3 music-db.py search
```
```
Connected to database
id_list file found.
Search -> Vector
```
```
0 - Haken (2) - Vector
1 - Vector-Lovers* - Vector Lovers
2 - Deck 8-9 - Vector
3 - Gilgamesh - Vector Transformation
4 - Lucifugum - Vector33
Which to chose? (input nothing to see next page) -> 0
```

### Update

By using the `update` argument the script will use the API key to check your Discogs collection and modify the `owned` and `pformat` fields in the DB accordingly. It can get very slow as it checks every single entry in the DB, but one day I will hopefully optimize it so that it only checks what's needed.
```
$ python3 music-db.py update
``` 

```
Connected to database
Updating Rainbow Rising...
Update finished.
```