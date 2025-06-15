# DevAICourse Backend

This repository contains an educational backend project based on the [Swagger Petstore](https://swagger.io/docs/specification/about/) API. The project demonstrates how to incrementally build a RESTful API using [FastAPI](https://fastapi.tiangolo.com/) and SQLite, following the OpenAPI specification.

## Purpose

The main goal of this repository is to provide a step-by-step learning resource for developers who want to understand how to design, implement, and evolve a backend API. Each stage in the repository represents a milestone in the development process, showing how to approach and solve common backend challenges.

## Task

For each stage of the project, your goal is to incrementally implement the required features and improvements as described in the stage documentation. Use an AI coding assistant (such as GitHub Copilot or a dedicated model) to help you:

1. Understand the Requirements: Carefully read the description and goals for the current stage.
2. Plan the Changes: Identify which files and code sections need to be added or modified. You can also use a code agent and let it decide where to make changes - but carefully review, what the agent does
3. Interact with the AI Assistant: Ask the assistant for code snippets, explanations, or best practices relevant to the stage. Request code reviews or suggestions for improvements. Use the assistant to generate boilerplate code, unit tests, or documentation as needed.
4. Implement and Test: Apply the suggested changes to your codebase. Test the new functionality to ensure it meets the requirements. Hint: Some code agents like Roo Code also test whether implemented changes work.
5. Compare your changes with the suggested state in the State branches. Due to usage of the AI, your code does not neccessary look like the solution given in the stage.

## Stages

The repository is divided into different stages, each represented by a branch or folder (depending on your setup):

0. **Stage 0: Main Branch**
   - The initial repo with the Petstore API specification 

2. **Stage 1: Model Generation**
   - Contains a "generated/models" folder with generated model classes from the API specification
   - Model classes match with the API specification yml-File
   - Hint: Try to generate models directly with help of the AI and also try to make use of CLI tools to generate the models.

3. **Stage 2: FastAPI**
   - Implement basic CRUD for pets, categories, and users as basis for frontend
   - Make usage of FastAPI and Uvicorn Webserver
   - Introduce main.py file as a runnable starting point for the project
   - API works with dummy data

4. **Stage 3: DB and Connection**
   - Adds a SQLite Database file named "app.db" to the "data" subfolder
   - Includes an index.py file to initialize the database schema
   - Connects the API to the database and read and write data
   - Hint: Check the DB schema for SQL best practices.

5. **Stage 4: Connect to frontend**
   - Add CORS support for frontend integration.
