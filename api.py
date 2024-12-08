import openai
import streamlit as st
import pandas as pd
import random

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
                                "### Part of Speech 1:\n"
                                "[Part of speech for this meaning]\n"
                                "### Synonyms 1:\n"
                                "[Comma-separated list of synonyms]\n"
                                "### Example 1:\n"
                                "[Example sentence]\n"
                                "### Meaning 2 (if any):\n"
                                "[Meaning]\n"
                                "### Part of Speech 2:\n"
                                "[Part of speech for this meaning]\n"
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
                    synonyms_list.append(synonyms if synonyms else "N/A")
                elif "Example" in part:
                    example = part.split(":", 1)[1].strip()
                    examples.append(example if example else "N/A")
                elif "Part of Speech" in part:
                    part_of_speech = part.split(":", 1)[1].strip()
                    parts_of_speech.append(part_of_speech if part_of_speech else "N/A")

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
            return df, meanings, synonyms_list, examples
        except Exception as parse_error:
            st.error(f"Parsing error: {parse_error}")
            return None, None, None, None

    except openai.error.AuthenticationError:
        st.error("Authentication error: Please check your API key.")
    except openai.error.RateLimitError:
        st.error("Rate limit exceeded: Too many requests. Try again later.")
    except openai.error.OpenAIError as e:
        st.error(f"OpenAI error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

    return None, None, None, None

def shuffle_list(data_list):
    if 'shuffle_idx' not in st.session_state:
        st.session_state.shuffle_idx = list(range(len(data_list)))
    else:
        st.session_state.shuffle_idx = st.session_state.shuffle_idx[::-1]

    return [data_list[i] for i in st.session_state.shuffle_idx]

def generate_quiz(meanings, synonyms, examples):
    questions = [
        ("What is the correct meaning of the word based on its definition?", meanings),
        ("Which of the following are synonyms for the word?", synonyms),
        ("Which of these sentences uses the word correctly?", examples),
    ]

    shuffled_questions = []
    for question, options in questions:
        shuffled_questions.append((question, shuffle_list(options)))

    return shuffled_questions

if st.button("Find Meaning and Synonyms"):
    if word:
        result_df, meanings, synonyms_list, examples = get_word_details(word)
        if result_df is not None:
            st.markdown(f"### Details for *{word}*:")
            st.dataframe(result_df)

            questions = generate_quiz(meanings, synonyms_list, examples)
            for i, (question, options) in enumerate(questions):
                st.markdown(f"#### Question {i + 1}")
                options = random.shuffle(options)
                selected_option = st.radio(question, options, key=f"question_{i}")
                correct_answer = ['meanings','synonyms','examples']
                
                if selected_option:
                    if selected_option == correct_answer[i]:
                        st.success("Correct!")
                    else:
                        st.error("Incorrect.")
    else:
        st.warning("Please enter a word!")
