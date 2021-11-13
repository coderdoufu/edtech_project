# Third party import
import streamlit as st
import streamlit_authenticator as stauth

# scrapy
from edtech.run_scraper import Scraper

# General import
import os
import json
import re
import time
from retry import retry
from dotenv import load_dotenv
load_dotenv()

@retry(exceptions=ValueError, tries=5, delay=6)
def open_json(output_file):
    with open(output_file,'r') as f:
        result = json.load(f)
        out = {}
        for sent_key in result:
            searchkey = sent_key['searchKey']
            sentence = sent_key['sentence']
            if out.get(searchkey,None):
                out[searchkey] += [sentence]
            else:
                out[searchkey] = [sentence]
                
    return out

output_file = 'edtech/edtech/data/cn_sentences.json'

if os.path.isfile(output_file):
    os.remove(output_file)

add_selectbox = st.sidebar.selectbox(
    "How would you like to be contacted?",
    ("Email", "Home phone", "Mobile phone")
)

# get keywords from user
searchKeys = st.text_area('Give me your choice of comma separated keywords.',placeholder="tissue, gigantic, surreal")

# post processing keywords
searchKeys = [x.strip() for x in re.split('，|,',searchKeys) if x.strip()]

searchKeys = st.multiselect(
    'Please check if these are all the keywords that you want',
    searchKeys,searchKeys)

if st.button('Search'):
    with st.spinner('Generating sentences based on your input keywords ...'):
        scraper = Scraper()
        scraper.run_spiders(searchKeys=searchKeys)
        while not os.path.isfile(output_file) or os.path.getsize(output_file) == 0: 
            pass

    with st.spinner('Loading result ...'):
        result = open_json(output_file)

    st.success('Done!')
    st.write(result)

    