import os
from langchain.llms import OpenAI
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
import streamlit as st

# Ingresa la key de openai
os.environ['OPENAI_API_KEY'] = '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'
# da un nombre predeterminado al pdf que se subira
default_doc_name = 'doc.html'

# la funcion process_doc procesa el documento, recupera informacion y responde preguntas
# ponemos True porque el archivo esta integrado localmente
def process_doc(
        path: str = 'Documento-de-examen-Grupo1.html',
        is_local: bool = True,
        question: str = 'Cuál es la fecha de la ultima versión entregada?'
):
    # descarga el pdf y luego pypdf carga el documento y lo divide en fragmentos de texto

    _, loader = os.system(f'curl -o {default_doc_name} {path}'), UnstructuredHTMLLoader(f"./{default_doc_name}") if is_local \
        else UnstructuredHTMLLoader(path)

    # luego de cargar el documento lo que hace es dividirlo gracias a load_and_split()
    doc = loader.load_and_split()

    print(doc[-1])

    # USA chroma para realizar un almacenamiento de vectores
    # utiliza inscrustaciones de openai para representar fragmentos de texto del html brindado
    db = Chroma.from_documents(doc, embedding=OpenAIEmbeddings())

    # con RetrievalQA ya hacemos llamado al llm de OpenAI y se crea el modelo para que recupere las preguntas
    qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type='stuff', retriever=db.as_retriever())

    # utiliza streamlit para mostrar la respuesta de la pregunta
    st.write(qa.run(question))

    # con RetrievalQA ya hacemos llamado al llm de OpenAI y se crea el modelo para que recupere las preguntas
    qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type='stuff', retriever=db.as_retriever())

    # utiliza streamlit para mostrar la respuesta de la pregunta
    st.write(qa.run(question))


# aqui ya define al cliente y la interfaz de usuario de streamlit para cargar el html
# ingresa preguntas y obtiene respuestas
def client():
    st.title('Examen usando UnstructuredHTMLLoader ')
    uploader = st.file_uploader('Upload HTML', type='html')

    if uploader:
        with open(f'./{default_doc_name}', 'wb') as f:
            f.write(uploader.getbuffer())
        st.success('HTML saved!!')

    question = st.text_input('Genera un pequeño resumen de las primeras 5 paginas',
                             placeholder='Give response about your HTML', disabled=not uploader)

    if st.button('Send Question'):
        if uploader:
            process_doc(
                path=default_doc_name,
                is_local=True,
                question=question
            )
        else:
            st.info('Loading default HTML')
            process_doc()


# esto ejecuta la funcion cliente.
if __name__ == '__main__':
    client()
