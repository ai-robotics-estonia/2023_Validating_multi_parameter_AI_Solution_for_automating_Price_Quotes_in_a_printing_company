"""Configuration loading from a local .env file.

The repository never ships real credentials. Copy `.env.example` to `.env`
and fill in your own values before running anything.
"""
from dotenv import dotenv_values


def load_env() -> dict:
    return dotenv_values()
