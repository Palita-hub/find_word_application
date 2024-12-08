import openai
import streamlit as st
import pandas as pd
import json

st.title("Word Meaning and Synonyms Finder")
api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")
if api_key:
    openai.api_key = api_key
word = st.text_input("What word are you looking for?")

def get_word_details(word):
    if not api_key:
        st.error("Please enter your API key in the sidebar.")
        return None
    if not word.strip():
        st.warning("Enter a word to search for its meaning.")
        return None

    prompt = (
        f"Provide detailed meanings for the word '{word}'. Respond in a strict JSON format as follows:\n"
        f"{{'meanings': ["
        f"{{'meaning': '...', 'synonyms': ['...'], 'part_of_speech': '...', 'example': '...'}},"
        f"{{'meaning': '...', 'synonyms': ['...'], 'part_of_speech': '...', 'example': '...'}}]}}"
    )

    for attempt in range(3):
        try:
            with st.spinner(f"Searching for meanings of: {word} (Attempt {attempt + 1}/3)..."):
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.5
                )

                content = response.choices[0].message.content.strip()
                try:
                    data = json.loads(content)
                    meanings = data.get("meanings", [])
                    if not meanings:
                        st.warning("No meanings found in the API response. Please try another word.")
                        return None
                    rows = []
                    for meaning_data in meanings:
                        meaning = meaning_data.get("meaning", "N/A")
                        synonyms = meaning_data.get("synonyms", [])
                        part_of_speech = meaning_data.get("part_of_speech", "N/A")
                        example = meaning_data.get("example", "N/A")
                        rows.append({
                            "Word": word,
                            "Part of Speech": part_of_speech,
                            "Meaning": meaning,
                            "Synonyms": ", ".join(synonyms) if synonyms else "N/A",
                            "Example": example
                        })
                    df = pd.DataFrame(rows)
                    return df
                except json.JSONDecodeError as e:
                    st.error(f"Error decoding JSON response: {e}. Content: {content}")
                    continue
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            continue

    st.error("Failed to fetch a valid response after 3 attempts. Please try again later.")
    return None

if st.button("Find Meaning and Synonyms"):
    if word:
        result_df = get_word_details(word)
        if result_df is not None:
            st.markdown(f"### Details for *{word}*:")
            st.dataframe(result_df)
    else:
        st.warning("Please enter a word!")
