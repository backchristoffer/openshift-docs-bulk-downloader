# openshift-docs-downloader
script to download all docs from selected openshift 4.y version in PDF

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
