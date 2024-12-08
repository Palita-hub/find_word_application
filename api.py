import openai
import streamlit as st
import pandas as pd
import re
import random
import json

st.title("Word Meaning and Synonyms Finder")

api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")
openai.api_key = api_key

word = st.text_input("What word are you looking for?")

@st.cache_data  # Cache the function output
def get_word_details(word):
    if not api_key:
        st.error("Please enter your API key in the sidebar.")
        return None

    if not word:
        st.warning("Enter a word to search for its meaning.")
        return None

    try:
        example_json = {
            'meanings': [
                {'meaning': 'meaning1', 'synonyms': ['synonym1', 'synonym2']},
                {'meaning': 'meaning2', 'synonyms': ['synonym3', 'synonym4']}
            ]
        }
        example_json_str = json.dumps(example_json)

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Provide the meaning(s) of '{word}' and their corresponding synonyms in a JSON format like this: {example_json_str}"},
            ],
        )

        content = response.choices[0].message["content"]

        # Check if the content is valid JSON before parsing
        if content and content.strip():
            try:
                data = json.loads(content)
                meanings = data.get("meanings", [])

                rows = []
                for meaning_data in meanings:
                    meaning = meaning_data.get("meaning", "")
                    synonyms = meaning_data.get("synonyms", [])
                    rows.append({"Word": word, "Meaning": meaning, "Synonyms": ", ".join(synonyms)})

                df = pd.DataFrame(rows)
                return df
            except json.JSONDecodeError as e:
                st.error(f"Error decoding JSON response: {e} Content: {content}")
                return None
        else:
            st.error("OpenAI response is empty or invalid JSON.")
            return None

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None


def generate_question(word_details_df):
    if word_details_df is None or word_details_df.empty:
        return None, []

    selected_meaning_row = word_details_df.sample(1).iloc[0]
    correct_answer = selected_meaning_row['Meaning']
    synonyms = selected_meaning_row['Synonyms'].split(', ') if selected_meaning_row['Synonyms'] else []
    options = [correct_answer] + random.sample(synonyms, min(3, len(synonyms)))
    while len(options) < 4:
        options.append("Random Word")  # Replace with actual random word generation logic
    random.shuffle(options)
    question = f"What is the meaning of '{selected_meaning_row['Word']}'?"
    return question, options, correct_answer  # Include correct_answer in return


if st.button("Find Meaning and Synonyms"):
    if word:
        result_df = get_word_details(word)
        if result_df is not None:
            st.markdown(f"### Details for *{word}*:")
            st.dataframe(result_df)

            question, options, correct_answer = generate_question(result_df)  # Get correct_answer
            if question:
                st.write("**Question:**", question)
                user_answer = st.radio("Choose an option:", options)

                if user_answer == correct_answer:
                    st.success("Correct!")
                else:
                    st.error("Incorrect. The correct answer is:", correct_answer)
    else:
        st.warning("Please enter a word!")
