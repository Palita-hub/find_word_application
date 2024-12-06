import openai
import streamlit as st
import pandas as pd

# Streamlit app title
st.title("Word Meaning and Synonyms Finder")

# Sidebar for API key input
api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")
openai.api_key = api_key

# User input for the word
word = st.text_input("What word are you looking for?")

# Function to get word meaning and synonyms from OpenAI API
def get_word_details(word):
    if not api_key:
        st.error("Please enter your API key in the sidebar.")
        return None

    if not word:
        st.warning("Enter a word to search for its meaning.")
        return None

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use "gpt-3.5-turbo" if needed
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"What is the meaning of '{word}'? Provide synonyms too."},
            ],
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Display result if the user inputs a word
if st.button("Find Meaning and Synonyms"):
    if word:
        result = get_word_details(word)
        if result:
            # Parse result and display as a DataFrame
            st.markdown(f"### Details for *{word}*:")
            st.write(result)

            # Example parsed result (replace with real parsing logic):
            meaning = "A brief definition of the word."
            synonyms = ["synonym1", "synonym2", "synonym3"]

            df = pd.DataFrame({
                "Word": [word],
                "Meaning": [meaning],
                "Synonyms": [", ".join(synonyms)]
            })

            st.dataframe(df)

            # Add download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name=f"{word}_details.csv",
                mime="text/csv"
            )
    else:
        st.warning("Please enter a word!")