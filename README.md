# Conversation and Agent Trace Analyzer

A comprehensive Python script for analyzing conversations and agent traces from the Weni AI platform. This tool collects conversation data, analyzes agent traces, and generates detailed statistics and CSV reports.

## Features

- **Conversation Collection**: Retrieves all conversations for a specified date range
- **Message Analysis**: Extracts all messages from each conversation
- **Agent Trace Analysis**: Analyzes agent traces to extract performance metrics
- **Statistics Generation**: Provides detailed statistics on agent and tool invocations
- **CSV Export**: Generates CSV files for detailed analysis of tool invocations
- **Rate Limiting**: Includes built-in rate limiting to be respectful to the APIs

## Requirements

- Python 3.7 or higher
- Required packages (install via `pip install -r requirements.txt`):
  - requests>=2.31.0
  - pandas>=2.0.0
  - urllib3>=1.26.0
  - python-dotenv>=1.0.0

## Security

**Important:** Never commit your `.env` file to version control! Add `.env` to your `.gitignore` file:

```bash
echo ".env" >> .gitignore
```

The `.env` file contains sensitive credentials and should be kept secure.

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (recommended):
   ```bash
   # Copy the template and edit with your credentials
   cp env_template.txt .env
   # Edit .env file with your actual values
   ```

## Usage

### Basic Usage

```bash
# Using command line arguments
python conversation_analyzer.py --start-date 15-05-2025 --end-date 22-05-2025 --token YOUR_BEARER_TOKEN --project-uuid YOUR_PROJECT_UUID

# Using environment variables (recommended)
python conversation_analyzer.py --start-date 15-05-2025 --end-date 22-05-2025
```

### Command Line Arguments

- `--start-date` / `-s`: Start date in DD-MM-YYYY format (required)
- `--end-date` / `-e`: End date in DD-MM-YYYY format (required)
- `--token` / `-t`: Bearer authorization token (optional if set in environment)
- `--project-uuid` / `-p`: Project UUID (optional if set in environment)
- `--output-dir` / `-o`: Output directory for generated files (optional, default: current directory)

### Environment Variables

Create a `.env` file in the project directory with:

```env
WENI_BEARER_TOKEN=your_bearer_token_here
WENI_PROJECT_UUID=your_project_uuid_here
```

### Examples

```bash
# Using environment variables (recommended - requires .env file)
python conversation_analyzer.py -s 15-05-2025 -e 22-05-2025

# Using command line arguments
python conversation_analyzer.py -s 15-05-2025 -e 22-05-2025 -t YOUR_TOKEN -p YOUR_PROJECT_UUID

# Analysis with custom output directory
python conversation_analyzer.py --start-date 01-01-2025 --end-date 31-01-2025 --output-dir ./reports

# Mixed approach - override project UUID from command line
python conversation_analyzer.py -s 15-05-2025 -e 22-05-2025 --project-uuid DIFFERENT_PROJECT_UUID

# Help message
python conversation_analyzer.py --help
```

## How It Works

The script follows this workflow:

1. **Conversation Collection**: 
   - Fetches all conversations from the billing API for the specified date range
   - Handles pagination automatically
   - Uses the endpoint: `https://billing.weni.ai/api/v1/{project_uuid}/conversations/`

2. **Message Extraction**:
   - For each conversation, retrieves all messages using the contact URN and start time
   - Filters for agent messages (source_type: "agent")
   - Uses the endpoint: `https://nexus.weni.ai/api/{project_uuid}/conversations/`

3. **Trace Analysis**:
   - For each agent message, fetches agent traces using the message ID
   - Analyzes traces to extract agent and tool invocations
   - Uses the endpoint: `https://nexus.weni.ai/api/agents/traces/`

4. **Statistics Generation**:
   - Counts agent invocations by agent name
   - Counts tool invocations by function name
   - Tracks detailed tool call parameters

5. **Report Generation**:
   - Displays statistics in the console
   - Saves statistics to a text file
   - Generates CSV files for detailed tool invocation analysis

## Output Files

The script generates several output files with timestamps:

### Statistics File
- `conversation_statistics_YYYYMMDD_HHMMSS.txt`: Complete statistics report

