"""Load html from files, clean up, split, ingest into Weaviate."""
import os
import datetime
import requests
from langchain.document_loaders import ReadTheDocsLoader
from langchain.document_loaders.pdf import PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
import logging
from chromaclient import client

def fetch_all_reports(
    base_url = "https://www.federalreserve.gov/mediacenter/files/FOMCpresconf",
    date_format = "%Y%m%d"):
  
    last_working_date = datetime.date.today()
    current_date = datetime.date.today()
    limit = datetime.timedelta(days=90) # three months
    reports = [] # list to store the report urls

    # check if the collection exists in the local machine
    try:
        client.get_collection(base_url.split("/")[-1].lower())
    except:
        logging.info("The reports db doesn't exists in the local machine, creating it now")
        # loop through the dates in the past three months
        while last_working_date - current_date <= limit:
            date_str = current_date.strftime(date_format)
            pdf_url = base_url + date_str + ".pdf"
            response = requests.get(pdf_url)
            status_code = response.status_code
            if status_code == 200: # the pdf exists
                logging.info("The report for {} is accessible through this link: {}".format(date_str, pdf_url))
                ingest(pdf_url, date_str)
                last_working_date = current_date # update the last working date
                current_date -= datetime.timedelta(days=1) # go to previous day
            elif status_code == 404: # the pdf does not exist
                logging.info("The report for {} does not exist".format(date_str))
                current_date -= datetime.timedelta(days=1) # go to previous day
            else: # unexpected status code for the pdf
                logging.info("The link for {} returned an unexpected status code: {}".format(date_str, status_code))
                break # stop the loop

    if not reports: # no reports were found in the past three months
        logging.info("No reports were found in the past three months")
    else: # some reports were found in the past three months
        logging.info("The following reports were found in the past three months: {}".format(reports))


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
            ingest(url, date_str)
        elif status_code == 404:
            today -= datetime.timedelta(days=1) # go to previous day
        else:
            logging.info("The link returned an unexpected status code: {}".format(status_code))
            break # stop the loop

    if not found:
        logging.info("No link was found in the past three months")


def ingest(report, date, namespace="fomcpresconf"):
    
    loader = PyPDFLoader(report)
    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = text_splitter.split_documents(raw_documents)
    for chunk in chunks:
        chunk.metadata["source"] = report
        chunk.metadata["date"] = date

    embeddings = OpenAIEmbeddings()
    collection = client.get_or_create_collection(name=namespace, embedding_function=embeddings)
    
    vectorstore = Chroma.from_documents(
            chunks, embeddings, collection_name=namespace, client=client, persist_directory="db")
    
    vectorstore.persist()


if __name__ == "__main__":
    ingest()