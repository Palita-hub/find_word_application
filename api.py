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

        st.text("Raw Response from OpenAI:")
        st.text(content)

        meanings = []
        synonyms_list = []
        examples = []

        try:
            parts = content.split("###")
            for part in parts:
                if "Meaning" in part:
                    meanings.append(part.split(":", 1)[1].strip())
                elif "Synonyms" in part:
                    synonyms = part.split(":", 1)[1].strip()
                    synonyms_list.append(synonyms if synonyms else "N/A")
                elif "Example" in part:
                    example = part.split(":", 1)[1].strip()
                    examples.append(example if example else "N/A")

            max_len = max(len(meanings), len(synonyms_list), len(examples))
            meanings.extend(["N/A"] * (max_len - len(meanings)))
            synonyms_list.extend(["N/A"] * (max_len - len(synonyms_list)))
            examples.extend(["N/A"] * (max_len - len(examples)))

            df = pd.DataFrame({
                "Meaning": meanings,
                "Synonyms": synonyms_list,
                "Example": examples
            })
            return df
        except Exception as parse_error:
            st.error(f"Parsing error: {parse_error}")
            st.warning("The response could not be processed. Here's the raw output:")
            st.text(content)
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
