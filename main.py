import streamlit as st
import pandas as pd
import io
from scrape import scrape_website, split_dom_content, clean_body_content, extract_body_content
from parse import parse_with_ollama

st.title(" AI Web Scraper ")

url = st.text_input("Enter a Website URL:")

if st.button("Scrape site"):
    if url.strip() == "":
        st.error("Please enter a valid URL.")
    else:
        try:
            with st.spinner("Scraping in progress..."):
                result = scrape_website(url)
                body_content = extract_body_content(result)
                cleaned_content = clean_body_content(body_content)

                st.session_state.dom_content = cleaned_content

            with st.expander("View Extracted DOM Content"):
                st.text_area("DOM Content", cleaned_content, height=300)

        except Exception as e:
            st.error(f"An error occurred while scraping: {e}")


if "dom_content" in st.session_state:
    parse_description = st.text_area(" Describe what you want to extract:")

    if st.button("Parse Content"):
        if parse_description.strip():
            st.write(" Parsing the content...")
            dom_chunks = split_dom_content(st.session_state.dom_content)

            parsed_result = parse_with_ollama(dom_chunks, parse_description)


            st.success(" Parsing complete!")
            if parsed_result.strip().startswith("|"):           
                try:
                    
                    df = pd.read_csv(io.StringIO(parsed_result), sep="|", engine='python', skipinitialspace=True)
                    df = df.dropna(axis=1, how="all").dropna(axis=0, how="all")  # Clean up extra NaNs
                    st.write("Extracted Table")
                    st.dataframe(df)
                except Exception as e:
                    st.text_area("Parsed Result (raw)", parsed_result, height=400)
                    st.warning(f"Couldn't render table: {e}")
            else:
                st.text_area("Parsed Result", parsed_result, height=400)
        else:
            st.warning("Please provide a description for parsing.")