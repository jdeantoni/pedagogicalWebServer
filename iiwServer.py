from io import BufferedReader, BufferedWriter, TextIOWrapper
from iiwServerHelper import *


def create404Page(path: str) ->str:
    '''This function create the content of a 404 page in which it tells about the path initially asked'''
    begin: str= str('''
    <html>
        <head>
         <title>file not found</title>
        </head>
        <body>
            <p> ERROR Request:<b>''')
    
    end: str = str('''</b></p>
            <p> has not been found on the server...</p>
        </body>
    </html>''')
    return begin+path+end

def getFileExtension(path: str) -> str:
    '''Returns the exntesion of the file pointed by the path'''
    # index: int = int(0)
    # current: str = str("")
    # while (index < len(path)):
    #     if(path[index] == "."):
    #         current = ""
    #     else:
    #         current = current + path[index]
    #     index = index + 1
    # return current
    index: int = int(len(path)-1)
    res: str = str("")
    while (index >= 0):
        if(path[index] == "."):
            return res
        else:
            res = path[index] + res
        index = index - 1
    return ""

def getContentType(fileExtension: str) -> str:
    '''Returns the http content type associated to a given file extension'''
    if (fileExtension == "html" or fileExtension == "css" or fileExtension == "csv"):
        return "text/"+fileExtension
    if (fileExtension == "png" or fileExtension == "jpeg" or fileExtension == "gif" or fileExtension == "webp"):
        return "image/"+fileExtension
    if (fileExtension == "jpg"):
        return "image/jpeg"
    if (fileExtension == "txt"):
        return "text/plain"
    return "unknow type"

def isBinaryFile(path: str) -> bool:
    '''Returns True is the file is Binary, False otherwise.
    WARNING: this is done based on the file extension and consequently not safe'''
    binaryFileExtensions: list[str] = list(["png","jpeg","jpg","gif","webp"])
    fileExtension: str = getFileExtension(path)
    i : int = int(0)
    while (i < len(binaryFileExtensions)):
        if (binaryFileExtensions[i] == fileExtension):
            return True
        i = i + 1
    return False


def getPostFilePath(request: str) -> str:
    ''' returns a string with the path to the post files'''
    return "./posts"+request+".txt"

def getTitle(postPath:str) -> str:
    ''' returns a string of the title of the post at a given path'''
    if doesFileExist(postPath):
        f: TextIOWrapper = open(postPath, "r")
        allLines: list[str] = f.readlines()
        return allLines[0]
    return "post does not exist"
    
def getContent(postPath:str) -> str:
    ''' returns a string of the content of the post at a given path'''
    if doesFileExist(postPath):
        f: TextIOWrapper = open(postPath, "r")
        allLines: list[str] = f.readlines()
        res: str = str()
        i : int = int(1)
        while i< len(allLines):
            res = res+"\n"+allLines[i]
            i += 1
        return res
    return "post does not exist"

def addHtmlParagraphs(content:str) -> str:
    ''' returns a string of the content string with paragraphs tags added'''
    i : int = int(0)
    res: str = str("<p>")
    while i< len(content):
        currentCar: str = content[i]
        if (currentCar=="\n"):
            res = res+"</p>\n<p>"
        else:
            res = res+currentCar
        i += 1
    return res+"</p>"

def addHtmlBold(content:str) -> str:
    ''' returns a string of the content string with bold tags added'''
    i : int = int(0)
    res: str = str()
    insideStars: bool = False
    stringSize: int = len(content)
    while i<stringSize :
        currentChar: str = content[i]
        nextChar:str = str("")
        if (i < stringSize - 1):
            nextChar = content[i+1]
        if (currentChar == "*" and nextChar == "*"):
            if (not insideStars):
                insideStars = True
                res = res + "<strong>"
                i += 1
            else:
                insideStars = False
                res = res + "</strong>"
                i += 1
        else:
            res = res+currentChar
        i += 1
    return res

#v2: la version v1 n'a juste pas besoin d'un tagStart tagEnd car les balises sont symétriques.
def addSpecificFormatting(content:str, charToSearch: str, tagStart: str, tagEnd: str) -> str:
    ''' returns a string of the content where the content between 2 charToSearch is prefixed by tagStart and postfixed with tagEnd'''
    content += (" ") # to handle last word in bold or so
    i : int = int(0)
    res: str = str()
    insideChars: bool = False
    stringSize: int = len(content)
    while i<stringSize :
        currentChar: str = content[i]
        nextChar:str = str("")
        if (i < stringSize - 1):
            nextChar = content[i+1]
        if (currentChar == charToSearch and nextChar == charToSearch):
            if (not insideChars):
                insideChars = True
                res = res + tagStart
                i += 1
            else:
                insideChars = False
                res = res + tagEnd
                i += 1
        else:
            res = res+currentChar
        i += 1
    return res


