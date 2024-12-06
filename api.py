import openai
import streamlit as st
import pandas as pd
import json

st.title("Word Meaning and Synonyms Finder")

api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")
openai.api_key = api_key

word = st.text_input("What word are you looking for?")

def get_word_details(word):
    if not api_key:
        st.error("Please enter your API key in the sidebar.")
        return None

    if not word:
        st.warning("Enter a word to search for its meaning.")
        return None

    try:
        st.write(f"Searching for meaning of: {word}")

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"What is the meaning of '{word}'? Provide synonyms too."},
            ]
        )

        content = response.choices[0].message.content

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
            st.error(f"Error decoding JSON response: {e}")
            return None

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
