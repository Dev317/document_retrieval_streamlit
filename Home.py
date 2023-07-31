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


st.set_page_config(
    page_title='ChromaDBConnection',
    page_icon='https://docs.trychroma.com/img/chroma.png'
)

st.title("📂 ChromaDBConnection")

"""
Connection for Chroma vector database, `ChromaDBConnection`, has been released which makes it easy to connect any Streamlit LLM-powered app to.

With `st.experimental_connection()`, connecting to a Chroma vector database becomes just a few lines of code:
"""

st.code("""
import streamlit as st

configuration = {
    "client_type": "PersistentClient",
    "path": "/tmp/.chroma"
}

collection_name = "documents_collection"

conn = st.experimental_connection("chromadb",
                                type=ChromaDBConnection,
                                **configuration)
documents_collection_df = conn.get_collection_data(collection_name)
st.dataframe(documents_collection_df)
    """,
    language='python'
)


"""
***
### ChromaDBConnection API

#### _connect()
There are 2 ways to connect to a Chroma client:
1. **PersistentClient**: Data will be persisted to a local machine
    ```python
    configuration = {
        "client_type": "PersistentClient",
        "path": "/tmp/.chroma"
    }

    conn = st.experimental_connection("chromadb",
                                    type=ChromaDBConnection,
                                    **configuration)
    ```

2. **HttpClient**: Data will be persisted to a cloud server where Chroma resides
    ```python
    configuration = {
        "client_type": "HttpClient",
        "host": "localhost",
        "port": 8000,
        "ssl": False
    }

    conn = st.experimental_connection("chromadb",
                                    type=ChromaDBConnection,
                                    **configuration)
    ```


#### create_collection()
In order to create a Chroma collection, one needs to supply a `collection_name` and `embedding_function_name`.
There are current possible options for `embedding_function_name`:
- DefaultEmbedding
- VertexEmbedding
- OpenAIEmbedding
```python
collection_name = "documents_collection"
embedding_function_name = "DefaultEmbedding"
conn.create_collection(collection_name=collection_name,
                       embedding_function_name=embedding_function_name)
```

#### get_collection_data()
This method returns a dataframe that consists of the embeddings and documents of a collection.

```python
collection_name = "documents_collection"
conn.get_collection_data(collection_name=collection_name)
```

#### delete_collection()
This method deletes the stated collection name.

```python
collection_name = "documents_collection"
conn.delete_collection(collection_name=collection_name)
```

#### upload_document()
This method utilises Langchain DocumentLoader to split uploaded files into text chunks. After which, the text chunks are converted to embeddings and stored into vector collection.

```python
upload_directory = "/tmp/upload"
collection_name = "documents_collection"

file_uploads = st.file_uploader('Only PDF(s)', type=['pdf'], accept_multiple_files=True)
file_paths = []

if file_uploads:
    for pdf_file in file_uploads:
        file_path = os.path.join(upload_directory, pdf_file.name)
        file_paths.append(file_path)

        with open(file_path,"wb") as f:
            f.write(pdf_file.getbuffer())


conn.upload_document(directory=upload_directory, collection_name=collection_name, file_paths=file_paths)
```

#### retrieve()
This method retrieves top 10 relevant document based on a prompt query!


```python
    query = "{random key words}"
    collection_name = "documents_collection"
    query_df = conn.retrieve(collection_name=collection_name, query=query)
    query_dataframe_placeholder.dataframe(query_df)
```

:tada: :tada: That's it! ChromaDBConnection is ready to be used with `st.experimental_connection()`.

***

"""
