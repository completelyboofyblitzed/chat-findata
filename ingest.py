"""Load html from files, clean up, split, ingest into Weaviate."""
import pickle
import datetime
import requests
from langchain.document_loaders import ReadTheDocsLoader
from langchain.document_loaders.pdf import PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
import logging


def fetch_latest_report(
    base_url = "https://www.federalreserve.gov/mediacenter/files/FOMCpresconf",
    date_format = "%Y%m%d"):
  
    today = datetime.date.today()
    limit = today - datetime.timedelta(days=90) # three months ago
    found = False

    while not found and today >= limit:
        date_str = today.strftime(date_format)
        url = base_url + date_str + ".pdf"
        response = requests.get(url)
        status_code = response.status_code
        if status_code == 200:
            logging.info("The latest report is accessible through this link: {}".format(url))
            return url
        elif status_code == 404:
            today -= datetime.timedelta(days=1) # go to previous day
        else:
            logging.info("The link returned an unexpected status code: {}".format(status_code))
            break # stop the loop

    if not found:
        logging.info("No link was found in the past three months")


def ingest_docs(pdf_path="https://www.federalreserve.gov/mediacenter/files/FOMCpresconf20230322.pdf"):
    """Get documents from web pages."""
    # loader = ReadTheDocsLoader("langchain.readthedocs.io/en/latest/")
    loader = PyPDFLoader(pdf_path)
    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    documents = text_splitter.split_documents(raw_documents)
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)

    # Save vectorstore
    report_name = pdf_path.split("/")[-1]

    with open(f"{report_name}.pkl", "wb") as f:
        pickle.dump(vectorstore, f)


if __name__ == "__main__":
    ingest_docs()