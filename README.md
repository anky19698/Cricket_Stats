# Cricket Stats Tracker

Cricket Stats Tracker is a Streamlit-based application that allows users to query cricket statistics, particularly from the IPL (Indian Premier League) and T20I (T20 Internationals). The app uses the Gemini Pro API for text generation and MongoDB for storing chat messages.

## Features

- **Query Cricket Stats:** Users can ask various cricket-related queries and get the statistics they need.
- **Generative AI:** Uses Gemini Pro API to generate SQL queries based on user input and analyze the results.
- **Database Integration:** Stores chat messages in a MongoDB collection and retrieves cricket data from a SQLite database.

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/your-username/cricket-stats-tracker.git
    cd cricket-stats-tracker
    ```

2. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up the Streamlit secrets. Create a file named `secrets.toml` in the `.streamlit` directory with the following content:

    ```toml
    [secrets]
    mongo_uri = "your_mongo_uri"
    key = "your_gemini_pro_api_key"
    ```

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
```
Open your browser and navigate to http://localhost:8501 to use the app.

## Code Explanation

### 1. Importing Required Libraries
The script starts by importing necessary libraries:
- `streamlit`: For building the web application.
- `pandas`: For handling data in DataFrames.
- `google.generativeai`: For using the Gemini Pro API for text generation.
- `json`, `sqlite3`: For handling JSON data and SQLite database operations.
- `pymongo`: For connecting to MongoDB.
- `certifi`: For SSL certificate verification.

### 2. Setting Up MongoDB Connection
We use `certifi` for SSL certification and `MongoClient` to connect to our MongoDB database using the URI stored in Streamlit secrets.

### 3. Database Functions
- **load_database_collection(mongo_uri):** Connects to MongoDB, creates or accesses the `cricket_chats` database and the `cricket_messages` collection.
- **store_message(collection, message):** Inserts a message into the MongoDB collection.
- **connect_to_database(database_name):** Connects to an SQLite database.
- **query_database(conn, query):** Executes a given SQL query on the SQLite database and returns the results.

### 4. Filter Database Based on User Input
- **filter_database(user_input):** Configures the Gemini Pro model and generates an appropriate SQL query based on the user input to filter cricket data from the database.

### 5. Analyze Query Result
- **analyze_result(df, user_input):** Converts the DataFrame to a dictionary and generates a summary using the Gemini Pro model based on the user input and DataFrame.

### 6. Streamlit App
The main function initializes the Streamlit app:
- **main():** Sets up the Streamlit app title, loads MongoDB collection, connects to the SQLite database, displays recommended queries, handles user inputs, generates SQL queries, fetches results, and displays them in a chat-like interface. It also stores the conversation in MongoDB.

### Instructions for Better Responses

1. Please use full names of players, teams, or venues.
2. Avoid using short names or nicknames.
3. Refer to the example queries for better understanding.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Streamlit for the web framework.
- Google Generative AI for the Gemini Pro API.
- MongoDB for the database solution.
- Pandas for data handling.


