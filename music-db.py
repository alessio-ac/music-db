import discogs_client, sqlite3, requests, os, sys, re, time


DISCOGS_API_KEY = str(os.getenv('DISCOGS_API_KEY')) # You can find this on discogs.com/settings/developers
DB_NAME = "music2.db" # Set the name of the database file

def clear_line(n=1):
    LINE_UP = '\033[1A'
    LINE_CLEAR = '\x1b[2K'
    for i in range(n):
        print(LINE_UP, end=LINE_CLEAR)

def stripString(string):
    special_characters = ['!','#','$','%', '&','@','[',']',' ',']','_','-']
    for i in special_characters:
        string = string.replace(i,'')
    return string.lower()

def genreCheck(subGenre):
    genre = ""
    if "numetal" in subGenre:   genre = "Nu Metal"
    elif "metal" in subGenre:   genre = "Metal"
    elif "rock" in subGenre:    genre = "Rock"
    elif "blue" in subGenre:    genre = "Blues" 
    elif "country" in subGenre: genre = "Country"
    elif "jazz" in subGenre:    genre = "Jazz"
    elif "electronic" in subGenre: genre = "Electronic"
    elif any(x in subGenre for x in ["punk","hardcore","crust"]): genre = "Punk"
    elif any(x in subGenre for x in ["hiphop","rap"]): genre = "Hip Hop"
    
    chooseGenre = input(f"Is the genre correct? -> {genre} -> ")
    if chooseGenre != "":
        genre = chooseGenre
    return genre

def getGenre(master):
    if master.styles == None:
        print("Couldn't find the correct genres...")
        subGenre = input("Insert the sub genre -> ")
        genre = genreCheck(stripString(subGenre))
        if stripString(genre) == stripString(subGenre):
            subGenre = None
    else:
        for i in range(len(master.styles)): print(f"{i} - {master.styles[i]}")
        chooseSub = input("Which sub genre to insert? -> ")
        if chooseSub == "":
            subGenre = master.styles[0]
        elif chooseSub.isnumeric():
            subGenre = master.styles[int(chooseSub)]
        else:
            subGenre = chooseSub
        genre = genreCheck(stripString(subGenre))

    return [subGenre, genre]

def collectionCheck(collection, master):
    for item in collection.collection_folders[0].releases:
        if master.title == item.release.title:
            owned = 1
            pformat = item.release.formats[0]['name']
            break
        else:
            owned = 0
            pformat = None
    
    return [owned,pformat]

def getMasterId(url):
    try:
        splitUrl = url.split("-")[0]
        return "".join(re.findall(r"\d", splitUrl))
    except:
        return url

def getMasterData(master,release):
    print(f"Adding {master.title}...")
    mainList = [master.title]
    if release.artists[0].name[-1] == ")":
        mainList.append(release.artists[0].name[:-4])
    else:
        mainList.append(release.artists[0].name)
    mainList.append(release.year)
    mainList.extend(getGenre(master))
    mainList.extend(collectionCheck(collection, master))
    #rl = "https://www.discogs.com" + master.url
    mainList.append(master.url)

    return mainList

def updateDatabase(cursor,collection):
    cursor.execute(f"""SELECT * FROM ALBUMS""")
    data = cursor.fetchall()
    for dbAlbum in data:
        print(f"Updating {dbAlbum[1]}...", end=clear_line())
        for collAlbum in collection.collection_folders[0].releases:    
            if collAlbum.release.artists[0].name[-1] == ")":
                collArtist = collAlbum.release.artists[0].name[:4]
            else:
                collArtist = collAlbum.release.artists[0].name
            if dbAlbum[1] == collAlbum.release.title: #and dbAlbum[2] == collArtist:
                if dbAlbum[6] == 1 and len(dbAlbum[7]) > 8:
                    dbFormat = dbAlbum[7]
                elif dbAlbum[6] == 1 and dbAlbum[7] != collAlbum.release.formats[0]['name']:
                    dbFormat = f"{dbAlbum[7]} + {collAlbum.release.formats[0]['name']}"
                else:
                    dbFormat = collAlbum.release.formats[0]['name']
                cursor.execute(f"""UPDATE Albums SET owned = ?, pformat = ? WHERE entityId = ?""", [1, dbFormat, dbAlbum[0]])
  
    print("Update finished.")

def discogsSearch(discogsConn, userInput):
    results = discogsConn.search(userInput, type='master')
    start = 0
    end = 5
    while True:
        for i in range(start,end):
            print(f"{i} - {results[i].title}")
        ans = input("Which to chose? (input nothing to see next page) -> ")
        if ans == "":
            return results[1].id
        elif ans.isnumeric():
            return results[int(ans)].id
        else:
            start += 5
            end += 5
            continue

def connectDB(db_path):
    global fileDB, cursor
    fileDB = sqlite3.connect(db_path)
    cursor = fileDB.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    if not tables:
#        with open("music_db_creator.sql", "r") as sql_file:
#            sql_script = sql_file.read()
        sql_script = """
        PRAGMA encoding="UTF-8";

        CREATE TABLE Albums (
            entityId INTEGER PRIMARY KEY AUTOINCREMENT,
            albumName TEXT NOT NULL,
            artistName TEXT NOT NULL,
            releaseDate TEXT(4) NULL,
            subGenre TEXT NULL,
            genre TEXT NULL,
            owned INTEGER NOT NULL,
            pformat TEXT NULL,
            url TEXT NULL
        );
        """
        cursor.executescript(sql_script)
        print("Database has been created.")
    print("Connected to database")


def createIdListFile():
    try:
        with open("id_list", "x") as f:
            pass
        print("id_list has been created.\nYou can now add Discogs master links to the file.")
    except:
        print("id_list file found.")

connectDB(DB_NAME)
createIdListFile()

discogsConn = discogs_client.Client('ExampleApplication/0.1', user_token=DISCOGS_API_KEY)
collection = discogsConn.identity()


if len(sys.argv) == 2:
    if len(sys.argv[1]) > 35:
        urlList = [sys.argv[1]]
    elif sys.argv[1] == "search":   # Allows to search for an album to add
        while True:
            try:
                urlTemp = discogsSearch(discogsConn, input("Search -> "))
                break
            except IndexError:
                print("No results found, try again")
                continue
        urlList = [urlTemp]
    elif sys.argv[1] == "update":   # Update the "owned" and "pformat" fields based on the Discogs colleciton
        updateDatabase(cursor, collection)
        urlList = []
    else:
        with open("id_list", "r") as f:     # Reads from the id_list file for links to add
            urlList = f.readlines()
            if not urlList:
                print("\nThe file is empty.") 
                
else:
    with open("id_list", "r") as f:
        urlList = f.readlines()
        if not urlList:
            print("\nThe file is empty.") 
            

for url in urlList:
    os.system("clear")
    try:
        time.sleep(0.2)
        try:
            master = discogsConn.master(getMasterId(url))
            release = master.main_release
            finalList = getMasterData(master,release)
            cursor.execute(f"""INSERT INTO Albums(albumName, artistName, releaseDate, subGenre, genre, owned, pformat, url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", finalList)
        except Exception as e:
            print(e)
            break
        except KeyboardInterrupt:
            print("Process interrupted.")
            continue
    except KeyboardInterrupt:
        print("Process interrupted.")
        break


print(f"\nNumber of changes to the table -> {fileDB.total_changes}")
fileDB.commit()
print(("Closing the database..."))
fileDB.close()
