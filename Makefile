# Makefile for 01-rag-document-intelligence
#
# This file provides shortcut commands for common project operations.
#
# Usage examples:
#   make install
#   make app
#   make test
#   make clean

.PHONY: help install app test clean clean-data clean-vector clean-cache notebooks

help:
	@echo "Available commands:"
	@echo "  make install       Install Python dependencies"
	@echo "  make app           Run the Streamlit app"
	@echo "  make test          Run pytest"
	@echo "  make notebooks     Start Jupyter Notebook"
	@echo "  make clean         Remove cache, vector store and generated data"
	@echo "  make clean-data    Remove generated interim and processed data"
	@echo "  make clean-vector  Remove ChromaDB vector store"
	@echo "  make clean-cache   Remove Python and notebook cache files"

install:
	pip install -r requirements.txt

app:
	streamlit run app/streamlit_app.py

test:
	pytest

notebooks:
	jupyter notebook

clean: clean-cache clean-vector clean-data
	@echo "Project cleanup completed."

clean-data:
	rm -rf data/interim/*
	rm -rf data/processed/*
	@echo "Generated data removed from data/interim and data/processed."

clean-vector:
	rm -rf chroma_db
	rm -rf vector_store
	@echo "Vector stores removed."

clean-cache:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cache files removed."
