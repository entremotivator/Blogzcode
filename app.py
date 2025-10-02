import streamlit as st
import pandas as pd
import re
from io import BytesIO
from html.parser import HTMLParser

st.set_page_config(page_title="Blog Cleaner", page_icon="🧹", layout="wide")

st.title("🧹 Advanced Blog Content Cleaner")
st.write("Remove code blocks, unwanted HTML elements, and clean up your blog content efficiently.")

# Sidebar configuration
st.sidebar.header("⚙️ Cleaning Options")
remove_h2 = st.sidebar.checkbox("Remove all <h2> headings", value=True)
remove_empty_p = st.sidebar.checkbox("Remove empty <p> tags", value=True)
remove_code = st.sidebar.checkbox("Remove <code> and <pre> blocks", value=True)
remove_script = st.sidebar.checkbox("Remove <script> tags", value=True)
remove_style = st.sidebar.checkbox("Remove <style> tags", value=True)
remove_comments = st.sidebar.checkbox("Remove HTML comments", value=True)
normalize_whitespace = st.sidebar.checkbox("Normalize whitespace", value=True)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Select only the cleaning operations you need for optimal results.")

# File uploader
uploaded_file = st.file_uploader(
    "📁 Upload your CSV file", 
    type=["csv"],
    help="Upload a CSV file containing blog content to clean"
)


def clean_html_content(text, options):
    """
    Comprehensively clean HTML content based on selected options.
    """
    if pd.isna(text) or not isinstance(text, str):
        return ""
    
    original_text = text
    
    # Remove script tags and their content
    if options['remove_script']:
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove style tags and their content
    if options['remove_style']:
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove code blocks (pre and code tags)
    if options['remove_code']:
        text = re.sub(r'<pre[^>]*>.*?</pre>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<code[^>]*>.*?</code>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML comments
    if options['remove_comments']:
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    # Remove h2 blocks
    if options['remove_h2']:
        text = re.sub(r'<h2[^>]*>.*?</h2>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove empty paragraph tags (including those with only &nbsp; or whitespace)
    if options['remove_empty_p']:
        text = re.sub(r'<p[^>]*>\s*(?:&nbsp;|\s)*\s*</p>', '', text, flags=re.IGNORECASE)
    
    # Normalize whitespace
    if options['normalize_whitespace']:
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple blank lines to double
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single
        text = text.strip()
    
    return text


if uploaded_file:
    try:
        # Read CSV with error handling
        df = pd.read_csv(uploaded_file, encoding='utf-8')
        
        st.success(f"✅ File uploaded successfully! Found {len(df)} rows and {len(df.columns)} columns.")
        
        # Preview original data
        with st.expander("👀 Preview Original Data", expanded=True):
            st.dataframe(df.head(10), use_container_width=True)
        
        # Column selection
        text_column = st.selectbox(
            "📝 Select the column containing blog content:",
            options=df.columns,
            help="Choose the column that contains the HTML content to clean"
        )
        
        # Show sample of selected column
        if text_column:
            st.markdown("### Sample from selected column:")
            sample_text = str(df[text_column].iloc[0])[:500]
            st.text_area("First entry preview:", sample_text, height=100, disabled=True)
        
        # Clean button
        if st.button("🧹 Clean All Blogs", type="primary", use_container_width=True):
            with st.spinner("Cleaning in progress..."):
                # Prepare cleaning options
                cleaning_options = {
                    'remove_h2': remove_h2,
                    'remove_empty_p': remove_empty_p,
                    'remove_code': remove_code,
                    'remove_script': remove_script,
                    'remove_style': remove_style,
                    'remove_comments': remove_comments,
                    'normalize_whitespace': normalize_whitespace
                }
                
                # Apply cleaning
                df["cleaned_content"] = df[text_column].apply(
                    lambda x: clean_html_content(x, cleaning_options)
                )
                
                # Calculate statistics
                original_lengths = df[text_column].astype(str).str.len()
                cleaned_lengths = df["cleaned_content"].str.len()
                total_removed = (original_lengths - cleaned_lengths).sum()
                avg_reduction = ((original_lengths - cleaned_lengths) / original_lengths * 100).mean()
                
                st.success("🎉 Cleaning complete!")
                
                # Show statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Characters Removed", f"{total_removed:,}")
                with col2:
                    st.metric("Average Reduction", f"{avg_reduction:.1f}%")
                with col3:
                    st.metric("Rows Processed", len(df))
                
                # Preview cleaned results
                with st.expander("👀 Preview Cleaned Results", expanded=True):
                    comparison_df = df[[text_column, "cleaned_content"]].head(10)
                    comparison_df.columns = ["Original", "Cleaned"]
                    st.dataframe(comparison_df, use_container_width=True)
                
                # Prepare download
                buffer = BytesIO()
                df.to_csv(buffer, index=False, encoding='utf-8')
                buffer.seek(0)
                
                st.download_button(
                    label="📥 Download Cleaned CSV",
                    data=buffer,
                    file_name="cleaned_blogs.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
                
                # Option to download only cleaned column
                buffer_minimal = BytesIO()
                df[["cleaned_content"]].to_csv(buffer_minimal, index=False, encoding='utf-8')
                buffer_minimal.seek(0)
                
                st.download_button(
                    label="📥 Download Only Cleaned Content",
                    data=buffer_minimal,
                    file_name="cleaned_content_only.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("Please ensure your CSV file is properly formatted and encoded in UTF-8.")

else:
    # Instructions when no file is uploaded
    st.info("👆 Please upload a CSV file to get started")
    
    with st.expander("📖 How to use this tool"):
        st.markdown("""
        ### Step-by-step guide:
        
        1. **Configure cleaning options** in the sidebar (left panel)
        2. **Upload your CSV file** containing blog content
        3. **Select the column** that contains the HTML content
        4. **Preview** your selection to ensure it's correct
        5. **Click "Clean All Blogs"** to process the content
        6. **Download** the cleaned CSV file
        
        ### What gets cleaned:
        
        - **Code blocks**: Removes `<pre>` and `<code>` tags with their content
        - **Scripts**: Removes `<script>` tags (security improvement)
        - **Styles**: Removes `<style>` tags
        - **H2 headings**: Removes all `<h2>` blocks
        - **Empty paragraphs**: Removes `<p>` tags with no content
        - **HTML comments**: Removes `<!-- -->` comments
        - **Whitespace**: Normalizes excessive line breaks and spaces
        """)