def createBlogPage(title: str, content: str) ->str:
    '''This function create the content of a blog page in which it put the actual formated content'''
    
    content = addHtmlParagraphs(content)  
    content = addSpecificFormatting(content, "*", "<strong>", "</strong>")
    content = addSpecificFormatting(content, "/", "<i>", "</i>")
    content = addSpecificFormatting(content, "#", '<img src="./posts/', '"/>')
    
    return str('''
    <html>
        <head>
         <title>'''+title+'''</title>
         <link href="./static/css/iiwBlogStyle.css" rel="stylesheet"/>
        </head>
        <body>
            <div class="main" id="main">
                <ol class="menu">
                    <li><a href="/">home</a></li>
                </ol>  
                <h1>'''+title+'''</h1>
                '''+content+'''
            </div>
        </body>
    </html>''')

def handleBadRequest(path) -> None:
    '''create and send a 404 page'''
    sendResponse(404)
    sendHeader("Content-type", "text/html")
    sendTextualFileContent(create404Page(path))

def handleFileBasedRequest(path):
    '''serve an existing file'''
    prefix: str = str('.')
    sendResponse(200)
    sendHeader("Content-type", getContentType(path))
    if(not isBinaryFile(prefix+path)):
        tFile: TextIOWrapper = open(prefix+path,"r")
        tContent : str = tFile.read()
        sendTextualFileContent(tContent)
    else:
        bFile: BufferedReader = open(prefix+path,"rb")  
        bcontent : bytes = bFile.read()
        sendBinaryFileContent(bcontent)

def handleBlogPagesRequest(path, postFilePath):
    '''serve a blog post textual file after formatting'''
    postTitle: str = getTitle(postFilePath)
    postContent: str = getContent(postFilePath)  
    htmlContent: str = createBlogPage(postTitle,postContent)
    sendResponse(200)
    sendHeader("Content-type", getContentType(path))
    sendTextualFileContent(htmlContent)

def removeExtension(filePath:str) -> str:
    fileExtension: str = getFileExtension(filePath)
    i: int = int(0)
    res: str = str()
    while i < (len(filePath) - len(fileExtension) - 1):
        res += filePath[i]
        i += 1
    return res
    

def createIndexPage() -> str:
    allFilePath: list[str] = list()
    allTitles: list[str] = list()
    for postPath in (os.listdir("./posts/")):
        if (getFileExtension(postPath) == "txt"):
            allFilePath.append(removeExtension(postPath))
            allTitles.append(getTitle("./posts/"+postPath))
    allLinks: list[str] = list()
    i: int = int(0)
    while i < len(allFilePath):
        allLinks.append('<a href="'+allFilePath[i]+'">'+allTitles[i]+'</a>')
        i += 1
    allLinksAsHtmlList: str = str('<ul>\n')
    i = 0
    while i < len(allLinks):
        allLinksAsHtmlList += '<li>'+allLinks[i]+'</li>\n'
        i += 1
    allLinksAsHtmlList += '</ul>\n'
    return str('''
               <html>
                <head><title>The best blog ever</title></head>
                 <link href="./static/css/iiwBlogStyle.css" rel="stylesheet"/>
                </head>
                <body>
                   
                    <div class="main" id="main">
                    
                    <ol class="menu">
                        <li><a href="./static/html/addPost.html">add a post</a></li>
                    </ol>
                    
                    <h1> welcome on the IIW blog ! </h1>
                      <h2>here is the list of posts we have so far </h2>
                    <h3>'''+allLinksAsHtmlList+'''</h3>
                    </div>
                </body>
               </html>
               ''')
        

def handleGetRequest(path: str) -> None:
    '''This function defines how my server handle the get requests'''
    if(path == "/" or path=="/index.html"):
        sendResponse(200)
        sendHeader("Content-type", "text/html")
        sendTextualFileContent(createIndexPage())
        return
    
    if (getFileExtension(path)==""):
        postFilePath: str = getPostFilePath(path)
        if (not doesFileExist(postFilePath)):
            handleBadRequest(path)
            return
        handleBlogPagesRequest(path, postFilePath)
        return
   
    if not doesFileExist("."+path):
        handleBadRequest(path)
        return
        
    handleFileBasedRequest(path)


nbPost: int = int(0)
def handlePostRequest(incomingData: list[PostedData]) -> None:
    global nbPost
    title: str = str()
    content: str = str()
    picture: bytes = bytes()
    pictureName: str = str()
    for p in incomingData:
        if (p.name=="title"):
            title = p.value
        elif(p.name == "content"):
            content = p.value
        elif(p.name == "picture"):
            picture = p.value  # type: ignore
        elif(p.name == "pictureName"):
            pictureName = p.value
    nbPost += 1
    postName: str = str("/Post"+str(nbPost))
    postFilePath: str = getPostFilePath(postName)
    file: TextIOWrapper = open(postFilePath, "w")
    file.write(title+"\n")
    file.write(content)
    file.close()
    
    pFile: BufferedWriter = open("./posts/"+pictureName, "wb")
    print("picture type",type(picture))
    pFile.write(picture)
    pFile.close
    handleBlogPagesRequest(postName, postFilePath)

#test server
nbPost = len(os.listdir("./posts/"))
setHandleGetRequest(handleGetRequest)
setHandlePostRequest(handlePostRequest)
hostName = "localhost"
serverPort = 8080
launchServer(hostName,serverPort)

