"""
title: Llama Index DB Pipeline
author: 0xThresh, Code GPT
date: 2024-08-11
version: 1.1
license: MIT
description: A pipeline for using text-to-SQL for retrieving relevant information from a database using the Llama Index library.
requirements: llama_index, sqlalchemy, psycopg2-binary
"""

import os
from typing import List, Union, Generator, Iterator

from llama_index.core import SQLDatabase, PromptTemplate
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.llms.ollama import Ollama
from pydantic import BaseModel
from sqlalchemy import create_engine


class Pipeline:
    """Primary pipeline class for Open WebUI."""

    # Metadata required for Open WebUI
    name = "Llama Index DB Pipeline"
    version = "1.1"
    description = "Pipeline for text-to-SQL queries using Llama Index."

    class Valves(BaseModel):
        # Connect this filter to all pipelines
        pipelines: List[str] = ["*"]
        # Add any custom parameters/configuration here
        DB_HOST: str = os.getenv("DB_HOST", "host.docker.internal")
        DB_PORT: str = os.getenv("DB_PORT", "5432")
        DB_USER: str = os.getenv("DB_USER", "DB_USER")
        DB_PASSWORD: str = os.getenv("DB_PASSWORD", "DB_PASSWORD")
        DB_DATABASE: str = os.getenv("DB_DATABASE", "postgres")
        DB_TABLE: str = os.getenv("DB_TABLE", "DB_TABLE")
        OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
        TEXT_TO_SQL_MODEL: str = os.getenv("TEXT_TO_SQL_MODEL", "llama3.1:latest")

    def __init__(self):
        self.name = "Database RAG Pipeline"
        self.engine = None
        self.valves = self.Valves()

    def init_db_connection(self):
        """Initialize the database connection using SQLAlchemy."""
        self.engine = create_engine(f"postgresql+psycopg2://{self.valves.DB_USER}:{self.valves.DB_PASSWORD}"
                                    f"@{self.valves.DB_HOST}:{self.valves.DB_PORT}/{self.valves.DB_DATABASE}")
        return self.engine

    async def on_startup(self):
        """Handle pipeline startup events."""
        try:
            print(f"on_startup: {__name__}")
            self.init_db_connection()
            print("Database connection initialized successfully.")
        except Exception as e:
            print(f"Error during startup: {e}")

    async def on_shutdown(self):
        """Handle pipeline shutdown events."""
        print(f"on_shutdown: {__name__}")

    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict) -> Union[
        str, Generator, Iterator]:
        """Main pipeline processing method."""
        try:
            print("pipe method triggered with:", user_message)
            sql_database = SQLDatabase(self.engine, include_tables=[self.valves.DB_TABLE])
            llm = Ollama(model=self.valves.TEXT_TO_SQL_MODEL, base_url=self.valves.OLLAMA_HOST, request_timeout=180.0,
                         context_window=30000)

            # Set up the custom prompt used when generating SQL queries from text
            text_to_sql_prompt = """
            Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer. 
            You can order the results by a relevant column to return the most interesting examples in the database.
            Unless the user specifies in the question a specific number of examples to obtain, query for at most 5 results using the LIMIT clause as per Postgres. You can order the results to return the most informative data in the database.
            Never query for all the columns from a specific table, only ask for a few relevant columns given the question.
            You should use DISTINCT statements and avoid returning duplicates wherever possible.
            Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Pay attention to which column is in which table. Also, qualify column names with the table name when needed. You are required to use the following format, each taking one line:

            Question: Question here
            SQLQuery: SQL Query to run
            SQLResult: Result of the SQLQuery
            Answer: Final answer here

            Only use tables listed below.
            {schema}

            Question: {query_str}
            SQLQuery: 
            """

            text_to_sql_template = PromptTemplate(text_to_sql_prompt)
            query_engine = NLSQLTableQueryEngine(sql_database=sql_database, tables=[self.valves.DB_TABLE], llm=llm,
                                                 text_to_sql_prompt=text_to_sql_template, streaming=True)

            m_response = query_engine.query(user_message)
            return m_response.response_gen

        except Exception as e:
            print(f"Error in pipe method: {e}")
            return f"Error: {e}"

# try:
#     pipeline = Pipeline()
#     pipeline.init_db_connection()  # Initialize DB connection
#     response = pipeline.pipe("how many employees are in the employees database?", "model_id", [], {})
#     for res in response:
#         print(res)
# except Exception as e:
#     print(f"Pipeline execution failed: {e}")
