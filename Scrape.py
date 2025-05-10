import streamlit as st
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from typing import Union, List, Dict

def scrape_webpage(url: str) -> Union[str, None]:
    """
    Scrapes the text content from a given URL.

    Args:
        url (str): The URL of the webpage to scrape.

    Returns:
        str: The text content of the webpage, or None if an error occurs.
    """
    try:
        # Add a user-agent to the request to avoid being blocked by some websites.
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)  # Set a timeout
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')
        # Remove script and style tags to get only the meaningful text
        for script_or_style in soup.find_all(['script', 'style']):
            script_or_style.decompose()
        text = soup.get_text(separator='\n', strip=True)  # Use \n as separator and strip text
        return text
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching URL: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None



def extract_data(text: str) -> List[Dict[str, Union[str, int, float]]]:
    """
    Extracts data from the text, attempting to identify different data types.

    Args:
        text (str): The text to extract data from.

    Returns:
        List[Dict[str, Union[str, int, float]]]: A list of dictionaries, where each dictionary
        represents a data entry with 'type' and 'value' keys.
    """
    data_list = []
    lines = text.split('\n')  # Split the text into lines

    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespace
        if not line:
            continue  # Skip empty lines

        # Attempt to identify data type and extract value
        if re.match(r'^\d+$', line):
            data_list.append({'type': 'integer', 'value': int(line)})
        elif re.match(r'^\d+\.\d+$', line):
            data_list.append({'type': 'float', 'value': float(line)})
        else:
            data_list.append({'type': 'string', 'value': line})

    return data_list



def preprocess_data(data: List[Dict[str, Union[str, int, float]]]) -> pd.DataFrame:
    """
    Preprocesses the extracted data and converts it into a Pandas DataFrame.

    Args:
        data (List[Dict[str, Union[str, int, float]]]): The data to preprocess.

    Returns:
        pd.DataFrame: A Pandas DataFrame representing the preprocessed data.
    """
    df = pd.DataFrame(data)
    return df



def main():
    """
    Main function to run the Streamlit application.
    """
    st.title("Web Scraper and Data Preprocessor")

    url = st.text_input("Enter the URL of the webpage to scrape:")

    if st.button("Scrape and Preprocess"):
        if not url:
            st.error("Please enter a URL.")
            return

        st.spinner("Scraping and processing data...")
        text_content = scrape_webpage(url)
        if text_content:
            extracted_data = extract_data(text_content)
            if extracted_data:
                df = preprocess_data(extracted_data)
                st.subheader("Extracted Data:")
                st.dataframe(df)  # Display as DataFrame
                #  Add a download button
                csv_data = df.to_csv(index=False)  # Get CSV data
                csv_size_bytes = sys.getsizeof(csv_data.encode('utf-8'))
                csv_size_kb = csv_size_bytes / 1024
                st.write(f"CSV File Size: {csv_size_kb:.2f} KB")
                st.download_button(
                    label="Download CSV",
                    data=csv_data.encode('utf-8'),
                    file_name="scraped_data.csv",
                    mime="text/csv",
                )
            else:
                st.warning("No data could be extracted from the webpage.")
        else:
            st.error("Failed to scrape data from the webpage.") # Error already shown by scrape_webpage, show generic
            return

if __name__ == "__main__":
    main()
