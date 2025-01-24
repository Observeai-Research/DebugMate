# DebugMate: An AI Agent for Efficient On-Call Debugging in Large Production Systems

DebugMate is an AI Agent that integrates an organization’s internal context with external knowledge sources. DebugMate connects to the organization’s key system resources like documentation, codebase, and knowledge base of historical incidents, along with online developer platforms (eg. StackOverflow, GitHub) and helps Software Engineers respond faster by generating multiple hypotheses for identifying the root cause of a production issue. DebugMate employs Retrieval-Augmented Generation (RAG), ReAct, Tree-of-Thought, and long-term memory to provide grounded hypotheses for debugging via structured and systematic self-planning.

## Installation

To get started, clone the repository and install the required dependencies:

```bash
git clone https://github.com/Observeai-Research/DebugMate.git
cd debugging-assistant
pip install -r requirements.txt
```

## Configuration
Before running DebugMate, you'll need to set up your API keys and environment variables. Add the following to your environment:

```
export OPENAI_API_KEY="<your_openai_api_key>"
export BITBUCKET_API_KEY="<your_bitbucket_api_key>"

# Confluence Tool Configuration (if using ConfluenceTool)
export CONFLUENCE_SPACE_NAME="<your_confluence_space_name>"
export CONFLUENCE_SPACE_KEY="<your_confluence_space_key>"
export CONFLUENCE_PRIVATE_API_KEY="<your_confluence_private_api_key>"
export EMAIL_ADDRESS="<your_confluence_email_address>"
```

## Instructions

1. **Replace Path in `code_tool.py`**:
    - Open `code_tool.py`
    - Replace `./temp_java` with the absolute path of your codebase

2. **Run CodeLoader to preprocess Class Paths and Interface Mappings**:
    - Open `tools/code_loader.py`
    - Replace `./temp_java` with the absolute path of your codebase
    ```sh
    python tools/code_loader.py
    ```

3. **Include new code bases to process**: 
    - run 
    ```sh
    cd tools
    ```
    - Within convertjar.py replace `<absolute_directory_path> ` with the absolute path of the compiled jar of your codebase
    ```sh
    python covertjar.py
    ```
    this produces the decompiled code within temp_java 

## Usage

**Update Stack Trace**: Place your stack trace in the stack_trace.txt file. This file will be used as input for the debugging process when provided.

**Run Query**: To see an example of how DebugMate works, run the main.py script:

```python main.py```

This script uses the stack trace provided in stack_trace.txt and demonstrates how DebugMate can help analyze and debug an issue.

## Tools Overview
- **Internal Knowledge-base (KB) Search:**
Uses advanced Retrieval-Augmented Generation (RAG) to locate and return the most relevant documentation and knowledge base entries. Search recall is enhanced through query expansion and cross-encoder reranking.

- **Code Search:**
Takes a string representing class name and construct name as input to find exact matches. Utilizes a vertical Path Tool to map class names from stack trace to file locations and uses an AST to map field objects to their respective class types.
if asked to input file path give the path after temp_java/ from the path

- **Online Developer Portal (DP) Search:**
Queries search engines with specific issue details, utilizing results from platforms like StackOverflow to find optimal solutions. Creates parse trees from HTML documents to extract relevant information that answers the questions queried.

- **TreeOfThoughts Tool:**
Allows DebugMate to  systematically explores multiple reasoning paths by saving current state of intermediate_steps and creating a new branch for each parallel function to debug simultaneously.

- **Graph Understanding Tool:**
Utilizes internal Neo4j graphs where nodes represent microservices, databases, API gateways, and messaging queues, with relationships such as ‘connected’, ‘publishes’, or ‘consumes’.

## Contributing
Contributions are welcome. Please open an issue or submit a pull request with your changes.
