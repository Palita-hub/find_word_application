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
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Provide the meaning(s) of '{word}' and their corresponding synonyms. "
                                           f"Separate meanings with 'Meaning:' and synonyms with 'Synonyms:'. "
                                           f"If there are multiple meanings, number them (e.g., Meaning 1:, Meaning 2:)."},
            ],
        )

        content = response.choices[0].message.content

        if content:
            rows = []
            meaning_blocks = content.split("Meaning")

            for i, block in enumerate(meaning_blocks[1:]):
                meaning_index = block.find(":")
                meaning = block[meaning_index + 1:block.find("Synonyms:")].strip()
                synonyms1 = block[block.find("Synonyms:") + len("Synonyms:"):].strip()
                synonyms2 = synonyms1.replace(',','\n')
                synonyms =synonyms2.split('\n')
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
       