### CSV Files
- `tool_invocations_YYYYMMDD_HHMMSS.csv`: All tool invocations with parameters
- `tool_{function_name}_YYYYMMDD_HHMMSS.csv`: Individual CSV for each tool type

## Data Analysis

### Agent Invocations
Tracks how many times each collaborator agent was called:
- Extracted from: `trace.orchestrationTrace.invocationInput.agentCollaboratorInvocationInput.agentCollaboratorName`
- Examples: `orders_agent_vtex`, `exchange_agent_troquecommerce`

### Tool Invocations
Tracks how many times each tool/function was called:
- Extracted from: `trace.orchestrationTrace.invocationInput.actionGroupInvocationInput.function`
- Examples: `order_status_by_order_number-17`, `getstatusbyordernumber__order_status_by_order_number-17`

### Tool Parameters
For each tool invocation, captures all parameters:
- Parameter names and values from: `trace.orchestrationTrace.invocationInput.actionGroupInvocationInput.parameters`
- Creates separate CSV columns for each parameter (e.g., `param_orderID`, `param_log_id`)

## API Endpoints Used

1. **Billing API**: `https://billing.weni.ai/api/v1/{project_uuid}/conversations/`
   - Purpose: Get conversations for date range
   - Parameters: page, start, end

2. **Nexus Conversations API**: `https://nexus.weni.ai/api/{project_uuid}/conversations/`
   - Purpose: Get messages for a specific conversation
   - Parameters: start, contact_urn

3. **Nexus Traces API**: `https://nexus.weni.ai/api/agents/traces/`
   - Purpose: Get agent traces for a specific message
   - Parameters: project_uuid, log_id

## Error Handling

The script includes comprehensive error handling:
- Network request failures
- JSON parsing errors
- Missing data fields
- Rate limiting and API throttling
- User interruption (Ctrl+C)

## Rate Limiting

The script includes built-in delays to be respectful to the APIs:
- 0.5 seconds between conversation page requests
- 0.2 seconds between trace requests

## Example Output

### Console Output
```
Starting conversation analysis...
Date range: 15-05-2025 to 22-05-2025
Project UUID: cd58be91-6218-4c0b-89ba-9fc2f032c0b3
--------------------------------------------------
Fetching conversations page 1 for dates 15-05-2025 to 22-05-2025...
Collected 5 conversations from page 1
Total conversations collected: 5

Processing conversation 1/5 (ID: 24293975)
  Found 4 total messages, 2 agent messages
    Processing agent message 1/2 (ID: 100483)
      Found 15 trace objects

============================================================
CONVERSATION ANALYSIS STATISTICS
============================================================

AGENT INVOCATIONS:
------------------------------
  orders_agent_vtex: 1

Total agent invocations: 1

TOOL INVOCATIONS:
------------------------------
  order_status_by_order_number-17: 1

Total tool invocations: 1
```

### CSV Output Example
| function_name | action_group_name | execution_type | param_orderID |
|---------------|-------------------|----------------|---------------|
| order_status_by_order_number-17 | getstatusbyordernumber | LAMBDA | 1506390500046-01 |

## Troubleshooting

### Common Issues

1. **Authentication Error**: Ensure your Bearer token is valid and not expired
2. **Missing Environment Variables**: Check that your `.env` file exists and contains valid `WENI_BEARER_TOKEN` and `WENI_PROJECT_UUID`
3. **Date Format Error**: Use DD-MM-YYYY format (e.g., 15-05-2025)
4. **Project UUID Error**: Ensure your project UUID is correct and you have access to it
5. **Network Timeout**: The script includes retry logic, but very slow networks may cause issues
6. **Empty Results**: Check date range and ensure conversations exist for the specified period

### Debug Mode

For debugging, you can add print statements or use a debugger to inspect:
- API responses
- Trace structure
- Parameter extraction

## Contributing

Feel free to submit issues or pull requests to improve the script:
- Add support for additional trace types
- Improve error handling
- Add more output formats
- Optimize performance

## License

This script is provided as-is for analyzing Weni AI platform data. Please ensure you have proper authorization to access the APIs before using this tool. 