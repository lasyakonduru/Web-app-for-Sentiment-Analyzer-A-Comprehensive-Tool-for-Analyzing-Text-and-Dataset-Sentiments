# -*- coding: utf-8 -*-
"""app

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Bm-oGBAkDjrtR3R0sKhTsJOi5ZbnoyUc
"""

# importing packages
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

nltk.download('punkt_tab')
nltk.download('stopwords')

# data loading

df = pd.read_csv("2011Tornado_Summary.csv")
df.head()

# Preprocessing function
def preprocess_text(text):
    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text)
    # Remove mentions and hashtags
    text = re.sub(r"@\w+|#\w+", '', text)
    # Remove special characters and numbers
    text = re.sub(r"[^a-zA-Z\s]", '', text)
    # Convert to lowercase
    text = text.lower()
    return text

# Applying preprocessing to the 'text' column
df['cleaned_text'] = df['text'].apply(preprocess_text)

# Displaying the first few rows
df[['text', 'cleaned_text']].head()

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# VADER Sentiment Analysis Function
def analyze_sentiment(text):
    scores = sia.polarity_scores(text)
    # Categorize sentiment
    if scores['compound'] >= 0.05:
        sentiment = 'Positive'
    elif scores['compound'] <= -0.05:
        sentiment = 'Negative'
    else:
        sentiment = 'Neutral'
    return sentiment, scores

# Analyzing dataset
def analyze_dataset(data):
    if "Cleaned Text" not in data.columns:
        data["Cleaned Text"] = data["Text"].apply(lambda x: x.lower())
    # Applying VADER sentiment analysis
    data["Sentiment"] = data["Cleaned Text"].apply(
        lambda x: analyze_sentiment(x)[0]
    )
    return data

data = pd.DataFrame({"Text": ["I love tornado shelters!", "This is so bad!", "the sun is rising."]})
data = analyze_dataset(data)
print(data)

# Predicting sentiment for new text
new_text = "eventhough there was a tornado last night, nothing happened"
cleaned_text = preprocess_text(new_text)
predicted_sentiment = analyze_sentiment(cleaned_text)

print(f"Text: {new_text}")
print(f"Predicted Sentiment: {predicted_sentiment}")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

# App navigation
st.sidebar.title("Sentiment Analyzer")
page = st.sidebar.radio("Navigate", ["Home", "Analysis", "Reports"])

# Function to preprocess and predict sentiments for a dataset
def preprocess_text(text):
    """
    Preprocess text for analysis.
    """
    return text.lower().strip()

def predict_sentiment(text):
    """
    Predict sentiment using VADER.
    """
    scores = sia.polarity_scores(text)
    # Determine sentiment based on compound score
    if scores["compound"] >= 0.05:
        sentiment = "Positive"
    elif scores["compound"] <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    return sentiment, scores

def analyze_dataset(data, text_column):
    """
    Analyze a dataset and predict sentiments for each row in the selected text column.
    """
    # Preprocess the text column
    data["Cleaned Text"] = data[text_column].apply(preprocess_text)
    # Predict sentiment for each row in the selected text column
    data["Sentiment"] = data["Cleaned Text"].apply(lambda x: analyze_sentiment(x)[0])
    return data

# Initializing session state
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None  # For dataset analysis
if "analysis_text" not in st.session_state:
    st.session_state.analysis_text = None  # For single text input
if "analysis_scores" not in st.session_state:
    st.session_state.analysis_scores = None  # For single text sentiment scores

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(to_email):
    message = Mail(
        from_email="data.user1237@gmail.com",
        to_emails=to_email,
        subject="Thank you for subscribing to the Sentiment Analyzer Newsletter!",
        html_content="""
        <p>Hello,</p>
        <p>Thank you for subscribing to the Sentiment Analyzer tool newsletter.</p>
        <p>Stay tuned for more updates, insights, and tools to help you analyze public sentiment with ease!</p>
        <p>Best regards,<br>Sentiment Analyzer Team</p>
        """,
    )

    try:
        sg = SendGridAPIClient("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")
        response = sg.send(message)
        print("Email sent successfully:", response.status_code)
    except Exception as e:
        print(f"Error: {e}")

if page == "Home":
    st.title("Sentiment Analyzer")
    st.write("To understand public sentiment during events in real-time.")
    st.write(
        "Our app helps organizations analyze sentiment for data to provide actionable insights, "
        "understand public opinion, and enhance decision-making.\n\nGo and analyze the Sentiment now to unlock valuable insights!"
    )

    # Email input
    user_email = st.text_input(
        "Follow the latest trends with our daily newsletter",
        placeholder="you@example.com",
    )

    if st.button("Submit"):
        if user_email.strip() == "":
            st.warning("Please enter a valid email address.")
        else:
            try:
                send_email(user_email)
                st.success(
                    f"Thank you for subscribing! A confirmation email has been sent to {user_email}."
                )
            except Exception as e:
                st.error(f"Failed to send email. Please try again later. Error: {e}")

