# Client-Server News Application

### Project Description:
This project uses server-client model to create a tool that exchanges news information from [NewsAPI](https://newsapi.org/). It allows the client to request news based on country, category, language, etc, The user can request further details about a specific result, for which furthen information about chosen result will be displayed.  it offers a GUI throught which the user interacts with the program.

- **first Semester 2024-2025**
  - Group: **A12**
  - course: **ITNE352**
  - Section: **2**
  - Tawfiq alzaidani - **202210158**
  - ayoup alansary - **202100735**

 ### Requirements:
 you need to install the following libraries in your environment to get the code working correctly, use the following commands in your terminal to install them:
```
pip install tkinter
pip install requests
pip install newsapi-python
```

### How to run the code:
- Running the code:
  1. On your IDE, open theterminal and split it into two
  2. In one terminal, run the server file `python Server.py`
  3. In the other, run the client file `python Client.py`
- Interacting with the GUI:
  - Once the client code is running, it will establish a connection with the server, the user then will be asked to wnter his/her name to proceed
  - A menu will show up (Headlines, sources, Quit) from which the user will choose an option. "Quit" option will terminate the connection"
  - The user can choose an option and results of headlines/sources will be generated displaying brief details of each result, should the user need further details about a specific result, he can choose it and further details will be listed.

### The code:
the code consists of two main files: `client.py` and `server.py`.
### `client.py`:
**Graphical User Interface (GUI):**

  -The code utilizes the Tkinter library to create a GUI application for accessing news headlines and sources.
  
**Main Menu:**
  - Upon launching the application, users are prompted to enter their name.
  - Users are presented with a main menu offering the following options:
    + Search Headlines
    + List of Sources
    + Quit
   
      ```
        print("\n    ~~~Menu~~~")
            print("1- Search Headlines")
            print("2- List of Soarces")
            print("3- Quit")

            choice = input("\nChoose an option:\n")
      ```
  
**Search Headlines:**

  - Users can search for news headlines based on different criteria:
  - Search by keywords: Allows users to enter keywords to search for headlines.
  - Search by category: Users can select a news category (e.g., business, entertainment).
  - Search by country: Users can select a country to view headlines.
  - List all new headlines: Displays a list of all available headlines.
  - Back to main menu: Returns users to the main menu.

    ```
     print("\n~~~Search Headlines Menu~~~")
                    print("1- Search by keywords")
                    print("2- Search by category")
                    print("3- Search by country")
                    print("4- List all new headlines")
                    print("5- Back to main menu")
    ```

**Headline Details:**

After selecting a headline from the search results, users can view detailed information about the selected headline, including source name, author, title, URL, description, publishing date, and publishing time.

**List of Sources:**

  - Users can browse through a list of news sources based on different criteria:
  - Search by category: Allows users to select a news category to view sources.
  - Search by country: Users can select a country to view sources from that country.
  - Search by language: Users can select a language to view sources.
  - List all: Displays a list of all available news sources.
  - Back to main menu: Returns users to the main menu.
 
### `server.py`:

**Server Setup:**

  - The code sets up a server that listens for incoming connections on localhost (127.0.0.1) and port 49999.

**ServeClient Function:**

  - This function handles client connections and their requests. It runs in a separate thread for each.
  - It receives the client's name and menu choice (headlines or sources).
  - It then processes the client's subsequent choices and performs actions accordingly.

**Headlines Functions:**

  - Functions to retrieve news headlines based on different criteria:
    - NEWHeadlines: Retrieves top headlines from the US.
    - Headline_KeyWord: Retrieves headlines based on a keyword provided by the client.
    - Headline_category: Retrieves headlines based on a specific category.
    - Headline_country: Retrieves headlines based on a specific country.

**Source Functions:**

  - Functions to retrieve news sources based on different criteria:
    - NEWSources: Retrieves a list of news sources.
    - SourceCategory: Retrieves sources based on a specific category.
    - SourceCountry: Retrieves sources based on a specific country.
    - Sourcelanguage: Retrieves sources based on a specific language.
   
### Acknowledgements:
We would want to express my sincere appreciation to our doctor for all of his guidance and motivation during this course. Their advice and guidance have been invaluable. Their commitment to supporting academic achievement and development is incredibly admirable.
### conclusion:
This project offers a server-client architecture that utilizes tkinter library to interact with a GUI to request headlines and sources from NewsAPI. It handles multiple connections by dedicating a thread for each client. The client can choose options such as searching headlines by keywords, category, or country, listing all headlines, or accessing details about news sources. The server rocesses these requests and detches relevant results from NewsAPI and sends it to the client

### Resources:

- [Python GUI programming](https://wiki.python.org/moin/GuiProgramming)
- [JSON encoder and decoder](https://docs.python.org/3/library/json.html)
