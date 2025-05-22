#!/usr/bin/env python3
"""
Conversation and Agent Trace Analyzer
====================================

This script collects conversations from the Weni AI platform, analyzes agent traces,
and generates comprehensive statistics and CSV reports.

Usage:
    python conversation_analyzer.py --start-date 15-05-2025 --end-date 22-05-2025 --token YOUR_BEARER_TOKEN

Author: AI Assistant
Date: 2025
"""

import argparse
import requests
import json
import pandas as pd
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
import time
import os
from dotenv import load_dotenv


class ConversationAnalyzer:
    """Main class for analyzing conversations and agent traces."""
    
    def __init__(self, bearer_token: str, project_uuid: str):
        """
        Initialize the analyzer with authentication and project information.
        
        Args:
            bearer_token: Bearer token for API authentication
            project_uuid: Project UUID for the Weni AI platform
        """
        self.bearer_token = bearer_token
        self.project_uuid = project_uuid
        self.session = requests.Session()
        self.session.headers.update({
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7,es;q=0.6,nl;q=0.5,fr;q=0.4',
            'authorization': f'Bearer {bearer_token}',
            'origin': 'https://intelligence-next.weni.ai',
            'priority': 'u=1, i',
            'referer': 'https://intelligence-next.weni.ai/supervisor',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
        })
        
        # Statistics containers
        self.agent_invocations = defaultdict(int)
        self.tool_invocations = defaultdict(int)
        self.tool_calls_data = []
    
    def get_conversations(self, start_date: str, end_date: str, page: int = 1) -> Dict[str, Any]:
        """
        Get conversations for the specified date range.
        
        Args:
            start_date: Start date in format DD-MM-YYYY
            end_date: End date in format DD-MM-YYYY
            page: Page number for pagination
            
        Returns:
            JSON response containing conversations
        """
        url = f"https://billing.weni.ai/api/v1/{self.project_uuid}/conversations/"
        params = {
            'page': page,
            'start': start_date,
            'end': end_date
        }
        
        print(f"Fetching conversations page {page} for dates {start_date} to {end_date}...")
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching conversations: {e}")
            return {}
    
    def get_all_conversations(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Get all conversations across all pages.
        
        Args:
            start_date: Start date in format DD-MM-YYYY
            end_date: End date in format DD-MM-YYYY
            
        Returns:
            List of all conversations
        """
        all_conversations = []
        page = 1
        
        while True:
            response = self.get_conversations(start_date, end_date, page)
            
            if not response or 'results' not in response:
                break
                
            conversations = response['results']
            if not conversations:
                break
                
            all_conversations.extend(conversations)
            print(f"Collected {len(conversations)} conversations from page {page}")
            
            # Check if there's a next page
            if not response.get('next'):
                break
                
            page += 1
            time.sleep(0.5)  # Be nice to the API
        
        print(f"Total conversations collected: {len(all_conversations)}")
        return all_conversations
    
    def get_conversation_messages(self, contact_urn: str, start_time: str) -> Dict[str, Any]:
        """
        Get all messages for a specific conversation.
        
        Args:
            contact_urn: The contact URN from the conversation
            start_time: The conversation start time
            
        Returns:
            JSON response containing messages
        """
        # URL encode the contact_urn and start_time
        encoded_urn = urllib.parse.quote(contact_urn, safe='')
        encoded_start = urllib.parse.quote(start_time, safe='')
        
        url = f"https://nexus.weni.ai/api/{self.project_uuid}/conversations/"
        params = {
            'start': start_time,
            'contact_urn': contact_urn
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching messages for URN {contact_urn}: {e}")
            return {}
    
    def get_agent_traces(self, log_id: int) -> List[Dict[str, Any]]:
        """
        Get agent traces for a specific message.
        
        Args:
            log_id: The message ID to get traces for
            
        Returns:
            List of trace objects
        """
        url = "https://nexus.weni.ai/api/agents/traces/"
        params = {
            'project_uuid': self.project_uuid,
            'log_id': log_id
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching traces for log_id {log_id}: {e}")
            return []
    
    def analyze_trace(self, trace_obj: Dict[str, Any]) -> None:
        """
        Analyze a single trace object to extract agent and tool invocations.
        
        Args:
            trace_obj: Individual trace object from the response
        """
        if 'trace' not in trace_obj:
            return
            
        trace = trace_obj['trace']
        
        # Check for orchestration trace
        if 'orchestrationTrace' in trace:
            orch_trace = trace['orchestrationTrace']
            
            # Check for agent collaborator invocations
            if 'invocationInput' in orch_trace:
                invocation_input = orch_trace['invocationInput']
                
                # Agent collaborator invocation
                if 'agentCollaboratorInvocationInput' in invocation_input:
                    agent_info = invocation_input['agentCollaboratorInvocationInput']
                    agent_name = agent_info.get('agentCollaboratorName', 'unknown')
                    self.agent_invocations[agent_name] += 1
                
                # Action group (tool) invocation
                elif 'actionGroupInvocationInput' in invocation_input:
                    action_info = invocation_input['actionGroupInvocationInput']
                    function_name = action_info.get('function', 'unknown')
                    self.tool_invocations[function_name] += 1
                    
                    # Collect detailed tool call data for CSV
                    tool_call_data = {
                        'function_name': function_name,
                        'action_group_name': action_info.get('actionGroupName', ''),
                        'execution_type': action_info.get('executionType', '')
                    }
                    
                    # Add parameters as separate columns
                    if 'parameters' in action_info:
                        for param in action_info['parameters']:
                            param_name = param.get('name', '')
                            param_value = param.get('value', '')
                            tool_call_data[f'param_{param_name}'] = param_value
                    
                    self.tool_calls_data.append(tool_call_data)
    
    def process_conversations(self, start_date: str, end_date: str) -> None:
        """
        Main processing function that orchestrates the entire workflow.
        
        Args:
            start_date: Start date in format DD-MM-YYYY
            end_date: End date in format DD-MM-YYYY
        """
        print("Starting conversation analysis...")
        print(f"Date range: {start_date} to {end_date}")
        print(f"Project UUID: {self.project_uuid}")
        print("-" * 50)
        
        # Step 1: Get all conversations
        conversations = self.get_all_conversations(start_date, end_date)
        
        if not conversations:
            print("No conversations found for the specified date range.")
            return
        
        # Step 2: Process each conversation
        total_conversations = len(conversations)
        processed_messages = 0
        
        for i, conversation in enumerate(conversations, 1):
            print(f"\nProcessing conversation {i}/{total_conversations} (ID: {conversation['id']})")
            
            contact_urn = conversation['urn']
            created_on = conversation['created_on']
            
            # Get messages for this conversation
            messages_response = self.get_conversation_messages(contact_urn, created_on)
            
            if not messages_response or 'results' not in messages_response:
                print(f"  No messages found for conversation {conversation['id']}")
                continue
            
            messages = messages_response['results']
            agent_messages = [msg for msg in messages if msg.get('source_type') == 'agent']
            
            print(f"  Found {len(messages)} total messages, {len(agent_messages)} agent messages")
            
            # Step 3: Process each agent message
            for j, message in enumerate(agent_messages, 1):
                message_id = message['id']
                print(f"    Processing agent message {j}/{len(agent_messages)} (ID: {message_id})")
                
                # Get traces for this message
                traces = self.get_agent_traces(message_id)
                
                if traces:
                    print(f"      Found {len(traces)} trace objects")
                    for trace_obj in traces:
                        self.analyze_trace(trace_obj)
                else:
                    print(f"      No traces found for message {message_id}")
                
                processed_messages += 1
                time.sleep(0.2)  # Rate limiting
        
        print(f"\nProcessing complete!")
        print(f"Total conversations processed: {total_conversations}")
        print(f"Total agent messages processed: {processed_messages}")
    
    def generate_statistics(self) -> None:
        """Generate and display statistics."""
        print("\n" + "=" * 60)
        print("CONVERSATION ANALYSIS STATISTICS")
        print("=" * 60)
        
        # Agent Invocations
        print("\nAGENT INVOCATIONS:")
        print("-" * 30)
        if self.agent_invocations:
            for agent_name, count in sorted(self.agent_invocations.items()):
                print(f"  {agent_name}: {count}")
            print(f"\nTotal agent invocations: {sum(self.agent_invocations.values())}")
        else:
            print("  No agent invocations found")
        
        # Tool Invocations
        print("\nTOOL INVOCATIONS:")
        print("-" * 30)
        if self.tool_invocations:
            for tool_name, count in sorted(self.tool_invocations.items()):
                print(f"  {tool_name}: {count}")
            print(f"\nTotal tool invocations: {sum(self.tool_invocations.values())}")
        else:
            print("  No tool invocations found")
    
    def generate_csv_files(self) -> None:
        """Generate CSV files for tool invocations."""
        print("\nGenerating CSV files...")
        
        if not self.tool_calls_data:
            print("No tool call data to export.")
            return
        
        # Create a DataFrame from tool calls data
        df = pd.DataFrame(self.tool_calls_data)
        
        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate overall tool invocations CSV
        overall_filename = f"tool_invocations_{timestamp}.csv"
        df.to_csv(overall_filename, index=False)
        print(f"Generated overall tool invocations CSV: {overall_filename}")
        
        # Generate separate CSV for each tool
        if 'function_name' in df.columns:
            unique_tools = df['function_name'].unique()
            
            for tool_name in unique_tools:
                tool_df = df[df['function_name'] == tool_name]
                tool_filename = f"tool_{tool_name}_{timestamp}.csv"
                tool_df.to_csv(tool_filename, index=False)
                print(f"Generated tool-specific CSV: {tool_filename}")
        
        print(f"\nTotal tool invocation records exported: {len(df)}")
    
    def save_statistics_to_file(self) -> None:
        """Save statistics to a text file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stats_filename = f"conversation_statistics_{timestamp}.txt"
        
        with open(stats_filename, 'w') as f:
            f.write("CONVERSATION ANALYSIS STATISTICS\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("AGENT INVOCATIONS:\n")
            f.write("-" * 30 + "\n")
            if self.agent_invocations:
                for agent_name, count in sorted(self.agent_invocations.items()):
                    f.write(f"  {agent_name}: {count}\n")
                f.write(f"\nTotal agent invocations: {sum(self.agent_invocations.values())}\n")
            else:
                f.write("  No agent invocations found\n")
            
            f.write("\nTOOL INVOCATIONS:\n")
            f.write("-" * 30 + "\n")
            if self.tool_invocations:
                for tool_name, count in sorted(self.tool_invocations.items()):
                    f.write(f"  {tool_name}: {count}\n")
                f.write(f"\nTotal tool invocations: {sum(self.tool_invocations.values())}\n")
            else:
                f.write("  No tool invocations found\n")
        
        print(f"Statistics saved to: {stats_filename}")


def main():
    """Main function to run the conversation analyzer."""
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="Analyze conversations and agent traces from Weni AI platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python conversation_analyzer.py --start-date 15-05-2025 --end-date 22-05-2025 --token YOUR_TOKEN
  python conversation_analyzer.py -s 01-01-2025 -e 31-01-2025 -t YOUR_BEARER_TOKEN
  python conversation_analyzer.py -s 01-01-2025 -e 31-01-2025  # Uses token from .env file
        """
    )
    
    parser.add_argument(
        '--start-date', '-s',
        required=True,
        help='Start date in DD-MM-YYYY format (e.g., 15-05-2025)'
    )
    
    parser.add_argument(
        '--end-date', '-e',
        required=True,
        help='End date in DD-MM-YYYY format (e.g., 22-05-2025)'
    )
    
    parser.add_argument(
        '--token', '-t',
        required=False,
        help='Bearer authorization token (can also be set via WENI_BEARER_TOKEN env variable)'
    )
    
    parser.add_argument(
        '--project-uuid', '-p',
        required=False,
        help='Project UUID (can also be set via WENI_PROJECT_UUID env variable)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='.',
        help='Output directory for generated files (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Get token from command line or environment variable
    bearer_token = args.token or os.getenv('WENI_BEARER_TOKEN')
    if not bearer_token:
        print("Error: Bearer token is required. Provide it via:")
        print("  --token argument, or")
        print("  WENI_BEARER_TOKEN environment variable, or")
        print("  .env file with WENI_BEARER_TOKEN=your_token")
        return 1
    
    # Get project UUID from command line or environment variable
    project_uuid = args.project_uuid or os.getenv('WENI_PROJECT_UUID')
    if not project_uuid:
        print("Error: Project UUID is required. Provide it via:")
        print("  --project-uuid argument, or")
        print("  WENI_PROJECT_UUID environment variable, or")
        print("  .env file with WENI_PROJECT_UUID=your_uuid")
        return 1
    
    # Validate date format
    try:
        datetime.strptime(args.start_date, '%d-%m-%Y')
        datetime.strptime(args.end_date, '%d-%m-%Y')
    except ValueError:
        print("Error: Dates must be in DD-MM-YYYY format")
        return 1
    
    # Change to output directory if specified
    if args.output_dir != '.':
        os.makedirs(args.output_dir, exist_ok=True)
        os.chdir(args.output_dir)
    
    # Initialize analyzer
    analyzer = ConversationAnalyzer(bearer_token, project_uuid)
    
    try:
        # Process conversations
        analyzer.process_conversations(args.start_date, args.end_date)
        
        # Generate and display statistics
        analyzer.generate_statistics()
        
        # Generate CSV files
        analyzer.generate_csv_files()
        
        # Save statistics to file
        analyzer.save_statistics_to_file()
        
        print("\nAnalysis completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
        return 1
    except Exception as e:
        print(f"\nError during analysis: {e}")
        return 1


if __name__ == '__main__':
    exit(main()) 