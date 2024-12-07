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
                                           f"If there are multiple meanings, number them (e.g., Meaning 1:, Meaning 2:)."
                                           f"Show example sentence of every meaning of '{word}'."},
            ],
        )

        content = response.choices[0].message.content

        meaning = None
        synonyms = []
        example = None

        for line in content.split("\n"):
            if line.lower().startswith("meaning:"):
                meaning = line.split(":", 1)[1].strip()
            elif line.lower().startswith("synonyms:"):
                synonyms = [syn.strip() for syn in line.split(":", 1)[1].split(",")]
            elif line.lower().startswith("example:"):
                example = line.split(":", 1)[1].strip()

        if not meaning:
            st.error("Could not retrieve the meaning of the word.")
            return None

        df = pd.DataFrame({
            "Word": [word],
            "Meaning": [meaning],
            "Synonyms": [", ".join(synonyms) if synonyms else "N/A"],
            "Example": [example if example else "N/A"]
        })
        return df

    except openai.error.AuthenticationError:
        st.error("Authentication error: Please check your API key.")
    except openai.error.RateLimitError:
        st.error("Rate limit exceeded: Too many requests. Try again later.")
    except openai.error.OpenAIError as e:
        st.error(f"OpenAI error: {e}")
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
