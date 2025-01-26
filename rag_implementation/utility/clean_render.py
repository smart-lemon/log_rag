import textwrap

def get_llm(llm, text_prompt: str) -> str:
    return llm.invoke(text_prompt)

# Define the column width for text wrapping
# (Medium's typical width is around 80 characters)
COLUMN_WIDTH: int = 76

def clean_text(text: str) -> str:
    # Remove newline characters and any other special characters
    cleaned_text = text.replace('\n', ' ').replace('\r', '').strip()
    return cleaned_text

def wrap_text(text: str, width: int) -> str:
    # Use textwrap to wrap text to the specified width
    wrapped_text = textwrap.fill(text, width=width)
    return wrapped_text

def wrap_text_with_comments(text: str, width: int) -> str:
    # First wrap the text to specified width, which is < 80 char
    # by which we create out text lines
    wrapped_text = textwrap.fill(text, width=width)

    # Split the wrapped text
    lines = wrapped_text.split('\n')

    # Add # character for each line and join the lines
    commented_lines = ['# ' + line for line in lines]
    commented_text = '\n'.join(commented_lines)
    return commented_text

def get_llm_response(llm, text_prompt: str) -> str:
    # Get the response from the model
    response = llm.invoke(text_prompt)
    # Clean the output text
    cleaned_response = clean_text(response)
    # Wrap the cleaned response text to the specified column width
    wrapped_response = wrap_text_with_comments(cleaned_response, COLUMN_WIDTH)
    return wrapped_response