import openai
import streamlit as st
import pandas as pd

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
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"What is the meaning of '{word}'? Provide synonyms in a comma-separated list after the meaning."},
            ],
        )

        content = response.choices[0].message.content

        if content:
            # Split the content into lines
            lines = content.split('\n')

            # Assume the first line is the meaning
            meaning = lines[0].strip() if lines else "Meaning not found."

            # Assume the second line (if present) contains synonyms
            synonyms = lines[1].strip() if len(lines) > 1 else "No synonyms found."
            # If "Synonyms:" is in the line, remove it
            if "Synonyms:" in synonyms:
                synonyms = synonyms.replace("Synonyms:", "").strip()

            synonyms_list = [syn.strip() for syn in synonyms.split(',')] if synonyms != "No synonyms found." else []
           
            df = pd.DataFrame({
                "Word": [word],
                "Meaning": [meaning],
                "Synonyms": [', '.join(synonyms_list)
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
