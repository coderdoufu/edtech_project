# Third party import
import streamlit as st
import extra_streamlit_components as stx
import authenticator as stauth

# First party import
from common import _get_state, get_authentication_block, is_authenticated

# scrapy
from edtech.run_scraper import Scraper

# General import
import os
import numpy as np
import json
import re
from retry import retry
from dotenv import load_dotenv
import random
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

def select_sentence(results, selected_sentences, refresh_sentence_options):
    for ind, (keyword, sentences) in enumerate(results.items()):
        try:
            if refresh_sentence_options:
                sentence_options_ind = random.sample(range(0, len(sentences)), 5)
            sentences = np.array(sentences)
            sentence_options = list(sentences[sentence_options_ind])
        except:
            print(f'{keyword} has no enough sentences: {len(sentences)}')
            sentence_options = sentences
        
        selected_sentences[keyword] = st.radio(f"这是关于 {keyword} 的造句选择",
                                               sentence_options,
                                               key=str(ind))
    return selected_sentences

def main(state, **kwargs):
    output_file = 'edtech/edtech/data/cn_sentences.json'

    # sb_lang = kwargs.get("sb_lang",st.sidebar.empty())
    # sb_searchInp = kwargs.get("sb_searchInp",st.sidebar.empty())
    # sb_searchBtn = kwargs.get("sb_searchBtn",st.sidebar.empty())
    # ct_sent_selection_confirm = kwargs.get("ct_sent_selection_confirm",st.empty())
    # ct_sent_selection_refresh = kwargs.get("ct_sent_selection_refresh",st.empty())

    if os.path.isfile(output_file):
        os.remove(output_file)

    # language selection
    lang = st.sidebar.selectbox(
        "请选择语言",
        ("中文",""),
        index=0,
    )

    # get keywords from user
    # searchKeys = st.sidebar.text_area('Give me your choice of comma separated keywords.',placeholder="tissue, gigantic, surreal")
    searchInputs = st.sidebar.text_area('请输入您要的关键字，并且用逗号（，）来区分不同的关键字',placeholder="一五一十，慢条斯理，记账")

    # post processing keywords
    searchKeys = []
    if searchInputs:
        searchKeys = [x.strip() for x in re.split('，|,',searchInputs) if x.strip()]

    # searchKeys = sb_searchInp.multiselect(
    #     'Please check if these are all the keywords that you want',
    #     searchKeys,searchKeys)
    
    result = {}
    searchBtn = st.sidebar.button('🔍 即刻查询', key="searchBtn")

    if searchBtn and len(searchKeys)==0:
        st.warning('请输入关键字！')

    if searchBtn and len(searchKeys)>0:
        with st.spinner('Generating sentences based on your input keywords ...'):
            scraper = Scraper()
            scraper.run_spiders(searchKeys=searchKeys)
            while not os.path.isfile(output_file) or os.path.getsize(output_file) == 0: 
                pass

        with st.spinner('Loading result ...'):
            state.result = open_json(output_file)

        st.success('Done!')

        state.sentence_options_ind = {}
        state.selected_sentences = {}
        state.edited_sentences = {}
        for ind, (keyword, sentences) in enumerate(state.result.items()):
            try:
                state.sentence_options_ind[keyword] = random.sample(range(0, len(sentences)), 5)
            except:
                state.sentence_options_ind[keyword] = list(range(len(sentences)))

    st.markdown(
    """
    <style>
        .reportview-container .markdown-text-container {
            font-family: monospace;
        }
        .sidebar .sidebar-content {
            background-image: linear-gradient(#2e7bcf,#2e7bcf);
            color: white;
        }
        .Widget>label {
            color: white;
            font-family: monospace;
        }
        [class^="st-b"]  {
            color: white;
            font-family: monospace;
        }
        .stRadio>label {
            font-size: 18px;
        }
        .st-bb {
            background-color: transparent;
        }
        .st-at {
            margin: 10px 0;
            font-size: 12px;
        }
        [data-testid="stForm"]:hover {
            border-color: #9ecaed;
            box-shadow: 0 0 10px #9ecaed;
            outline: none;
        }
        footer {
            font-family: monospace;
        }
        .reportview-container .main footer, .reportview-container .main footer a {
            color: #0c0080;
        }
        header .decoration {
            background-image: none;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    if state.result:
        st.subheader("请选择你要的句子，按下“确定”键之后可以做二次修改。")
        # state.selected_sentences = select_sentence(
        #                             state.result, 
        #                             state.selected_sentences,
        #                             state.refresh_sentence_options)
        for ind, (keyword, sentences) in enumerate(state.result.items()):
            sentence_selection_form = st.form(keyword)
            sentences = np.array(sentences)
            sentence_options = list(sentences[state.sentence_options_ind[keyword]])            
            state.selected_sentences[keyword] = sentence_selection_form.radio(
                                                    f"{ind+1}: 这是关于 **{keyword}** 的造句选择",
                                                    sentence_options,
                                                    key=keyword)
            # state.edited_sentences[keyword] = sentence_selection_form.text_area(
            #                                         "选择的句子，可在此进行二次更改",
            #                                         state.selected_sentences[keyword])
            if sentence_selection_form.form_submit_button('Refresh'):
                try:
                    state.sentence_options_ind[keyword] = random.sample(range(0, len(sentences)), 5)
                except:
                    state.sentence_options_ind[keyword] = range(len(sentences))
    
        _, confirm_col = st.columns((1.5, 1))
        with confirm_col:
            confirm_selected_btn = st.button('我已选定句子，确定进行二次更改')
            if confirm_selected_btn:
                state.confirm_sentence_btn = not state.confirm_sentence_btn
    
    # if ct_sent_selection_refresh.button('Refresh Selection'):
    #     state.refresh_sentence_options = not state.refresh_sentence_options

    # if state.confirm_sentence_btn == True:
    #     break
        
    # for st_sentence_option in st_sentence_options:
    #     st_sentence_option.empty()

    # based on the returned result, select the sentence
    # select_sentence(result)

def authentication():
    # NAME = os.getenv('NAME')
    # USERNAME = os.getenv('USERNAME')
    # PASSWORD = os.getenv('PASSWORD')

    NAME = st.secrets["NAME"]
    USERNAME = st.secrets["USERNAME"]
    PASSWORD = st.secrets["PASSWORD"]

    state = _get_state()

    names = [NAME]
    usernames = [USERNAME]
    passwords = [PASSWORD]
    hashed_passwords = stauth.hasher(passwords).generate()
    authenticator = stauth.authenticate(names,usernames,hashed_passwords,
        'kiki_cookie','kiki_key',cookie_expiry_days=30)
    name, authentication_status = authenticator.login('Login','main')

    state = _get_state()
    # st_state_list = {"sb_lang":st.sidebar.empty(), 
    #                  "sb_searchInp":st.sidebar.empty(), 
    #                  "sb_searchBtn":st.sidebar.empty(),
    #                  "ct_sent_selection_confirm":st.empty(),
    #                  "ct_sent_selection_refresh":st.empty()}

    if authentication_status:
        # print(f"[LOGIN]authentication_status: {st.session_state['authentication_status']}")
        main(state)
    elif st.session_state['authentication_status'] == False:
        st.error('Username/password is incorrect')
    elif st.session_state['authentication_status'] == None:
        st.warning('Please enter your username and password')
        # print(f"[LOGOUT]authentication_status: {st.session_state['authentication_status']}")

    # Mandatory to avoid rollbacks with widgets, must be called at the end of your app
    state.sync()

if __name__ == "__main__":
    st.set_page_config(page_title="Sentence Autogenerator")
    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden; }
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    authentication()