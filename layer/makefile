build-PythonExtensionLayer:
	cp -r extensions $(ARTIFACTS_DIR)
	cp -r python-extension $(ARTIFACTS_DIR)
	python3 -m pip install -r python-extension/requirements.txt -t $(ARTIFACTS_DIR)/python-extension
	chmod +x $(ARTIFACTS_DIR)/python-extension/extension.py $(ARTIFACTS_DIR)/extensions/python-extension
