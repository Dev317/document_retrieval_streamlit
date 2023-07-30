__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from streamlit.connections import ExperimentalBaseConnection
import chromadb
from typing import List
import pandas as pd
from chromadb.utils.embedding_functions import *
import logging



class ChromaDBConnection(ExperimentalBaseConnection):

    def _connect(self, **kwargs) -> chromadb.Client:
        type = self._kwargs["client_type"]

        if type == "PersistentClient":
            path = self._kwargs["path"] if "path" in self._kwargs else "/tmp/.chromadb"

            if path.split("/")[0] != "tmp":
                raise Exception("Path should start with `/tmp`")

            return chromadb.PersistentClient(
                path=path,
            )

        if type == "HttpClient":
            return chromadb.HttpClient(
                host=self._kwargs["host"],
                port=self._kwargs["port"],
                ssl=self._kwargs["ssl"],
            )

        return chromadb.Client()

    def create_collection(self,
                          collection_name,
                          embedding_function_name,
                          config):

        embedding_function = DefaultEmbeddingFunction()
        if embedding_function_name == "VertexEmbedding":
            embedding_function = GoogleVertexEmbeddingFunction(**config)
        elif embedding_function_name == "OpenAIEmbedding":
            embedding_function = OpenAIEmbeddingFunction(**config)

        try:
            self._raw_instance.create_collection(name=collection_name,
                                                 embedding_function=embedding_function)
        except Exception as ex:
            raise ex

    def get_collection_names(self):
        collection_names = []
        collections = self._raw_instance.list_collections()
        for col in collections:
            collection_names.append(col.name)

        return collection_names

    def get_collection_data(self, collection_name, attributes: List = ["documents", "embeddings", "metadatas"]):
        collection = self._raw_instance.get_collection(collection_name)
        collection_data = collection.get(
            include=attributes
        )
        return pd.DataFrame(data=collection_data)

    def get_collection_embedding_function(self, collection_name):
        collection = self._raw_instance.get_collection(collection_name)
        return collection._embedding_function.__class__.__name__


st.header("ChromaDB Connection")


client_type = st.selectbox(
    label="Client Type",
    options=["PersistentClient", "HttpClient"]
)

if not client_type:
    st.warning("Please select a Client Type")


st.session_state["configuration"] = {}
st.session_state["configuration"]["client_type"] = client_type

if client_type == "PersistentClient":
    persistent_path = st.text_input(
        label="Persistent directory",
        placeholder="/tmp/.chroma"
    )
    st.session_state["configuration"]["path"] = persistent_path

if client_type == "HttpClient":
    host = st.text_input(label='Chroma host', placeholder="localhost")
    port = st.text_input(label='Chroma port', placeholder=8000)
    ssl = st.selectbox(
        label="SSL",
        options=[False, True]
    )

    st.session_state["configuration"]["host"] = host
    st.session_state["configuration"]["port"] = port
    st.session_state["configuration"]["ssl"] = ssl

def connectChroma():
    try:
        st.session_state["conn"] = st.experimental_connection("chromadb",
                                type=ChromaDBConnection,
                                **st.session_state["configuration"])

        st.session_state["is_connected"] = True

        st.toast(body='Connection established!',
                icon='✅')

        st.session_state["chroma_collections"] = st.session_state["conn"].get_collection_names()

    except Exception as ex:
        logging.error(f"Error: {str(ex)}")
        st.toast(body="Failed to establish connection",
                icon="❌")


st.button(label="Connect", on_click=connectChroma)

if "chroma_collections" in st.session_state:
    selected_collection_placeholder = st.empty()
    st.session_state["selected_collection"] = selected_collection_placeholder.selectbox(
            label="Chroma collections",
            options=st.session_state["chroma_collections"]
        )

    if "selected_collection" in st.session_state:
        if st.session_state["selected_collection"]:
            df = st.session_state["conn"].get_collection_data(collection_name=st.session_state["selected_collection"])
            st.subheader("Embedding data")
            st.markdown("Dataframe:")

            dataframe_placeholder = st.empty()
            dataframe_placeholder.data_editor(df)


if "is_connected" in st.session_state and st.session_state["is_connected"]:
    with st.container():
        new_collection_name = st.sidebar.text_input(label='New collection name', placeholder='')
        new_collection_embedding = st.sidebar.selectbox(label='Embedding function',
                                                        options=["OpenAIEmbedding", "VertexEmbedding"])

        config = {}
        config["api_key"] = st.sidebar.text_input(label='API KEY', placeholder='')

        if new_collection_embedding == "VertexEmbedding":
            config["project_id"] = st.sidebar.text_input(label='PROJECT ID', placeholder='')
            config["model_name"] = st.sidebar.text_input(label='MODEL_NAME', placeholder='textembedding-gecko-001')

        if new_collection_embedding == "OpenAIEmbedding":
            config["model_name"] = st.sidebar.text_input(label='MODEL_NAME', placeholder='text-embedding-ada-002')


        if st.sidebar.button("Create"):

            try:
                st.session_state["conn"].create_collection(collection_name=new_collection_name,
                                                        embedding_function_name=new_collection_embedding,
                                                        config=config)
                st.toast(body='New collection created!',
                             icon='✅')

                st.session_state["chroma_collections"] = st.session_state["conn"].get_collection_names()
                selected_collection_placeholder.empty()
                st.session_state["selected_collection"] = selected_collection_placeholder.selectbox(
                    label="Chroma collections",
                    options=st.session_state["chroma_collections"],
                    key="new_select_box"
                )
            except Exception as ex:
                st.toast(body=f"{str(ex)}",
                    icon="⚠️")
                st.toast(body="Failed to create new connection",
                    icon="😢")

