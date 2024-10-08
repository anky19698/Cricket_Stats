import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import sqlite3
from pymongo.mongo_client import MongoClient
import certifi
import os
from langchain_huggingface import HuggingFaceEndpoint
import re
from langchain_groq import ChatGroq
#
# Database for Storing Chats
ca = certifi.where()

mongo_uri = st.secrets['mongo_uri']
key = st.secrets['key']
hf_api_token = st.secrets['hf_token']
groq_key = st.secrets['groq_key']


################
# Hugging Face #
################

def get_hf_model():
    # Set up Hugging Face Token
    hf_token = hf_api_token
    os.environ['HUGGINGFACEHUB_API_TOKEN'] = hf_token

    model_id = "mistralai/Mistral-7B-Instruct-v0.3"
    # model_id = "microsoft/tapex-large-sql-execution"
    model = HuggingFaceEndpoint(
        endpoint_url=model_id,
        task="text-generation",
        temperature= 1,
        max_new_tokens= 1000,
        token=hf_token
    )
    return model

def get_llama_model():
    g_key = groq_key
    os.environ['GROQ_API_KEY'] = g_key

    model_name = 'llama-3.1-8b-instant'

    model = ChatGroq(
        model=model_name
    )

    return model

def get_sql_query(user_input):
    table_info = """

    TABLE: batter_vs_venue

        striker, played_for, stadium, innings, runs_scored, balls_faced, dots, fours, sixes, fifties, hundreds, batting_AVG, batting_SR, dot_percentage, format
        A Ashish Reddy, India, Arun Jaitley Stadium, 1, 16, 9, 1, 1, 2, 0, 0, 16.0, 177.77777777777777, 11.11111111111111, T20I

    TABLE: batter_vs_team
    
        striker, played_for, bowling_team, innings, runs_scored, balls_faced, dots, fours, sixes, fifties, hundreds, batting_AVG, batting_SR, dot_percentage, format
        A Ashish Reddy, India, Chennai Super Kings, 3, 45, 25, 2, 3, 3, 0, 0, 22.5, 180.0, 32.0, T20I
    
    TABLE: batter_vs_bowler
    
        striker, bowler, innings, runs_scored, wickets_taken, batting_SR, dot_percentage, format
        A Ashish Reddy, A Nehra, 2, 7, 1, 77.77777777777777, 55.55555555555556, T20I
    
    TABLE: bowling_record
    
        bowler, played_for, innings, runs_conceded, balls_bowled, wickets_taken, dots, fours, sixes, Economy, bowling_AVG, format
        A Ashish Reddy, India, 20, 400, 270, 18, 89, 26, 20, 8.88888888888889, 22.22222222222222, T20I
    
    TABLE: batting_record
    
        striker, played_for, innings, runs_scored, balls_faced, dots, fours, fifties, hundreds, sixes, batting_SR, dot_percentage, batting_AVG, format
        A Ashish Reddy, India, 23, 280, 196, 13, 61, 16, 1, 15, 142.85714285714286, 31.122448979591837, 21.53846153846154, T20I
    
    TABLE: bowling_record_by_year
    
        bowler, played_for, year, innings, runs_conceded, balls_bowled, wickets_taken, dots, fours, sixes, Economy, bowling_AVG, format
        A Ashish Reddy, India, 2022, 20, 400, 270, 18, 89, 26, 20, 8.88888888888889, 22.22222222222222, T20I
    
    TABLE: batting_record_by_year
    
        striker, played_for, year, innings, runs_scored, balls_faced, dots, fours, fifties, hundreds, sixes, batting_SR, dot_percentage, batting_AVG, format
        A Ashish Reddy, India, 2022, 23, 280, 196, 13, 61, 16, 1, 15, 142.85714285714286, 31.122448979591837, 21.53846153846154, T20I
    
    TABLE: batting_record_by_innings
    
        striker, played_for, bowling_team, start_date, runs_scored, balls_faced, player_dismissed, dots, fours, sixes, batting_SR, dot_percentage, format
        V Kohli, India, Punjab Kings, 2024-05-04, 21, 21, Yes, 2, 5, 6, 100, 20, T20I
    
    TABLE: bowling_record_by_innings
    
        bowler, played_for, batting_team, start_date, runs_conceded, balls_bowled, wickets_taken, dots, Economy, format
        A Ashish Reddy, India, Punjab Kings, 2024-05-04, 21, 21, 2, 5, 6, T20I
    
    TABLE: bowler_vs_team
    
        bowler, played_for, batting_team, runs_conceded, balls_bowled, wickets_taken, dots, Economy, format
        A Ashish Reddy, India, Punjab Kings, 21, 21, 2, 5, 6, T20I

    TABLE: bowler_vs_venue
    
        bowler, played_for, stadium, runs_conceded, balls_bowled, wickets_taken, dots, Economy, format
        A Ashish Reddy, India, Wankhede Stadium, 21, 21, 2, 5, 6, T20I

    """

    examples = [
        {
            "Question": "virat Kohli vs jasprit bumrah Record",
            "SQLQuery": "Select All From batter_vs_bowler where striker LIKE 'V% Kohli' AND bowler LIKE 'J% Bumrah'"
        },
        {
            "Question": "virat kohli runs in ipl 2024",
            "SQLQuery": "Select * from batting_record_by_year where striker LIKE 'V% Kohli' AND year=2024 AND format = 'IPL'"
        },
        {
            "Question": "jasprit bumrah wickets in ipl",
            "SQLQuery": "Select bowler, played_for, innings, wickets_taken, dots, Economy From bowling_record where bowler LIKE 'J% Bumrah' AND format = 'IPL'"
        },
        {
            "Question": "rohit Sharma scores in last 7 innings in t20i",
            "SQLQuery": "Select * From batting_record_by_innings where striker LIKE 'R% Sharma' LIMIT 7 AND format = 'T20I'"
        },
        {
            "Question": "Jasprit Bumrah bowling economy in recent innings",
            "SQLQuery": "Select * From bowling_record_by_innings where bowler LIKE 'J% Bumrah' LIMIT 5"
        },
        {
            "Question": "most sixes hit by player",
            "SQLQuery": "Select * From batting_record order by sixes DESC LIMIT 10"
        },
        {
            "Question": "Virat Kohli Record on 18 May in all Years",
            "SQLQuery": "Select * from batting_record_by_innings where striker LIKE 'V% Kohli' AND EXTRACT(MONTH FROM start_date) = 5 AND EXTRACT(DAY FROM start_date) = 18"
        },
        {
            "Question": "virat Kohli vs pakistan",
            "SQLQuery": "Select * From batter_vs_team where striker LIKE 'V% Kohli' AND bowling_team LIKE 'Pakistan'"
        },
        {
            "Question": "Rohit Sharma Runs for Mumbai Indians",
            "SQLQuery": "Select * From batting_record where striker LIKE 'RG% Sharma' AND played_for LIKE 'Mumbai Indians'"
        },
        {
            "Question": "Most Wickets for rajasthan royals",
            "SQLQuery": "Select bowler, played_for, wickets, innings, Economy From bowling_record where played_for LIKE 'Rajasthan Royals' Order By wickets_taken DESC"
        },
        {
            "Question": "Rohit Sharma Batting Record",
            "SQLQuery": "Select * From batting_record where striker LIKE 'RG% Sharma'"
        },
        {
            "Question": "Most Wickets By Indian Player Against Pakistan in T20I",
            "SQLQuery": "Select * From bowler_vs_team where played_for LIKE 'India' AND batting_team LIKE 'Pakistan' AND format = 'T20I' order by wickets_taken DESC"
        }
    ]

    example_output_format = """
    {
        "sql_query': "Select * From bowler_vs_team where played_for LIKE 'India' AND batting_team LIKE 'Pakistan' AND format = 'T20I' order by wickets_taken DESC"
    }
    """    

    input_prompt = f"""
    You are a Smart AI Cricket Analyst, working on IPL (Indian Premier League) and T20I (T20 Internationals) data.

    Your task is to generate a SQL query based on the user input to filter cricket data from the database. Extract player names, stadium names, and team names from the user input and filter accordingly.

    Remember:
    - Each row in the database represents a ball event.
    - Use only the specified columns to construct the SQL query.
    - If the format (like IPL or T20I) is mentioned, apply a filter by format in the SQL query.
    - If the format is not mentioned, ignore the format filter.

    Database Table Information: {table_info}

    For player names, use the following format (last name is always complete):
    - [Initial letter of first name + any letters in between + last name]
    - Example: For a player named Sunil Narine, use "S% Narine"

    Here are some few-shot examples:
    {examples}

    Generate the SQL query based on the following user input:
    [user input] = {user_input}

    Output only 1 SQL Query the following Format: {example_output_format}
    Dont Generate Any other Characters!
    """

    hf_model = get_llama_model()

    try:
        prompt = input_prompt
        response = hf_model.invoke(prompt)
        # print("User Input:", user_input)
        # print("Response:", response)
        # cleaned_response = re.sub(r'^-+$', '', response, flags=re.MULTILINE).strip()
        # # print("Cleaned Response:", cleaned_response)
        # json_part = re.search(r'\{.*\}', response, re.DOTALL).group()
        # json_response = json.loads(cleaned_response)
        # # print("JSON Response:", json_response)
        # generated = json_response['sql_query']
        # return generated
        return response.content
    except:
        return None

