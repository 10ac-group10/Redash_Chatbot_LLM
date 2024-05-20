## Introduction

The Redash ChatGPT Plugin is an integration that brings natural language conversation capabilities powered by ChatGPT to your Redash dashboard. With this plugin, Redash users can engage in interactive and conversational queries, as well as visualize data directly from the chat interface.

## Features

* Conversational Queries: Users can interact with Redash using natural language queries, making the process more intuitive and user-friendly.
* Interactive Responses: ChatGPT generates human-like responses, providing users with informative and contextual feedback on their queries.
* Data Visualization: The plugin allows users to visualize query results directly within the chat interface, enabling faster data exploration and analysis.

`The Redash ChatGPT Plugin is an exciting project that aims to integrate natural language conversation capabilities powered by ChatGPT into your Redash dashboard. Although the plugin is still a work in progress, it currently provides functionality for engaging in conversational queries with ChatGPT directly within the Redash interface`

## Requirements Before Installation
- Docker
- Docker Compose
- Node.js
- Yarn
- Python >= 3.9 and <= 3.10.2
- Poetry

### Setup and Installation
1. **Clone the Repository**
    ```bash
    git clone git@github.com:10ac-group10/Redash_Chatbot_LLM.git
    cd Redash_Chatbot_LLM
    ```

2. **Create a Virtual Environment and Install Dependencies**
```bash
python -m venv venv
source venv/bin/activate  # For Unix or MacOS
venv\Scripts\activate     # For Windows
pip install -r requirements.txt
```

3. **Install the frontend dependencies**
    ```bash
    poetry add openai
    ```

    ```bash
    yarn add react-icons
    ```

    ```bash
    yarn add react-syntax-highlighter
    ```


4. **Environment Variables**
    - Create a `.env` file in the root directory and add the following environment variables:
    ```bash
    OPENAI_API_KEY=your_openai_api_key
    ```
    - Replace `your_openai_api_key` with your OpenAI API key.
    - **Get your free OpenAI API key** - [OpenAI](https://platform.openai.com/)
    - **Note:** Follow the best practices by not commiting the .env file to the repository.

5. **Build the application**

   - Run the following commands to get the container up and running and start the application:

      ```bash
      yarn
      ```
      ```bash
      make build
      ```
      ```bash
      make compose_build
      ```
      ```bash
     make up
      ```

   - If running all the above commands successfully, in future you can then simplify the process by running the below command to start the application.

        ```bash
      make run
        ```

6. **Access the Application**
   - Open your browser and navigate to `http://localhost:8081` to access the Redash homepage.

   - **Note**: The port 8081 is access to Nginx, which is the reverse proxy server for the Redash application. The Redash application runs on port 5000, but it is not directly accessible from the browser. The Nginx server acts as a reverse proxy server that forwards requests from the browser to the Redash application running on port 5000.

7. **Login to Redash**
   - After accessing the Redash setup page, you will be prompted to sign up.
   - Here is how the redash setup page looks like:
   ![login page](./screenshots/login_page.png "Redash Setup Page")
   - Fill in the required details and click on the `Setup` button to create an account.

8. **Get the Redash API Key**
   - After creating an account, you will be redirected to the Redash homepage.
   - Click on the settings icon at the bottom left corner of the page.
   - Navigate to the `Account` tab.
   ![account settings](./screenshots/redash_api_key.png "Account Settings")
   - Copy the API key and save it in a secure location.
   - **Note**: The API key is required for making API requests to the Redash server.
   - Locate the `.env` file and add the `REDASH_API_KEY` environment variable with the copied API key.
   ```bash
    REDASH_API_KEY=your_redash_api_key
   ```

