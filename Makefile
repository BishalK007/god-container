DEVCONTAINER_MK := .devcontainer/devcontainer.mk

.PHONY: conf-container

conf-container:
	@$(MAKE) -f $(DEVCONTAINER_MK) conf-container

.PHONY: conn

conn:
	@$(MAKE) -f $(DEVCONTAINER_MK) conn