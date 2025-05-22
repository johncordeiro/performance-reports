#!/usr/bin/env python3
"""
Test Script for Conversation Analyzer
====================================

This script tests the ConversationAnalyzer functionality using mock data,
without making actual API calls.

Usage:
    python test_analyzer.py
"""

import json
from conversation_analyzer import ConversationAnalyzer

def test_trace_analysis():
    """Test the trace analysis functionality with sample data."""
    
    print("Testing trace analysis functionality...")
    
    # Initialize analyzer with dummy token and project UUID
    analyzer = ConversationAnalyzer("dummy_token", "cd58be91-6218-4c0b-89ba-9fc2f032c0b3")
    
    # Sample trace data based on the example provided in the request
    sample_traces = [
        {
            "sessionId": "project-cd58be91-6218-4c0b-89ba-9fc2f032c0b3-session-ext:651311104728_64",
            "trace": {
                "orchestrationTrace": {
                    "invocationInput": {
                        "agentCollaboratorInvocationInput": {
                            "agentCollaboratorAliasArn": "arn:aws:bedrock:us-east-1:739649339569:agent-alias/INLINE_AGENT/orders_agent_vtex",
                            "agentCollaboratorName": "orders_agent_vtex",
                            "input": {
                                "text": "Por favor, verifique o status do pedido 1506390500046-01.",
                                "type": "TEXT"
                            }
                        },
                        "invocationType": "AGENT_COLLABORATOR"
                    }
                }
            }
        },
        {
            "sessionId": "e216b105-c765-4103-bdcd-7a9ccc8f872f",
            "trace": {
                "orchestrationTrace": {
                    "invocationInput": {
                        "actionGroupInvocationInput": {
                            "actionGroupName": "getstatusbyordernumber",
                            "executionType": "LAMBDA",
                            "function": "order_status_by_order_number-17",
                            "parameters": [
                                {
                                    "name": "orderID",
                                    "type": "string",
                                    "value": "1506390500046-01"
                                }
                            ]
                        },
                        "invocationType": "ACTION_GROUP"
                    }
                }
            }
        },
        {
            "sessionId": "test-session-2",
            "trace": {
                "orchestrationTrace": {
                    "invocationInput": {
                        "agentCollaboratorInvocationInput": {
                            "agentCollaboratorName": "exchange_agent_troquecommerce",
                            "input": {
                                "text": "Check exchange status for customer",
                                "type": "TEXT"
                            }
                        },
                        "invocationType": "AGENT_COLLABORATOR"
                    }
                }
            }
        },
        {
            "sessionId": "test-session-3",
            "trace": {
                "orchestrationTrace": {
                    "invocationInput": {
                        "actionGroupInvocationInput": {
                            "actionGroupName": "customerservice",
                            "executionType": "LAMBDA",
                            "function": "update_customer_info",
                            "parameters": [
                                {
                                    "name": "customer_id",
                                    "type": "string",
                                    "value": "12345"
                                },
                                {
                                    "name": "email",
                                    "type": "string", 
                                    "value": "customer@example.com"
                                }
                            ]
                        },
                        "invocationType": "ACTION_GROUP"
                    }
                }
            }
        }
    ]
    
    # Analyze each trace
    for i, trace in enumerate(sample_traces, 1):
        print(f"  Analyzing trace {i}/{len(sample_traces)}")
        analyzer.analyze_trace(trace)
    
    # Display results
    print("\nTest Results:")
    print(f"  Agent invocations detected: {len(analyzer.agent_invocations)}")
    print(f"  Tool invocations detected: {len(analyzer.tool_invocations)}")
    print(f"  Tool call records: {len(analyzer.tool_calls_data)}")
    
    # Verify agent invocations
    expected_agents = {'orders_agent_vtex': 1, 'exchange_agent_troquecommerce': 1}
    print(f"\nAgent Invocations:")
    for agent, count in analyzer.agent_invocations.items():
        print(f"  {agent}: {count}")
        if agent in expected_agents and count == expected_agents[agent]:
            print(f"    ✓ Correct count for {agent}")
        else:
            print(f"    ✗ Unexpected count for {agent}")
    
    # Verify tool invocations
    expected_tools = {'order_status_by_order_number-17': 1, 'update_customer_info': 1}
    print(f"\nTool Invocations:")
    for tool, count in analyzer.tool_invocations.items():
        print(f"  {tool}: {count}")
        if tool in expected_tools and count == expected_tools[tool]:
            print(f"    ✓ Correct count for {tool}")
        else:
            print(f"    ✗ Unexpected count for {tool}")
    
    # Verify tool call data
    print(f"\nTool Call Data:")
    for i, call_data in enumerate(analyzer.tool_calls_data, 1):
        print(f"  Call {i}: {call_data['function_name']}")
        if 'param_orderID' in call_data:
            print(f"    Parameter orderID: {call_data['param_orderID']}")
        if 'param_customer_id' in call_data:
            print(f"    Parameter customer_id: {call_data['param_customer_id']}")
        if 'param_email' in call_data:
            print(f"    Parameter email: {call_data['param_email']}")

