#!/usr/bin/env python3
"""
Script to create database tables in Neon Serverless PostgreSQL.
This script connects to the database using the configured DATABASE_URL and creates all required tables.
"""

import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine
from src.models.user import User
from src.models.task import Task

def main():
    # Load environment variables
    load_dotenv()

    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL environment variable not set.")
        print("Please set the DATABASE_URL in your .env file.")
        print("For Neon, it should look like: postgresql://username:password@ep-xxxxxx.us-east-1.aws.neon.tech/dbname")
        return

    print(f"Connecting to database: {database_url}")

    # Create the engine
    engine = create_engine(database_url, echo=True)

    # Create all tables
    print("Creating tables...")
    SQLModel.metadata.create_all(bind=engine)
    print("Tables created successfully!")

    # Verify tables were created by reflecting the schema
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print(f"\nTables in database: {tables}")

    if 'user' in tables and 'task' in tables:
        print("\nSUCCESS: User and Task tables created successfully!")
        print("SUCCESS: Database initialization completed successfully!")
    else:
        print("\nERROR: Some tables may not have been created properly.")

if __name__ == "__main__":
    main()