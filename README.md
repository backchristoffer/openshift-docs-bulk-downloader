# openshift-docs--bulk-downloader
script to download all docs from selected openshift 4.y version in PDF .
useful if you intend to load ocp docs into your LLM in bulk

# Container Build Command

### Build Using Podman
podman build -t openshift-docs .

### Build Using Docker
docker build -t openshift-docs .

# OpenShift Downloader Examples

### Example 1: Full Automation
podman run -it --rm -v ./:/app:Z openshift-docs --version 4.20 --scrape --verify --download --cleanup

### Example 2: Scrape and Verify Only
podman run -it --rm -v ./:/app:Z openshift-docs --version 4.19 --scrape --verify

### Example 3: Download from Cache
podman run -it --rm -v ./:/app:Z openshift-docs --version 4.18 --download

### Example 4: Target Specific Version
podman run -it --rm -v ./:/app:Z openshift-docs --version 4.17 --scrape --verify --download

# Python Pipenv Examples

### Example 1: Full Automation
pipenv run python app.py --version 4.20 --scrape --verify --download --cleanup

### Example 2: Scrape and Verify Only
pipenv run python app.py --version 4.19 --scrape --verify

### Example 3: Download from Cache
pipenv run python app.py --version 4.18 --download

### Example 4: Target Specific Version
pipenv run python app.py --version 4.17 --scrape --verify --download

# OpenShift Downloader CLI Arguments

| Argument | Description |
| :--- | :--- |
| `--version` | Specify the OpenShift version (e.g., 4.18, 4.20). |
| `--scrape` | Scrapes the landing page and creates a `toc_VERSION.json` cache. |
| `--verify` | Performs a HEAD request for every PDF to ensure it exists on the server. |
| `--download` | Downloads the PDFs from the cache into versioned subdirectories. |
| `--cleanup` | Deletes the JSON cache file upon successful completion. |
