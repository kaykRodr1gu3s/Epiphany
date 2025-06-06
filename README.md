# Epiphany

**Epiphany** is a Python-based tool that collects alerts from SIEM platforms, enriches and processes them, and creates corresponding cases in TheHive to support incident response workflows.


[![Splunk](https://img.shields.io/badge/SIEM-Splunk-green.svg)](https://www.splunk.com/)
[![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

## Table of Contents
+ [Overview](#overview)
+ [main features](#main-features)
+ [Prerequisites](#prerequisites)
+ [Flow process](#flow-process)
+ [Setup Instructions](#setup-instructions)
+ [Installations guide](#installations-guide)
+ [Command-Line Usage](#command-line-usage)
+ [uture Improvements](#future-improvements)
+ [Contribution](#contribution)

-------  

### Overview

Epiphany is an automation framework built with Python that collects alerts from multiple SIEM platforms and centralizes them in Elasticsearch for analysis and correlation. It ensures data integrity by verifying and filtering out already-processed alerts to avoid redundant uploads. Once verification is complete, any new alerts not present in TheHive are automatically pushed for case creation and investigation — streamlining the incident response process

### main features

+ Remote Suricata Execution - 
+ Data Collection Pipeline
+ Integration with Splunk
+ Elasticsearch Enrichment
+ Efficient Alert Filtering
+ TheHive Case Management
+ Redundancy Prevention

### Prerequisites

  + python
  + Linux server
  + Splunk
  + elasticsearch
  + TheHive  

### Flow process

+ 1 - Connect to Remote Server
  + Establish SSH connection to the Linux server.

+ 2 - Run Suricata with PCAP
  + Execute Suricata on a .pcap file to generate eve.json logs.

+ 3 - Download Log File
  + Transfer eve.json from the server to local machine.

+ 4 - Upload to Splunk
  + Index the eve.json into Splunk.
 
+ 5 - Collect Data from Splunk
  + Retrieve the indexed alerts from Splunk via splunk-sdk.

+ 6 - Enrich & Upload to Elasticsearch
  + Add a verified: false field to each alert.
  + Upload the enriched data into Elasticsearch.

+ 7 - Query Unverified Alerts
  + Use a KQL query to filter only alerts that are:
    + Not verified.
    + Not previously uploaded to TheHive.

+ 8 - Upload to TheHive
  + Create alerts in TheHive from the filtered Elasticsearch data.

+ 9 - Update Verification Status
  + Mark successfully uploaded alerts as verified: true in Elasticsearch.
  

### Setup Instructions

   To get started, clone the repository:

  ```
  git clone git@github.com:kaykRodr1gu3s/Epiphany.git
  ```

  Then, navigate to the Main directory 
  ```
  cd Epiphany
  ```
  create a .env file with the following content:
  
  ```
server_ip="your_server_ip"
server_user="your_server_username"
server_password="your_server_password"
remote_path="path/to/remote/eve.json"
pcap_file="your_file.pcap"

elastic_endpoint="http://your-elasticsearch-url:9200"
elasticsearch_apikey="your_elasticsearch_api_key"

splunk_endpoint="https://your-splunk-url:8089"
splunk_token="your_splunk_tok
  ```
:exclamation: Note: Ensure Suricata is installed and configured on the remote server, and all API endpoints and credentials are valid.

### Installations guide
To install the required Python dependencies, I recommend using Poetry for dependency management and virtual environments:

```
pip install poetry
poetry install
poetry shell
```
:exclamation: This will create a virtual environment and install all necessary packages defined in the pyproject.toml file.

### Command-Line Usage

 | argument | Description |required |
 | -------- | ------------| -------- |
 | splunk   | Specifies the SIEM platform to use |  Yes     |
 | -upload   | Connect to the server to execute and download the .json file |No      |

 ### Example

#### Verify & Upload Alerts to TheHive (without fetching new data)
   ```
  python3 -m poetry run python main.py splunk
   ```
  This command will

  + Query Elasticsearch for alerts marked as `verified: false`
  + Check if those alerts already exist in TheHive
  + Upload only the new, unprocessed alerts to TheHive

-------

#### Full Pipeline Execution (Suricata → Splunk → Elasticsearch → TheHive)

  ```
  python3 -m poetry run python main.py splunk --upload
  ```

  This command will:

  + Connect to the remote Linux server via SSH

  + Execute Suricata with the specified PCAP file

  + Download the generated eve.json file to your local machine

  + Upload the logs to Splunk

  + Collect alerts from Splunk, enrich them, and send them to Elasticsearch

  + Upload any new alerts to TheHive




### Future Improvements

Epiphany is designed with extensibility in mind. Future versions will support data collection from additional SIEM platforms, expanding the tool’s integration capabilities and flexibility in diverse security environments.

#### Planned SIEM Integrations

+ [crowdstrike](https://www.crowdstrike.com/en-us/) - integration for ingesting alerts and telemetry data


### Contribution

- **Project Link**: [Epiphany](https://github.com/kaykRodr1gu3s/Epiphany/)
- **Linkedin**: [Linkedin](www.linkedin.com/in/kayk-rodrigues-504a03273)

