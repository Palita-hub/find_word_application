import openai
import streamlit as st
import pandas as pd

st.title("Word Meaning and Synonyms Finder")

api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")
if api_key:
    openai.api_key = api_key

word = st.text_input("What word are you looking for?")

def get_word_details(word):
    if not api_key:
        st.error("Please enter your API key in the sidebar.")
        return None

    if not word.strip().isalpha():
        st.warning("Enter a valid word containing only alphabets.")
        return None

    try:
        with st.spinner("Fetching details... Please wait."):
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an assistant specialized in language analysis."},
                    {"role": "user",
                     "content": f"Provide detailed information about the word '{word}' in this structured format:\n"
                                "1. Meaning: [First meaning]\n"
                                "   Synonyms: [Comma-separated list of synonyms for this meaning]\n"
                                "   Example: [Example sentence using the word with this meaning]\n"
                                "2. Meaning: [Second meaning, if any]\n"
                                "   Synonyms: [Comma-separated list of synonyms for this meaning]\n"
                                "   Example: [Example sentence using the word with this meaning]"},
                ],
                max_tokens=500,
                temperature=0.7
            )

        content = response.choices[0].message.content.strip()

        meanings = []
        synonyms_list = []
        examples = []

        current_meaning = None
        current_synonyms = []
        current_example = None

        for line in content.split("\n"):
            line = line.strip()
            if line.lower().startswith("meaning:"):
                if current_meaning:
                    meanings.append(current_meaning)
                    synonyms_list.append(", ".join(current_synonyms) if current_synonyms else "N/A")
                    examples.append(current_example if current_example else "N/A")
                current_meaning = line.split(":", 1)[1].strip()
                current_synonyms = []
                current_example = None
            elif line.lower().startswith("synonyms:"):
                current_synonyms = [syn.strip() for syn in line.split(":", 1)[1].split(",") if syn]
            elif line.lower().startswith("example:"):
                current_example = line.split(":", 1)[1].strip()

        if current_meaning:
            meanings.append(current_meaning)
            synonyms_list.append(", ".join(current_synonyms) if current_synonyms else "N/A")
            examples.append(current_example if current_example else "N/A")

        if not meanings:
            st.error("Couldn't retrieve the details of the word. Please try another word.")
            return None

        df = pd.DataFrame({
            "Meaning": meanings,
            "Synonyms": synonyms_list,
            "Example": examples
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
