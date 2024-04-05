import difflib
import os

import requests
import seaborn as sns
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_ENDPOINT = os.getenv("API_ENDPOINT")

# Frontend Settings
bias_type_categories = [
    'Framing Bias - Word Choice', 'Framing Bias - Labeling', 'Epistemological Bias - Misleading use of verbs',
    'Demographic Bias - Stereotyping roles/attributes',
    'Demographic Bias - Use of both feminine and masculine reference words.'

]

bias_colors = sns.color_palette("pastel", n_colors=len(bias_type_categories)).as_hex()

color_dict = {}
for bias_color, bias_type_category in zip(bias_colors, bias_type_categories):
    color_dict[bias_type_category] = bias_color


def colorize_multiselect_options(detected_bias_types: list[str]) -> None:
    custom_css = """
        <style>
            {options_css}
        </style>
    """
    options_css = ""

    for option  in detected_bias_types:
        color = color_dict[option]
        options_css += f"""
            /* Change the badge background color based on option */
            span[data-baseweb="tag"]:has(span[title="{option}"])  {{
                background-color: {color};
                color: black; /* Change text color if needed */
            }}
        """

    st.markdown(custom_css.format(options_css=options_css), unsafe_allow_html=True)


def request_response_from_model(article):
    payload = {"article": article}  # Constructing the request payload
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.post(API_ENDPOINT,
                      headers=headers,
                      data=payload)
    return r.json()


def highlight_changes_in_revision(model_output, revisions):
    highlighted_revised_full_text = model_output['input']
    for revision in revisions:
        original_sentence = revision['sentence']
        highlighted_sentence = ''
        changes = revision['changes']
        for change in changes:
            if change[0] == 0:
                highlighted_sentence += change[1]
            elif change[0] == -1:
                original_text = change[1]
                crossed_text = f'<span style="text-decoration: line-through; color: red;">{original_text}</span>'
                highlighted_sentence += crossed_text
            else:
                original_text = change[1]
                added_text = f'<span style="color: green;">{original_text}</span>'
                highlighted_sentence += added_text
        highlighted_revised_full_text = highlighted_revised_full_text.replace(original_sentence, highlighted_sentence)
    return highlighted_revised_full_text


# Function to highlight sentences based on model output
def highlight_sentences(text, model_output):
    highlighted_text = ""
    sentences = text.split('. ')  # Split text into sentences (assuming period-space is the sentence separator)

    for i, sentence in enumerate(sentences):
        if i in model_output:
            highlighted_text += f"<mark>{sentence}</mark> "
        else:
            highlighted_text += f"{sentence}. "

    return highlighted_text


def find_differences(text_1, text_2):
    """
    Find the differences between two texts.

    Args:
    text_1 (str): The first text.
    text_2 (str): The second text.

    Returns:
    list: A list of strings representing the differences between the two texts.
    """
    # Create a SequenceMatcher object
    matcher = difflib.SequenceMatcher(None, text_1, text_2)

    # Get the differences between the texts
    diff_chunks = matcher.get_opcodes()

    # Initialize list to store differences
    differences = []

    for tag, i1, i2, j1, j2 in diff_chunks:
        # Append differences to the list
        if tag == 'insert':
            differences.append((None, text_2[j1:j2]))
        elif tag == 'delete':
            differences.append((text_1[i1:i2], None))

    return differences


def colorize_bias_spans(biased_text, selected_bias_types, model_output):
    for bias_type in model_output['bias_types']:
        if bias_type['bias_type'] not in selected_bias_types:
            continue
        bias_span = bias_type['span']
        selected_color = color_dict[bias_type['bias_type']]
        biased_text = biased_text.replace(bias_span,
                                          f'<span style="background-color: {selected_color}; padding: 0 5px;">{bias_span}</span>')
    return biased_text


# Streamlit app
def main():
    st.title("BiasBlocker-AI Demonstration")

    # Input text
    text = st.text_area("Paste the news article:", height=500)

    if 'clicked' not in st.session_state:
        st.session_state.clicked = False

    def set_clicked():
        st.session_state.clicked = True

    # Highlight button
    st.button("Check Biases", on_click=set_clicked)

    if st.session_state.clicked:
        # Highlight sentences based on model output
        model_output = request_response_from_model(article=text)

        st.subheader("Analysis by the Model")
        biased = model_output['biased']
        if biased:
            st.markdown('The text contains text spans introducing bias.')
            st.markdown('The bias topics that the model found are as follows:')

            for bias_topic in model_output['bias_topics']:
                st.markdown(f'- {bias_topic}')

            detected_bias_types = list(set(list(map(lambda x: x['bias_type'], model_output['bias_types']))))
            # we add all if user wants to all detected bias types
            detected_bias_types.append('all')
            st.markdown(f'\n\n')

            biased_text = model_output['input']
            st.subheader("Highlights - Fine-grained Bias Types")
            st.markdown(':gray[Choose Bias Type(s) to highlight]:')
            selected_bias_types = st.multiselect('', detected_bias_types)
            colorize_multiselect_options(color_dict)

            if 'all' in selected_bias_types:
                detected_bias_types.remove("all")
                selected_bias_types = detected_bias_types

            biased_text = colorize_bias_spans(biased_text, selected_bias_types, model_output)
            st.markdown(biased_text, unsafe_allow_html=True)

            st.subheader("Model's Revision")

            revisions = model_output['revisions']

            highlighted_revised_full_text = highlight_changes_in_revision(model_output, revisions)
            st.markdown(highlighted_revised_full_text, unsafe_allow_html=True)


        else:
            st.markdown('The model didn\'t detect any bias.')


if __name__ == "__main__":
    main()