elif page == "Analysis":
    st.title("Analysis")
    st.write("Analyze the sentiment of data or text.")

    # Choose input option
    input_option = st.radio("Select input type:", ["Upload a CSV file", "Enter a single text"])

    if input_option == "Upload a CSV file":
        # File upload
        uploaded_file = st.file_uploader("Upload a CSV file:", type=["csv"])
        if uploaded_file:
            # Load the dataset
            data = pd.read_csv(uploaded_file)
            st.write("### Uploaded Dataset")
            st.dataframe(data.head())

            # Allow user to select text column
            text_column = st.selectbox(
                "Select the column containing text:",
                options=data.columns,
                help="Choose the column to perform sentiment analysis on.",
            )

            # Analyze dataset
            if st.button("Analyze Dataset"):
                data = analyze_dataset(data, text_column)
                st.session_state.analysis_data = data  # Save to session state
                st.session_state.text_column = text_column  # Save column name
                st.write("### Analyzed Dataset")
                st.dataframe(data[[text_column, "Sentiment"]].head())

    elif input_option == "Enter a single text":
        # Text input for analysis
        user_input = st.text_area("Enter a text:", placeholder="Type something...")
        if st.button("Analyze Sentiment"):
            if user_input.strip() == "":
                st.warning("Please enter some text to analyze.")
            else:
                sentiment, scores = analyze_sentiment(user_input)
                st.session_state.analysis_text = user_input
                st.session_state.analysis_scores = scores
                st.subheader(f"Predicted Sentiment: {sentiment}")
                st.write("Sentiment Scores:")
                st.json(scores)

elif page == "Reports":
    st.title("Reports")
    st.write("View sentiment analysis results.")

    if st.session_state.get("analysis_data") is not None:
        # Dataset analysis reports
        data = st.session_state.analysis_data
        text_column = st.session_state.text_column

        st.write("### Analyzed Data Preview")

        # Dynamic row control for displaying analyzed data
        rows_to_display = st.slider(
            "Rows to display", 
            min_value=5, 
            max_value=min(100, len(data)),  
            value=10
        )
    
        # Display only the selected text column and sentiment
        st.dataframe(data[[text_column, "Sentiment"]].head(rows_to_display))

        # Visualize sentiment distribution (Pie Chart)
        st.write("### Sentiment Distribution (Pie Chart)")
        sentiment_counts = data["Sentiment"].value_counts()
        fig, ax = plt.subplots()
        ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct="%1.1f%%", startangle=90)
        ax.set_title("Sentiment Distribution")
        st.pyplot(fig)

        # Sentiment Distribution (Bar Chart)
        st.write("### Sentiment Distribution (Bar Chart)")
        fig, ax = plt.subplots()
        sentiment_counts.plot(kind="bar", color=["green", "orange", "red"], ax=ax)
        ax.set_ylabel("Count")
        ax.set_title("Sentiment Distribution")
        st.pyplot(fig)

        # Line Chart: Sentiment trends over time
        if "timestamp" in data.columns:
            st.write("### Sentiment Trends Over Time")
            data["timestamp"] = pd.to_datetime(data["timestamp"])  # Ensure timestamp is datetime
            sentiment_trends = data.groupby([data["timestamp"].dt.date, "Sentiment"]).size().unstack(fill_value=0)
            fig, ax = plt.subplots()
            sentiment_trends.plot(ax=ax)
            ax.set_ylabel("Count")
            ax.set_xlabel("Date")
            ax.set_title("Sentiment Trends Over Time")
            st.pyplot(fig)

        # Histogram: Distribution of compound scores
        if "Cleaned Text" in data.columns:
            st.write("### Compound Score Distribution")
            data["Compound Score"] = data["Cleaned Text"].apply(lambda x: sia.polarity_scores(x)["compound"])
            fig, ax = plt.subplots()
            ax.hist(data["Compound Score"], bins=20, color="blue", alpha=0.7)
            ax.set_title("Compound Score Distribution")
            ax.set_xlabel("Compound Score")
            ax.set_ylabel("Frequency")
            st.pyplot(fig)

        # Word Cloud: Most frequent words for each sentiment
        from wordcloud import WordCloud

        st.write("### Word Clouds for Each Sentiment")
        sentiments = data["Sentiment"].unique()
        for sentiment in sentiments:
            sentiment_words = " ".join(data[data["Sentiment"] == sentiment]["Cleaned Text"])
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(sentiment_words)
            st.subheader(f"Most Frequent Words in {sentiment} Sentiment")
            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)

        # Option to download analyzed dataset
        csv = data.to_csv(index=False)
        st.download_button(
            label="Download Analyzed Dataset",
            data=csv,
            file_name="analyzed_dataset.csv",
            mime="text/csv",
        )

    elif st.session_state.get("analysis_text") is not None:
        # Single text analysis reports
        user_input = st.session_state.analysis_text
        scores = st.session_state.analysis_scores

        st.write("### Analyzed Text")
        st.write(f"**Input Text:** {user_input}")

        # Visualize sentiment scores (Bar Chart)
        st.write("### Sentiment Scores (Bar Chart)")
        fig, ax = plt.subplots()
        ax.bar(scores.keys(), scores.values(), color=["green", "orange", "red"])
        ax.set_ylabel("Score")
        ax.set_title("Sentiment Score Breakdown")
        st.pyplot(fig)

    else:
        st.warning("No analysis data available. Please perform analysis first.")
