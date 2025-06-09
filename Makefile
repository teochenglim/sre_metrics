.DEFAULT_GOAL := help

.PHONY: help install test test-fastapi test-flask run-examples

## -------------------------------------------------------------------
## 📖 Usage summary
## -------------------------------------------------------------------
help: ## Show this help message
	@echo "\nUsage: make [target]\n"
	@awk 'BEGIN { FS = ":[ ]*##[ ]*" } \
	       /^[a-zA-Z_-]+:.*##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo

## -------------------------------------------------------------------
## ⚙️  Setup & Testing
## -------------------------------------------------------------------
install: ## Install package with FastAPI & Flask extras
	pip install -e .[fastapi,flask]

test: test-fastapi test-flask ## Run both FastAPI + Flask tests

test-fastapi: ## Run FastAPI tests
	pytest tests/test_fastapi.py -v

test-flask: ## Run Flask tests
	pytest tests/test_flask.py -v

## -------------------------------------------------------------------
## 🚀 Examples
## -------------------------------------------------------------------
run-fastapi-examples: ## Launch both FastAPI & Flask example apps (in background)
	cd examples && python fastapi_app.py

run-flask-examples: ## Launch both FastAPI & Flask example apps (in background)
	cd examples && python flask_app.py