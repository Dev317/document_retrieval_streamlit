__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import streamlit as st
import logging
logging.basicConfig(level=logging.DEBUG)
import tempfile

FOLDER = f"{tempfile.gettempdir()}/upload"
CHROMA_PATH = f"{tempfile.gettempdir()}/.chroma"
st.session_state["UPLOAD_FOLDER"] = FOLDER
st.session_state["CHROMA_PATH"] = CHROMA_PATH
if not os.path.exists(FOLDER):
    logging.info("Creating upload folder!")
    os.makedirs(FOLDER)