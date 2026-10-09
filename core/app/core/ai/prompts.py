# prompts.py

TRANSCRIPT_SUMMARY_PROMPT = """
I have a detailed transcript and I'd like you to summarize it in a clean, tidy, and well-organized manner. Present the content in a first-person perspective, using a style similar to the original transcript but with improved formatting to make it visually appealing, entertaining and easy to follow. The summary should capture all key details and be formatted in a way that's clear, professional, and engaging.

Structure all the output inside a <div></div> and the text into suitable html tags. Give the raw html output without backticks.
Be detailed as possible, with a good flow for reading, highly comprehensible, more entertaining.

Title: {video_title}
Content: {transcript_text}
"""

SUBJECT_LINE_PROMPT = """
Create an exciting, clickbaity 4-9 word subject line for an email newsletter summarizing the following YouTube video titles:
{video_titles}

The output from you must not contain any enclosing quotes or brackets.
"""

VIDEO_TITLE_SUMMARY_PROMPT = """
Give me a hyper short dynamic 1-sentence summary created by analyzing today’s video titles.
{video_titles}

The summary should be catchy and informative, highlighting the most interesting themes or topics.
"""