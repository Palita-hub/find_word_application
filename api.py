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
                     "content": f"Provide detailed information about the word '{word}' in this exact structured format:\n"
                                "### Meaning 1:\n"
                                "[Meaning]\n"
                                "### Synonyms 1:\n"
                                "[Comma-separated list of synonyms]\n"
                                "### Example 1:\n"
                                "[Example sentence]\n"
                                "### Meaning 2 (if any):\n"
                                "[Meaning]\n"
                                "### Synonyms 2:\n"
                                "[Comma-separated list of synonyms]\n"
                                "### Example 2:\n"
                                "[Example sentence]"},
                ],
                max_tokens=500,
                temperature=0.7
            )

        content = response.choices[0].message.content.strip()

        meanings = []
        synonyms_list = []
        examples = []
        parts_of_speech = []

        try:
            parts = content.split("###")
            for part in parts:
                if "Meaning" in part:
                    meanings.append(part.split(":", 1)[1].strip())
                elif "Synonyms" in part:
                    synonyms = part.split(":", 1)[1].strip()
                    synonyms_list.append(synonyms if synonyms else "Synonyms not found")
                elif "Example" in part:
                    example = part.split(":", 1)[1].strip()
                    examples.append(example if example else "Not found")
                elif "Part of Speech" in part:
                    part_of_speech = part.split(":", 1)[1].strip()
                    parts_of_speech.append(part_of_speech if part_of_speech else "Not found")

            max_len = max(len(meanings), len(synonyms_list), len(examples), len(parts_of_speech))
            meanings.extend(["N/A"] * (max_len - len(meanings)))
            synonyms_list.extend(["N/A"] * (max_len - len(synonyms_list)))
            examples.extend(["N/A"] * (max_len - len(examples)))
            parts_of_speech.extend(["N/A"] * (max_len - len(parts_of_speech)))

            df = pd.DataFrame({
                "Word": [word] * max_len,
                "Part of Speech": parts_of_speech,
                "Meaning": meanings,
                "Synonyms": synonyms_list,
                "Example": examples
            })
            return df
        except Exception as parse_error:
            st.error(f"Parsing error: {parse_error}")
            return None

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
