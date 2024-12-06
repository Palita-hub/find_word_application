import openai
import streamlit as st
import pandas as pd
import re

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

        if content:
            rows = []

            meaning_blocks = re.split(r"\n\d+\.\s", content)[1:]  )

            for i, block in enumerate(meaning_blocks, 1):

                meaning_match = re.search(r"(.*?)(?=(Synonyms|Examples|Alternatively))", block, re.DOTALL | re.IGNORECASE)
                synonyms_match = re.search(r"(Synonyms|Synonyms and related words):\s*(.*)", block, re.DOTALL | re.IGNORECASE)

                meaning = meaning_match.group(1).strip() if meaning_match else "Meaning not found"
                synonyms = synonyms_match.group(2).strip() if synonyms_match else "Synonyms not found"

                rows.append({"Word": word, "Meaning": meaning, "Synonyms": synonyms})

            df = pd.DataFrame(rows)
            return df
        else:
            st.error("OpenAI response is empty.")
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