################
# Hugging Face #
################

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

        striker, played_for, stadium, innings, runs_scored, balls_faced, dots, fours, sixes, fifties, hundreds, batting_AVG, batting_SR, dot_percentage, format
        A Ashish Reddy, India, Arun Jaitley Stadium, 1, 16, 9, 1, 1, 2, 0, 0, 16.0, 177.77777777777777, 11.11111111111111, T20I

    TABLE: batter_vs_team
    
        striker, played_for, bowling_team, innings, runs_scored, balls_faced, dots, fours, sixes, fifties, hundreds, batting_AVG, batting_SR, dot_percentage, format
        A Ashish Reddy, India, Chennai Super Kings, 3, 45, 25, 2, 3, 3, 0, 0, 22.5, 180.0, 32.0, T20I
    
    TABLE: batter_vs_bowler
    
        striker, bowler, innings, runs_scored, wickets_taken, batting_SR, dot_percentage, format
        A Ashish Reddy, A Nehra, 2, 7, 1, 77.77777777777777, 55.55555555555556, T20I
    
    TABLE: bowling_record
    
        bowler, played_for, innings, runs_conceded, balls_bowled, wickets_taken, dots, fours, sixes, Economy, bowling_AVG, format
        A Ashish Reddy, India, 20, 400, 270, 18, 89, 26, 20, 8.88888888888889, 22.22222222222222, T20I
    
    TABLE: batting_record
    
        striker, played_for, innings, runs_scored, balls_faced, dots, fours, fifties, hundreds, sixes, batting_SR, dot_percentage, batting_AVG, format
        A Ashish Reddy, India, 23, 280, 196, 13, 61, 16, 1, 15, 142.85714285714286, 31.122448979591837, 21.53846153846154, T20I
    
    TABLE: bowling_record_by_year
    
        bowler, played_for, year, innings, runs_conceded, balls_bowled, wickets_taken, dots, fours, sixes, Economy, bowling_AVG, format
        A Ashish Reddy, India, 2022, 20, 400, 270, 18, 89, 26, 20, 8.88888888888889, 22.22222222222222, T20I
    
    TABLE: batting_record_by_year
    
        striker, played_for, year, innings, runs_scored, balls_faced, dots, fours, fifties, hundreds, sixes, batting_SR, dot_percentage, batting_AVG, format
        A Ashish Reddy, India, 2022, 23, 280, 196, 13, 61, 16, 1, 15, 142.85714285714286, 31.122448979591837, 21.53846153846154, T20I
    
    TABLE: batting_record_by_innings
    
        striker, played_for, bowling_team, start_date, runs_scored, balls_faced, player_dismissed, dots, fours, sixes, batting_SR, dot_percentage, format
        V Kohli, India, Punjab Kings, 2024-05-04, 21, 21, Yes, 2, 5, 6, 100, 20, T20I
    
    TABLE: bowling_record_by_innings
    
        bowler, played_for, batting_team, start_date, runs_conceded, balls_bowled, wickets_taken, dots, Economy, format
        A Ashish Reddy, India, Punjab Kings, 2024-05-04, 21, 21, 2, 5, 6, T20I
    
    TABLE: bowler_vs_team
    
        bowler, played_for, batting_team, runs_conceded, balls_bowled, wickets_taken, dots, Economy, format
        A Ashish Reddy, India, Punjab Kings, 21, 21, 2, 5, 6, T20I

    TABLE: bowler_vs_venue
    
        bowler, played_for, stadium, runs_conceded, balls_bowled, wickets_taken, dots, Economy, format
        A Ashish Reddy, India, Wankhede Stadium, 21, 21, 2, 5, 6, T20I

    """

    # user_input = "kl rahul vs jasprit bumrah Record"

    input_prompt = f"""
    You are a Smart AI Cricket Analyst, Working on IPL(Indian Premier League) and T20I(T20 Internationals) Data

    You're tasked with generating a SQL query based on the user input to filter cricket data from the database. Your goal is to extract Player Names, Stadium Names, and Team Names from the user input and filter accordingly.

    Remember, each row in the database represents a Ball Event, and you should only use the specified columns to construct the SQL query.

    Check if Format is mentioned in query, Like IPL or T20I. If Mentioned, then Apply Filter by format in SQL query also.
    If not mentioned, then ignore format filter.

    Here's the Database Table Information: {table_info}

    For Player Names, use the following format (LastName is always complete):
    [initial Letter of firstName + any letters in between + LastName]
    Example: For a player named Sunil Narine, use "S% Narine"



    1) virat Kohli vs jasprit bumrah Record

    Expected SQL Output:
    select * from batter_vs_bowler where lower(striker) like "v% kohli" and lower(bowler) like "j% bumrah"
    
    2) virat kohli runs in ipl 2024
    
    Expected SQL Output:
    select * from batting_record_by_year where lower(striker) like "v% kohli" and year=2024 and lower(format) = 'ipl'
    
    3) jasprit bumrah wickets in ipl
    
    Expected SQL Output:
    select bowler, played_for, innings, wickets_taken, dots, economy from bowling_record where lower(bowler) like "j% bumrah" and lower(format) = 'ipl'
    
    4) rohit Sharma scores in last 7 innings in t20i
    
    Expected SQL Output:
    select * from batting_record_by_innings where lower(striker) like "r% sharma" limit 7 and lower(format) = 't20i'
    
    5) jasprit bumrah bowling economy in recent innings
    
    Expected SQL Output:
    select * from bowling_record_by_innings where lower(bowler) like "j% bumrah" limit 5
    
    6) virat Kohli Record on 18 May in all Years
    
    Expected SQL Output:
    select * from batting_record_by_innings where lower(striker) like "v% kohli" and extract(month from start_date) = 5 and extract(day from start_date) = 18
    
    7) virat Kohli vs pakistan
    
    Expected SQL Output:
    select * from batter_vs_team where lower(striker) like "v% kohli" and lower(bowling_team) like "pakistan"
    
    8) rohit Sharma Runs for Mumbai Indians
    
    Expected SQL Output:
    select * from batting_record where lower(striker) like "rg% sharma" and lower(played_for) like "mumbai indians"
    
    9) most Wickets for rajasthan royals
    
    Expected SQL Output:
    select bowler, played_for, wickets, innings, economy from bowling_record where lower(played_for) like "rajasthan royals" order by wickets_taken desc
    
    10) rohit Sharma Batting Record
    
    Expected SQL Output:
    select * from batting_record where lower(striker) like "rg% sharma"
    
    11) most Wickets By Indian Player Against Pakistan in T20I
    
    Expected SQL Output:
    select * from bowler_vs_team where lower(played_for) like "india" and lower(batting_team) like "pakistan" and lower(format) = "t20i" order by wickets_taken
     
    
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
    # genai.configure(api_key=key)
    # model = genai.GenerativeModel('gemini-pro')
    model = get_llama_model()
    # prompt = f"""
    # You are a AI Cricket Stats Assistant Like ChatGPT but for Cricket.
    # Based on Previous User Input: {user_input}, You have Successfully got a resulting Dataframe: {df}
    # Analyze this Dataframe df about cricket(IPL) records, Give a brief summary highlighting important stats like runs_scored, wickets_taken, etc from df.
    # and dont include false numbers, summarize in 3-4 lines
    # You are a Smart AI Assistant Like ChatGPT, so dont reveal whats happening in the backend!
    # Explain in Cricket Terms dont include Technical Terms!
    # """
    # Convert DataFrame to dictionary
    df_dict = df.to_dict(orient='records')

    prompt = f"""
    You are a AI Cricket Content Writer. 
    Based on Previous User Input: {user_input}, You have Successfully got a resulting Data in Form of Python Dictionary: {df_dict}
    Analyze this Data about cricket Player records and Briefly Summerize.
    Don't Reveal any Backend Information, Assume You have Learned from Data, And Just Add 3-7 Bullet Points to Summarize the Data
    Don't Write Your Own Lines, Use Data to Write the Summary
    Explain in Cricket Terms dont include Technical Terms!
    If Dataframe is Empty, Ask Them to Try Again!
    """

    # prompt = f"""
    # You are a Cricket Data Analyst, Summarize the Dataframe: {df} of {user_input},
    # Generate Response in Following Format:
    # Mention the user_input on top
    # then on each row give, [column_name: value] each on new line:
    # till all the column values written
    # """

    # response = model.generate_content(prompt)
    response = model.invoke(prompt)

    return response.content


