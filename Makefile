.PHONY: binder-open help

# Binder URL for this repository
BINDER_URL := https://mybinder.org/v2/gh/adamisom/jupyterlab-research-assistant-wwc-copilot/HEAD

# Detect OS and use appropriate command to open URL
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	OPEN_CMD := xdg-open
endif
ifeq ($(UNAME_S),Darwin)
	OPEN_CMD := open
endif
ifeq ($(UNAME_S),Windows_NT)
	OPEN_CMD := start
endif

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

binder-open: ## Open Binder URL in default browser
	@echo "Opening Binder URL: $(BINDER_URL)"
	@$(OPEN_CMD) $(BINDER_URL) || echo "Error: Could not open browser. Please visit $(BINDER_URL) manually"

