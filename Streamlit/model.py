import streamlit as st
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import CTransformers
from langchain.chains import RetrievalQA

DB_FAISS_PATH = 'vectorstores/db_faiss'

custom_prompt_template = """Use the following pieces of information to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context: {context}
Question: {question}

Only return the helpful answer below and nothing else.
Helpful answer:
"""

def set_custom_prompt():
    prompt = PromptTemplate(template=custom_prompt_template,
                            input_variables=['context', 'question'])
    return prompt

def retrieval_qa_chain(llm, prompt, db):
    qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                           chain_type='stuff',
                                           retriever=db.as_retriever(search_kwargs={'k': 2}),
                                           return_source_documents=True,
                                           chain_type_kwargs={'prompt': prompt}
                                           )
    return qa_chain

def load_llm():
    llm = CTransformers(
        model="TheBloke/Llama-2-7B-Chat-GGML",
        model_type="llama",
        max_new_tokens=512,
        temperature=0.5
    )
    return llm

def qa_bot(query):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                       model_kwargs={'device': 'cpu'})
    db = FAISS.load_local(DB_FAISS_PATH, embeddings)
    llm = load_llm()
    qa_prompt = set_custom_prompt()
    qa = retrieval_qa_chain(llm, qa_prompt, db)

    # Implement the question-answering logic here
    response = qa({'query': query})
    return response['result']

def add_vertical_space(spaces=1):
    for _ in range(spaces):
        st.markdown("---") 

def main():
    st.set_page_config(page_title="Llama-2-GGML Medical Chatbot")

    with st.sidebar:
        st.title('Llama-2-GGML Medical Chatbot! 🚀🤖')
        st.markdown('''
        ## About
                    
        The Llama-2-GGML Medical Chatbot uses the **Llama-2-7B-Chat-GGML** model and was trained on medical data from **"The GALE ENCYCLOPEDIA of MEDICINE"**.
                    
        ### 🔄Bot evolving, stay tuned!
        ## Useful Links 🔗

        - **Model:** [Llama-2-7B-Chat-GGML](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML) 📚
        - **GitHub:** [ThisIs-Developer/Llama-2-GGML-Medical-Chatbot](https://github.com/ThisIs-Developer/Llama-2-GGML-Medical-Chatbot) 💬
        ''')
        add_vertical_space(1)  # Adjust the number of spaces as needed
        st.write('Made by [@ThisIs-Developer](https://huggingface.co/ThisIs-Developer)')

    st.title("Llama-2-GGML Medical Chatbot")
    st.markdown(
        """
        <style>
            .chat-container {
                display: flex;
                flex-direction: column;
                height: 400px;
                overflow-y: auto;
                padding: 10px;
                color: white; /* Font color */
            }
            .user-bubble {
                background-color: #007bff; /* Blue color for user */
                align-self: flex-end;
                border-radius: 10px;
                padding: 8px;
                margin: 5px;
                max-width: 70%;
                word-wrap: break-word;
            }
            .bot-bubble {
                background-color: #363636; /* Slightly lighter background color */
                align-self: flex-start;
                border-radius: 10px;
                padding: 8px;
                margin: 5px;
                max-width: 70%;
                word-wrap: break-word;
            }
        </style>
        """
    , unsafe_allow_html=True)

    conversation = st.session_state.get("conversation", [])
    
    query = st.text_input("Ask your question here:", key="user_input")
    if st.button("Get Answer"):
        if query:
            with st.spinner("Processing your question..."):  # Display the processing message
                conversation.append({"role": "user", "message": query})
                # Call your QA function
                answer = qa_bot(query)
                conversation.append({"role": "bot", "message": answer})
                st.session_state.conversation = conversation
        else:
            st.warning("Please input a question.")

    chat_container = st.empty()
    chat_bubbles = ''.join([f'<div class="{c["role"]}-bubble">{c["message"]}</div>' for c in conversation])
    chat_container.markdown(f'<div class="chat-container">{chat_bubbles}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
