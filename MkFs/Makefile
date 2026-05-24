ENV_DIR=../YMLs
ENV_NAME=invColors
ROOT_DIR=$(shell git rev-parse --show-toplevel)
MAMBA=micromamba

PROJECT_DIR := ..

TARGET ?= $(PWD)

.PHONY: create run update delete shell

create:
	@echo "🚀 Creating env $(ENV_NAME)..."
	$(MAMBA) env create -f $(ENV_DIR)/$(ENV_NAME).yml -y

	$(MAMBA) run -n $(ENV_NAME) \
		python -m ipykernel install --user \
		--name $(ENV_NAME) \
		--display-name "Python ($(ENV_NAME))"

build: clean
	cd $(ROOT_DIR) && $(MAMBA) run -n $(ENV_NAME) python -m build

check:
	cd $(ROOT_DIR) && $(MAMBA) run -n $(ENV_NAME) python -m twine check dist/*

upload:
	cd $(ROOT_DIR) && $(MAMBA) run -n $(ENV_NAME) python -m twine upload dist/*

run:
	@echo "🌙 Inverting PDFs in:"
	@echo "📂 $(TARGET)"

	$(MAMBA) run -n $(ENV_NAME) \
		python $(PROJECT_DIR)/invColors.py "$(TARGET)" $(ARGS)

shell:
	@echo "🏃 Entering 2env $(ENV_NAME)..."
	$(MAMBA) run -n $(ENV_NAME) bash

update:
	@echo "🔄 Updating env..."
	$(MAMBA) env update -n $(ENV_NAME) \
		-f $(ENV_DIR)/$(ENV_NAME).yml -y

release: build check upload

delete:
	@echo "🧹 Rm env..."
	$(MAMBA) env remove -n $(ENV_NAME) -y