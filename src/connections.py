import os
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
from pymongo import MongoClient

load_dotenv()


def get_secret(key: str, default=None):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


@st.cache_resource
def pg_engine():
    return create_engine(get_secret("POSTGRES_URL"), pool_pre_ping=True)


@st.cache_resource
def mongo_db():
    client = MongoClient(get_secret("MONGO_URI"), serverSelectionTimeoutMS=8000)
    return client[get_secret("MONGO_DB_NAME", "pangan_jabar")]
