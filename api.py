import openai
import streamlit as st
import pandas as pd
import requests
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

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"What is the meaning of '{word}'? Provide synonyms too."},
            ]
        )

        st.write("API response:", response)

        content = response.choices[0].message["content"]

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

        return meaning, synonyms

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        raise

def get_synonyms_from_api(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            synonyms = []
            for meaning in data[0]["meanings"]:
                for definition in meaning["definitions"]:
                    if "synonyms" in definition:
                        synonyms.extend(definition["synonyms"])
            return ", ".join(synonyms) if synonyms else "No synonyms found."
        else:
            return "Error fetching synonyms from external API."
    except Exception as e:
        return f"Error: {e}"

if st.button("Find Meaning and Synonyms"):
    if word:
        result = get_word_details(word)
        if result:
            meaning, synonyms = result
            st.markdown(f"### Details for *{word}*:")
            st.write(f"**Meaning:** {meaning}")
            st.write(f"**Synonyms:** {synonyms}")

            external_synonyms = get_synonyms_from_api(word)
            st.write(f"**External Synonyms (API):** {external_synonyms}")

            df = pd.DataFrame({
                "Word": [word],
                "Meaning": [meaning],
                "Synonyms": [synonyms]
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
