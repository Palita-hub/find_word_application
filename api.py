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
                {"role": "user", "content": f"Provide the meaning(s) of '{word}' and their corresponding synonyms in a JSON format like this: "
                                           f"{{'meanings': [{'meaning': 'meaning1', 'synonyms': ['synonym1', 'synonym2']}, "
                                           f"{{'meaning': 'meaning2', 'synonyms': ['synonym3', 'synonym4']}]}}"},
            ],
        )

        content = response.choices[0].message.content

        if content:
            meaning_start = content.find("means:")
            synonyms_start = content.find("Synonyms:")


            if meaning_start != -1:
                meaning = content[meaning_start + len("means:"):synonyms_start].strip() if synonyms_start != -1 else content[meaning_start + len("means:"):].strip()
            else:
                meaning = "Meaning not found."

            if synonyms_start != -1:
                synonyms = content[synonyms_start + len("Synonyms:"):].strip()
                synonyms = synonyms.replace("\n", ", ").replace("  ", " ") 
            else:
                synonyms = "No synonyms found."

            
            df = pd.DataFrame({
                "Word": [word], 
                "Meaning": [meaning],
                "Synonyms": [synonyms]
            })

            return df  

        return None 

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

if st.button("Find Meaning and Synonyms"):
    if word:
        result_df = get_word_details(word)
        if result_df is not None:
            st.markdown(f"### Details for *{word}*:")
            st.dataframe(result_df) 
    else:
        st.warning("Please enter a word!")
