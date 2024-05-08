import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import sqlite3
from pymongo.mongo_client import MongoClient
import certifi

# Database for Storing Chats
ca = certifi.where()

mongo_uri = st.secrets['mongo_uri']
key = st.secrets['key']

def load_database_collection(mongo_uri):
    # Connect to MongoDB
    ca = certifi.where()

    # Create a new client and connect to the server
    client = MongoClient(mongo_uri, tlsCAFile=ca)

    # Create Database
    mydb = client['cricket_chats']

    # Create Collection
    collection = mydb.cricket_messages

    return collection

def store_message(collection, message):
    # Insert message into MongoDB collection
    collection.insert_one(message)



def connect_to_database(database_name):
    conn = sqlite3.connect(database_name)
    return conn

def query_database(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    column_names = [description[0] for description in cursor.description]
    data = cursor.fetchall()
    return column_names, data



def filter_database(user_input):

    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-pro')

    # user_input = input(" Please Ask: ")

    table_info = """

    TABLE: batter_vs_venue
    
    striker,stadium,innings,runs_scored,balls_faced,dismissals,dots,fours,sixes,fifties,hundreds,batting_AVG,batting_SR,dot_percentage
    A Ashish Reddy,Arun Jaitley Stadium,1,16,9,1,1,2,0,0,0,16.0,177.77777777777777,11.11111111111111
    
    TABLE: batter_vs_team
    
    striker,bowling_team,innings,runs_scored,balls_faced,dismissals,dots,fours,sixes,fifties,hundreds,batting_AVG,batting_SR,dot_percentage
    A Ashish Reddy,Chennai Super Kings,3,45,25,2,8,3,3,0,0,22.5,180.0,32.0
    
    TABLE: batter_vs_bowler
    
    striker,bowler,innings,runs_scored,balls_faced,dismissals,dots,fours,sixes,batting_SR,dot_percentage,inning_vs_dismissal
    A Ashish Reddy,A Nehra,2,7,9,1,5,1,0,77.77777777777777,55.55555555555556,1
    
    TABLE: bowling_record
    
    bowler,innings,runs_conceded,balls_bowled,dismissals,dots,fours,sixes,Economy,bowling_AVG
    A Ashish Reddy,20,400,270,18,89,26,20,8.88888888888889,22.22222222222222
    
    TABLE: batting_record
    
    striker,innings,runs_scored,balls_faced,dismissals,dots,fours,fifties,hundreds,sixes,batting_SR,dot_percentage,batting_AVG
    A Ashish Reddy,23,280,196,13,61,16,2,1,15,142.85714285714286,31.122448979591837,21.53846153846154
    
    TABLE: bowling_record_by_year

    bowler, year, innings,runs_conceded,balls_bowled,dismissals,dots,fours,sixes,Economy,bowling_AVG
    A Ashish Reddy, 2022, 20,400,270,18,89,26,20,8.88888888888889,22.22222222222222
    
    TABLE: batting_record_by_year
    
    striker, year, innings,runs_scored,balls_faced,dismissals,dots,fours, fifties, hundreds, sixes,batting_SR,dot_percentage,batting_AVG
    A Ashish Reddy, 2022, 23,280,196,13,61,16,2,1,15,142.85714285714286,31.122448979591837,21.53846153846154
    
    """


    # user_input = "kl rahul vs jasprit bumrah Record"

    input_prompt = f"""
    You are a Smart AI Cricket Analyst, Working on IPL(Indian Premier League) Data
    
    You're tasked with generating a SQL query based on the user input to filter cricket data from the database. Your goal is to extract Player Names, Stadium Names, and Team Names from the user input and filter accordingly.
    
    Remember, each row in the database represents a Ball Event, and you should only use the specified columns to construct the SQL query.
    
    Here's the Database Table Information: {table_info}
    
    For Player Names, use the following format (LastName is always complete):
    [initial Letter of firstName + any letters in between + LastName]
    Example: For a player named Sunil Narine, use "S% Narine"
    
    Example user input:
    1) virat Kohli vs jasprit bumrah Record
    
    Expected SQL Output:
    Select * From batter_vs_bowler where striker LIKE "V% Kohli" AND bowler LIKE "J% Bumrah"

    2) virat kohli runs in ipl 2024
    
    Expected SQL Output:
    Select * From batting_record_by_year where striker LIKE "V% Kohli" AND year=2024

    3) jasprit bumrah wickets in ipl
    
    Expected SQL Output:
    Select * From bowling_record where bowler LIKE "J% Bumrah"
    
    4) most sixes hit by player: In this case, you should apply sort in SQL query, and retrieve only top 10 rows 
    
    Remember, only use filters or sorts in the SQL query, and do not use any type of JOIN operations.
    
    Ensure that the SQL query is written only for the relevant table and includes columns and table names only from the Table Information.
    
    [user input] = {user_input}
    """


    response = model.generate_content(input_prompt)

    # data = pd.read_csv('all_ipl_data.csv')
    #
    # print(data.columns)

    print(response.text)

    sql_query = response.text.replace('```', '')
    sql_query = sql_query.replace('sql', '', 1)

    return sql_query


def analyze_result(df, user_input):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    Act as a Smart AI Cricket Analyst Chat Assistant Like ChatGPT, 
    Based on Previous {user_input}, You have Successfully got a resulting Dataframe: {df}
    Analyze this Dataframe about cricket records, Give a brief summary highlighting only important stats, in 3-4 lines
    """
    response = model.generate_content(prompt)

    return response

def main():
    st.title("Cricket Stats Assistant")

    # Instructions for Chat App
    instructions_button = st.button("How to Use")

    instructions = """
    This is Cricket(IPL) Stats Assistant, which answers your cricket stats queries.
    It has Latest Data up to 2 previous days.
    
    You Can Ask Queries like: 
    1) Virat Kohli runs in ipl 2024
    2) virat kohli vs jasprit bumrah
    3) yuzi chahal bowling record in ipl
    4) rohit sharma record vs sunrisers hyderabad
    5) virat kohli record at wankhede stadium

    Some Instructions for Better Response:
    1) Please try using Full Names of Players/Teams/Venue
    2) Avoid using short names or nick names
    3) Take above queries as a reference
    """
    
    if instructions_button:
        # Display the text if the button is clicked
        st.text_area("Hidden Text", value=instructions, disabled=True)
    
    # Load Database of Chats
    collection = load_database_collection(mongo_uri)

    # Connect to Cricket Data
    conn = connect_to_database('cricket_database.db')

    # # User input
    # user_input = st.text_input("Ask something about cricket:")


    # # If user submits a query
    # if st.button("Ask"):
    #     # Generate SQL query based on user input (you need to implement this)
    #     sql_query = filter_database(user_input)  # Implement this function
    #
    #     # Query the database
    #     if sql_query:
    #         column_names, result = query_database(conn, sql_query)
    #
    #         # Create DataFrame
    #         df = pd.DataFrame(result, columns=column_names)
    #
    #         # Display result in a table
    #         st.write(df)
    #     else:
    #         st.write("Sorry, I couldn't understand your query.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

        # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

        # Accept user input
    if user_input := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        # Display user message in chat message container

        try:
            with st.chat_message("user"):
                st.markdown(user_input)
    
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
    
                    sql_query = filter_database(user_input)
                    # Query the database
                    if sql_query:
                        column_names, result = query_database(conn, sql_query)
    
                        # Create DataFrame
                        df = pd.DataFrame(result, columns=column_names)
    
                        # Display result in a table
                        # st.write(df)
    
                        content = analyze_result(df, user_input)
                        st.write(content.text)
                        # Store user message and assistant response
                        store_message(collection,
                                      {"User": user_input,
                                       "AI": content.text})
                        st.write(df)
    
                    else:
                        st.write("Sorry, I couldn't understand your query.")
    
    
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": content.text})
    
        except:
            st.write("This Question Was a Googly, Please Try Some Another Delivery")

    # Close the connection
    conn.close()


if __name__ == "__main__":
    main()