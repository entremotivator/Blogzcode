import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.title("🧹 Bulk Blog Cleaner")
st.write("Upload a CSV of blogs, and this tool will remove ALL <h2> blocks and strip empty <p> tags.")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

# Regex patterns
remove_h2 = re.compile(r"<h2>.*?</h2>", flags=re.DOTALL | re.IGNORECASE)
remove_empty_p = re.compile(r"<p>\s*(?:&nbsp;)?\s*</p>", flags=re.IGNORECASE)

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.write("✅ File uploaded successfully. Preview of data:")
    st.dataframe(df.head())

    # Select which column has blog text
    text_column = st.selectbox(
        "Select the column containing blog content:",
        df.columns
    )

    if st.button("🧹 Clean Blogs"):
        def clean_text(text):
            text = re.sub(remove_h2, "", str(text))       # Remove all <h2> blocks
            text = re.sub(remove_empty_p, "", text)       # Remove empty <p> tags
            return text.strip()

        df["cleaned_content"] = df[text_column].apply(clean_text)

        st.success("🎉 Cleaning complete! Preview of cleaned blogs:")
        st.dataframe(df[[text_column, "cleaned_content"]].head())

        # Download as CSV
        buffer = BytesIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)

        st.download_button(
            "📥 Download Cleaned CSV",
            data=buffer,
            file_name="cleaned_blogs.csv",
            mime="text/csv"
        )
