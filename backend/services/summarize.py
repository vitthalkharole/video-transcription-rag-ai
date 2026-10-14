from langchain_mistralai import ChatMistralAI
from langchain_groq import ChatGroq
from backend.core.config import settings
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough , RunnableLambda
import os


def get_llm():
    return ChatGroq(
        model = "qwen/qwen3.8-27b",
        api_key = settings.GROQ_API_KEY,
        temperature = 0.3,
        max_tokens=250)


def split_transcript(transcript:str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 200

    )

    return splitter.split_text(transcript)



def summarize(transcript: str):
    llm = get_llm()

    # Step 1: Summarize each transcript chunk
    map_prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize this portion of a transcript concisely."),
        ("human", "{text}")
    ])

    map_chain = map_prompt | llm | StrOutputParser()

    chunks = split_transcript(transcript)

    chunk_summaries = [
        map_chain.invoke({"text": chunk})
        for chunk in chunks
    ]

    # Step 2: Combine partial summaries
    combined = "\n\n".join(chunk_summaries)

    combined_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert meeting summarizer. Combine these partial "
            "summaries into one final, professional meeting summary "
            "in bullet points."
        ),
        ("human", "{text}")
    ])

    combined_chain = (
        combined_prompt
        | llm
        | StrOutputParser()
    )

    return combined_chain.invoke({"text": combined})


def generate_title(transcript : str):
    llm = get_llm()

    title_chain = (
        RunnablePassthrough() | RunnableLambda(lambda x : {"text":x})|
        ChatPromptTemplate.from_messages([
            (
            "system",
            "based on the meeting transcript, generate a short professional meeting title"
            "(max 8 words) that captures the essence of the title , nothing else."

        ),
        ("human","{text}"),]
    )|llm |StrOutputParser()
    )

    return title_chain.invoke(transcript[:2000])