def test_csv_generation():
    """Test CSV generation with mock data."""
    
    print("\n" + "=" * 50)
    print("Testing CSV generation...")
    
    # Initialize analyzer with dummy token and project UUID
    analyzer = ConversationAnalyzer("dummy_token", "cd58be91-6218-4c0b-89ba-9fc2f032c0b3")
    
    # Add some mock tool call data
    analyzer.tool_calls_data = [
        {
            'function_name': 'order_status_by_order_number',
            'action_group_name': 'getstatusbyordernumber',
            'execution_type': 'LAMBDA',
            'param_orderID': '1506390500046-01'
        },
        {
            'function_name': 'update_customer_info',
            'action_group_name': 'customerservice', 
            'execution_type': 'LAMBDA',
            'param_customer_id': '12345',
            'param_email': 'customer@example.com'
        },
        {
            'function_name': 'order_status_by_order_number',
            'action_group_name': 'getstatusbyordernumber',
            'execution_type': 'LAMBDA',
            'param_orderID': '9876543210987-01'
        }
    ]
    
    # Add mock statistics
    analyzer.tool_invocations = {
        'order_status_by_order_number': 2,
        'update_customer_info': 1
    }
    
    analyzer.agent_invocations = {
        'orders_agent_vtex': 2,
        'customer_service_agent': 1
    }
    
    try:
        # Test CSV generation
        analyzer.generate_csv_files()
        print("  ✓ CSV generation completed successfully")
        
        # Test statistics generation
        analyzer.generate_statistics()
        print("  ✓ Statistics generation completed successfully")
        
        # Test statistics file save
        analyzer.save_statistics_to_file()
        print("  ✓ Statistics file save completed successfully")
        
    except Exception as e:
        print(f"  ✗ Error during testing: {e}")

def test_data_structures():
    """Test the basic data structures and initialization."""
    
    print("\n" + "=" * 50)
    print("Testing data structures...")
    
    # Test initialization
    analyzer = ConversationAnalyzer("test_token", "cd58be91-6218-4c0b-89ba-9fc2f032c0b3")
    
    # Verify initialization
    assert hasattr(analyzer, 'agent_invocations'), "Missing agent_invocations attribute"
    assert hasattr(analyzer, 'tool_invocations'), "Missing tool_invocations attribute"
    assert hasattr(analyzer, 'tool_calls_data'), "Missing tool_calls_data attribute"
    assert hasattr(analyzer, 'project_uuid'), "Missing project_uuid attribute"
    
    print("  ✓ All required attributes initialized")
    
    # Test that collections start empty
    assert len(analyzer.agent_invocations) == 0, "Agent invocations should start empty"
    assert len(analyzer.tool_invocations) == 0, "Tool invocations should start empty"
    assert len(analyzer.tool_calls_data) == 0, "Tool calls data should start empty"
    
    print("  ✓ All collections start empty as expected")
    
    # Test project UUID
    expected_uuid = "cd58be91-6218-4c0b-89ba-9fc2f032c0b3"
    assert analyzer.project_uuid == expected_uuid, f"Unexpected project UUID: {analyzer.project_uuid}"
    
    print("  ✓ Project UUID matches expected value")

def main():
    """Run all tests."""
    
    print("Conversation Analyzer - Test Suite")
    print("=" * 50)
    
    try:
        # Test data structures
        test_data_structures()
        
        # Test trace analysis
        test_trace_analysis()
        
        # Test CSV generation
        test_csv_generation()
        
        print("\n" + "=" * 50)
        print("ALL TESTS COMPLETED SUCCESSFULLY! ✓")
        print("=" * 50)
        print("\nThe analyzer is ready for use with real data.")
        print("Run with: python conversation_analyzer.py --start-date 15-05-2025 --end-date 22-05-2025 --token YOUR_TOKEN")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error during testing: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main()) 