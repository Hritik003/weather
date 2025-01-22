# MCP Weather Server

A lightweight **Model Context Protocol (MCP)** server designed for handling weather data, with a Command-Line Interface (CLI) client for interaction. This project demonstrates how to create and interact with an MCP server, focusing on weather-related information.

## Features

- **MCP Server**: A modular server to handle weather data and client requests.
- **CLI Client**: A command-line tool to connect and interact with the server.
- **Asynchronous Communication**: Leverages `asyncio` for efficient client-server interaction.
- **Extensibility**: Easily extend the server to support additional commands or data formats.

## Requirements

- Python 3.12 or higher
- `asyncio`
- Any additional Python packages can be found in `requirements.txt`.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Hritik003/mcp-weather-server.git
   ```

2. Start the server
   ```bash
   cd Server
   uv --directory <path/to/weather> run weather
   ```

3. Start the Client
    ```bash
   cd mcp-Client
   uv run client.py <path/to/server.py>
   ```

