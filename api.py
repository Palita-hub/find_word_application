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
        response = openai.chat.completion.create(
            model="gpt-4", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"What is the meaning of '{word}'? Provide synonyms too."},
            ],
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Error: {e}")
        return None

if st.button("Find Meaning and Synonyms"):
    if word:
        result = get_word_details(word)
        if result:
            st.markdown(f"### Details for *{word}*:")
            st.write(result)
            meaning = "A brief definition of the word."
            synonyms = ["synonym1", "synonym2", "synonym3"]

            df = pd.DataFrame({
                "Word": [word],
                "Meaning": [meaning],
                "Synonyms": [", ".join(synonyms)]
            })

            st.dataframe(df)

            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name=f"{word}_details.csv",
                mime="text/csv"
            )
    else:
        st.warning("Please enter a word!")
