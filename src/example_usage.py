#!/usr/bin/env python3
"""
Example Usage of the Conversation Analyzer
==========================================

This script demonstrates how to use the ConversationAnalyzer class programmatically.
You can use this as a reference for integrating the analyzer into your own applications.

Usage:
    python example_usage.py
"""

from conversation_analyzer import ConversationAnalyzer
import os
from datetime import datetime

def example_basic_usage():
    """Example of basic usage with the ConversationAnalyzer."""
    
    # You would replace this with your actual Bearer token
    bearer_token = "YOUR_BEARER_TOKEN_HERE"
    
    # Check if token is provided via environment variable
    if bearer_token == "YOUR_BEARER_TOKEN_HERE":
        bearer_token = os.getenv('WENI_BEARER_TOKEN')
        if not bearer_token:
            print("Please set your Bearer token either:")
            print("1. Set the WENI_BEARER_TOKEN environment variable")
            print("2. Replace 'YOUR_BEARER_TOKEN_HERE' in this script")
            return
    
    # Initialize the analyzer (using default project UUID for example)
    print("Initializing Conversation Analyzer...")
    project_uuid = "cd58be91-6218-4c0b-89ba-9fc2f032c0b3"  # Replace with your project UUID
    analyzer = ConversationAnalyzer(bearer_token, project_uuid)
    
    # Set date range (example dates)
    start_date = "15-05-2025"
    end_date = "22-05-2025"
    
    print(f"Analyzing conversations from {start_date} to {end_date}")
    
    try:
        # Process conversations
        analyzer.process_conversations(start_date, end_date)
        
        # Generate statistics
        analyzer.generate_statistics()
        
        # Generate CSV files
        analyzer.generate_csv_files()
        
        # Save statistics to file
        analyzer.save_statistics_to_file()
        
        # Access the collected data programmatically
        print("\n" + "=" * 50)
        print("PROGRAMMATIC ACCESS TO DATA")
        print("=" * 50)
        
        print(f"Agent invocations collected: {len(analyzer.agent_invocations)}")
        print(f"Tool invocations collected: {len(analyzer.tool_invocations)}")
        print(f"Tool call records: {len(analyzer.tool_calls_data)}")
        
        # Example: Get the most used agent
        if analyzer.agent_invocations:
            most_used_agent = max(analyzer.agent_invocations.items(), key=lambda x: x[1])
            print(f"Most used agent: {most_used_agent[0]} ({most_used_agent[1]} invocations)")
        
        # Example: Get the most used tool
        if analyzer.tool_invocations:
            most_used_tool = max(analyzer.tool_invocations.items(), key=lambda x: x[1])
            print(f"Most used tool: {most_used_tool[0]} ({most_used_tool[1]} invocations)")
        
        print("\nAnalysis completed successfully!")
        
    except Exception as e:
        print(f"Error during analysis: {e}")

def example_custom_processing():
    """Example of custom processing of the collected data."""
    
    print("\n" + "=" * 50)
    print("CUSTOM DATA PROCESSING EXAMPLE")
    print("=" * 50)
    
    # This is just an example with dummy data
    # In real usage, you would use the actual analyzer instance
    
    # Example: Calculate performance metrics
    sample_agent_data = {
        'orders_agent_vtex': 15,
        'exchange_agent_troquecommerce': 8,
        'general_support_agent': 23
    }
    
    sample_tool_data = {
        'order_status_by_order_number': 12,
        'get_exchange_status': 7,
        'update_customer_info': 19
    }
    
    total_agent_calls = sum(sample_agent_data.values())
    total_tool_calls = sum(sample_tool_data.values())
    
    print(f"Total agent calls: {total_agent_calls}")
    print(f"Total tool calls: {total_tool_calls}")
    print(f"Agent efficiency ratio: {total_tool_calls/total_agent_calls:.2f}")
    
    # Agent usage distribution
    print("\nAgent Usage Distribution:")
    for agent, count in sample_agent_data.items():
        percentage = (count / total_agent_calls) * 100
        print(f"  {agent}: {percentage:.1f}%")
    
    # Tool usage distribution  
    print("\nTool Usage Distribution:")
    for tool, count in sample_tool_data.items():
        percentage = (count / total_tool_calls) * 100
        print(f"  {tool}: {percentage:.1f}%")

def example_export_formats():
    """Example of different export formats you could implement."""
    
    print("\n" + "=" * 50)
    print("CUSTOM EXPORT FORMATS EXAMPLE")
    print("=" * 50)
    
    # Example data
    sample_data = [
        {
            'timestamp': '2025-05-15T14:40:36.653446Z',
            'agent': 'orders_agent_vtex',
            'tool': 'order_status_by_order_number',
            'parameters': {'orderID': '1506390500046-01'},
            'execution_time_ms': 1250
        },
        {
            'timestamp': '2025-05-15T15:22:18.445332Z',
            'agent': 'exchange_agent_troquecommerce',
            'tool': 'get_exchange_status',
            'parameters': {'cpf': '12345678901'},
            'execution_time_ms': 890
        }
    ]
    
    # Example: Export to JSON
    import json
    json_filename = f"conversation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_filename, 'w') as f:
        json.dump(sample_data, f, indent=2)
    print(f"Exported JSON: {json_filename}")
    
    # Example: Export to Excel (requires openpyxl)
    try:
        import pandas as pd
        df = pd.DataFrame(sample_data)
        excel_filename = f"conversation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(excel_filename, index=False)
        print(f"Exported Excel: {excel_filename}")
    except ImportError:
        print("Excel export requires openpyxl: pip install openpyxl")

if __name__ == '__main__':
    print("Conversation Analyzer - Example Usage")
    print("=" * 50)
    
    # Run basic usage example
    example_basic_usage()
    
    # Run custom processing example
    example_custom_processing()
    
    # Run export formats example
    example_export_formats()
    
    print("\n" + "=" * 50)
    print("Example completed!")
    print("To run the actual analyzer, use:")
    print("python conversation_analyzer.py --start-date 15-05-2025 --end-date 22-05-2025 --token YOUR_TOKEN") 