def main():
    st.title("Cricket Stats Tracker")

    
    # Define recommended queries
    recommended_queries = [
        "Virat Kohli runs in IPL 2024",
        "Virat Kohli vs Jasprit Bumrah",
        "Yuzvendra Chahal bowling record in IPL",
        "Rohit Sharma record vs Sunrisers Hyderabad",
        "Virat Kohli record at Wankhede Stadium",
        "Most sixes hit in IPL 2024"
    ]

    
    
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
    6) most sixes hit in ipl 2024

    Some Instructions for Better Response:
    1) Please try using Full Names of Players/Teams/Venue
    2) Avoid using short names or nick names
    3) Take above queries as a reference
    """

    if instructions_button:
        # Display the text if the button is clicked
        st.text_area("Instructions", value=instructions, height=300, disabled=True)

    # Load Database of Chats
    collection = load_database_collection(mongo_uri)

    # Connect to Cricket Data
    conn = connect_to_database('cricket_database.db')


    # Display recommended queries as buttons
    st.sidebar.title("Recommended Queries")
    for query in recommended_queries:
        if st.sidebar.button(query):
            # Set the selected query as user input
            st.session_state.user_input = query
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


    # if "user_input" in st.session_state:
    #     user_input = st.session_state.user_input
    #     # Clear the session state variable to avoid reusing the same input again
    #     st.session_state.user_input = None
    # else:
    #     # If user_input is not set through the session state, use the chat input
    #     user_input = st.chat_input("What is up?")

    # Retrieve user input from session state if available, otherwise display chat input box
    

    # CSS for chatbox

    user_input = st.chat_input("What is up?")
    
    if "user_input" in st.session_state:
        if st.session_state.user_input is not None:
            user_input = st.session_state.user_input
            # Clear the session state variable to avoid reusing the same input again
            st.session_state.user_input = None

    
    # user_input = st.session_state.user_input if "user_input" in st.session_state else st.chat_input("What is up?")
    # Retrieve user input from session state if available, otherwise display chat input box
    # user_input = st.session_state.user_input if "user_input" in st.session_state else ""
    
    # Display chat input box
    if user_input:
    
    # if user_input := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        # Display user message in chat message container

        try:
            with st.chat_message("user"):
                st.markdown(user_input)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):

                # sql_query = filter_database(user_input)
                sql_query = get_sql_query(user_input) # Hugging Face
                # Query the database
                if sql_query:
                    column_names, result = query_database(conn, sql_query)

                    # Create DataFrame
                    df = pd.DataFrame(result, columns=column_names)

                    # Display result in a table
                    # st.write(df)

                    content = analyze_result(df, user_input)
                    st.write(content)
                    # Store user message and assistant response
                    store_message(collection,
                                  {"User": user_input,
                                   "AI": content})
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
