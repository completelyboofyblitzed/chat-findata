# 💼 ChatFinData

This repo is aimed to be an implementation of a locally hosted chatbot specifically focused on question answering over the financial data.
Built with [LangChain](https://github.com/hwchase17/langchain/) and [FastAPI](https://fastapi.tiangolo.com/).

## ✅ Running locally
1. Install dependencies: `pip install -r requirements.txt`
1. Run the app: `make start`
   1. To enable tracing, make sure `langchain-server` is running locally and pass `tracing=True` to `get_chain` in `main.py`. You can find more documentation [here](https://langchain.readthedocs.io/en/latest/tracing.html).
1. Open [localhost:9000](http://localhost:9000) in your browser.

## 📚 Technical description

There are two components: ingestion and question-answering.

Ingestion has the following steps:

1. Pull pdf from [Federal Reserve](https://www.federalreserve.gov/)
2. Load pdf with LangChain's [PyPDFLoader Loader](https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/pdf.html)
3. Split documents with LangChain's [TextSplitter](https://langchain.readthedocs.io/en/latest/reference/modules/text_splitter.html)
4. Create a vectorstore of embeddings, using LangChain's [vectorstore wrapper](https://python.langchain.com/en/latest/modules/indexes/vectorstores.html) (with OpenAI's embeddings and FAISS vectorstore).

Question-Answering has the following steps, all handled by [ChatVectorDBChain](https://langchain.readthedocs.io/en/latest/modules/indexes/chain_examples/chat_vector_db.html):

1. Given the chat history and new user input, determine what a standalone question would be (using GPT-3).
2. Given that standalone question, look up relevant documents from the vectorstore.
3. Pass the standalone question and relevant documents to GPT-3 to generate a final answer.

## 🚀 Roadmap

- [x] Implement LangChain + GPT-3.5 for Federal Speeches application
- [ ] Unstructured file access based on langchain
   - [ ].md ?
   - [x].pdf
   - [ ].docx ?
   - [ ].txt ?
- [ ] Add support for other LLM models
- [ ] Implement analysis in time
   - [ ] analize data structured in time 
   - [ ] show graphs 
   - [ ] allign with graphs