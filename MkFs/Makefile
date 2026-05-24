ENV_DIR=../YMLs
ENV_NAME=invColors

ROOT_DIR=$(shell git rev-parse --show-toplevel)
PROJECT_DIR=$(ROOT_DIR)

MAMBA=micromamba

TARGET ?= $(PWD)
ARGS ?=

.PHONY: create build check upload release run shell update clean delete

create:
	@echo "🚀 Creating env $(ENV_NAME)..."

	$(MAMBA) env create \
		-f $(ENV_DIR)/$(ENV_NAME).yml \
		-n $(ENV_NAME) \
		-y

	@echo "📓 Installing Jupyter kernel..."

	$(MAMBA) run -n $(ENV_NAME) \
		python -m ipykernel install --user \
		--name $(ENV_NAME) \
		--display-name "Python ($(ENV_NAME))"

build: clean
	@echo "📦 Building package..."

	cd $(ROOT_DIR) && \
	$(MAMBA) run -n $(ENV_NAME) \
		python -m build

check:
	@echo "🔍 Checking package..."

	cd $(ROOT_DIR) && \
	$(MAMBA) run -n $(ENV_NAME) \
		twine check dist/*

upload:
	@echo "🚀 Uploading to PyPI..."

	cd $(ROOT_DIR) && \
	$(MAMBA) run -n $(ENV_NAME) \
		twine upload dist/*

release: build check upload

run:
	@echo "🌙 Inverting PDFs in:"
	@echo "📂 $(TARGET)"

	cd $(ROOT_DIR) && \
	$(MAMBA) run -n $(ENV_NAME) \
		python $(PROJECT_DIR)/invColors.py "$(TARGET)" $(ARGS)

shell:
	@echo "🏃 Entering env $(ENV_NAME)..."

	$(MAMBA) run -n $(ENV_NAME) bash

update:
	@echo "🔄 Updating env..."

	$(MAMBA) env update \
		-n $(ENV_NAME) \
		-f $(ENV_DIR)/$(ENV_NAME).yml \
		-y

clean:
	@echo "🧹 Cleaning build artifacts..."

	cd $(ROOT_DIR) && \
	rm -rf dist build *.egg-info

delete:
	@echo "🗑 Removing env $(ENV_NAME)..."

	$(MAMBA) env remove \
		-n $(ENV_NAME) \
		-y