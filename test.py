import os
import asyncio

from PyPDF2 import PdfReader

from fastapi import APIRouter
from pydantic import BaseModel
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI

from dotenv import load_dotenv, find_dotenv

from prompts import product_prompt_template,final_product_prompt_template

_ = load_dotenv(find_dotenv())

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def extract_text_from_pdf(pdf):
    pdf_reader = PdfReader(pdf)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    return text


def split_into_chunks(text: str) -> list[str]:
    """Splits text into chunks

    Args:
        text (_type_): _extracted text_

    Returns:
        _type_: _description_
    """
    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=7000, chunk_overlap=700, length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def analyze_document(document: str) -> dict:
    if document.endswith(".pdf"):
        try:
            extracted_text = extract_text_from_pdf(document)
            chunks = split_into_chunks(extracted_text)
            
            insights = []
            for chunk in chunks:
                transcript = product_prompt_template.format_messages(text=chunk)
                chat = ChatOpenAI(temperature=0.0,model="gpt-4")

                insight = chat(transcript)
                insights.append(insight)

            summary = final_product_prompt_template.format_messages(text=insights)
            chat = ChatOpenAI(temperature=0.0,model="gpt-4")
            final_insights = chat(summary)
            return final_insights

        except Exception as e:
            print("Error: ", e)
    elif document.endswith(".txt"):
        return "This is a text file."
    else:
        return "Error: This is not a PDF or text file."



def main():
    # Assume 'document.pdf' is the path to a PDF file
    document = '/Users/Zachary_Royals/Code/zelta-challenge/Sample Transcript_pdf.pdf'
    results = analyze_document(document)
    print(results)

# Run the event loop
main()