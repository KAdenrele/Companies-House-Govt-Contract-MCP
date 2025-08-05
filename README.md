Competition Information MCP Server
Status: In Development

1. Project Description
This is a specialized Model Context Protocol (MCP) server designed to provide back-end tools for a language model like Google's Gemini. The server allows an LLM to query and analyze UK government contracts and company information by calling strongly-typed Python functions as API endpoints.

2. Features
This server exposes several tools that can be called programmatically:

Contract Analysis: Reads and processes UK government contract award data from a CSV file.

Company Information: Fetches details about specific companies (e.g., profiles, officers, charges).

Competitor Listing: Provides a list of known competitors for analysis.

Data Summarization: Can generate metrics and summaries from the loaded contract data on demand.

3. System Prerequisites
Before you begin, ensure you have the following installed on your local machine or server:

Python (Version 3.11+)

Git for cloning the repository.

Docker and Docker Desktop (Recommended for deployment).

Tesseract OCR Engine: Required for processing scanned documents.

On macOS with Homebrew: brew install tesseract

On Debian/Ubuntu: sudo apt-get install tesseract-ocr

4. Installation and Setup
Follow these steps to set up the project locally.

Step 1: Clone the Repository
Bash

git clone <your-repository-url>
cd ModelContextProtocol-CompetitionInformation
Step 2: Create and Activate a Virtual Environment
It is crucial to work within a Python virtual environment.

Bash

# Create the virtual environment
python3 -m venv .venv

# Activate it (on macOS/Linux)
source .venv/bin/activate
(On Windows, use the command .venv\Scripts\activate)

Step 3: Install Dependencies
Install all the required Python packages from the requirements.txt file.

Bash

# Ensure your virtual environment is active
pip install -r requirements.txt
5. Configuration
The server requires environment variables for configuration, such as API keys or file paths.

Create an .env file:
Copy the example file to create your local configuration.

Bash

cp .env.example .env
Edit the .env file:
Open the newly created .env file in a text editor and fill in the required values.

6. Running the Server
You can run the MCP server directly for local development or within a Docker container for a more isolated and portable deployment.

Method 1: Running Locally
This method is best for actively developing and testing your tools.

Bash

# Make sure your virtual environment is active
source .venv/bin/activate

# Run the server
python3 server.py
The server will start, and you should see a confirmation message from Uvicorn:
INFO: Uvicorn running on http://0.0.0.0:50000 (Press CTRL+C to quit)

Method 2: Using Docker (Recommended)
This is the recommended way to run the application to ensure a consistent environment.

Build the Docker Image:
From the project's root directory, run the build command.

Bash

docker build -t mcp-server-app .
Run the Docker Container:
This command starts the container, maps the port, and injects your environment variables from the .env file.

Bash

docker run -d -p 50000:50000 --env-file ./.env mcp-server-app
-d: Runs the container in detached (background) mode.

-p 50000:50000: Maps port 50000 on your computer to port 50000 in the container.

--env-file ./.env: Securely passes the variables from your .env file to the container.

