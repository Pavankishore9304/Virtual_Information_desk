"""
Test to verify intelligent routing between SQL database and Vector database
based on different query types
"""
from agents.planner import PlannerAgent
from agents.text_to_sql import TextToSQLAgent
from agents.retriever_agent import RetrieverAgent
from core.rag.vector_store import VectorStore
from core.db.database import get_db

def test_query_routing():
    """Test different query types to verify intelligent routing"""
    
    planner = PlannerAgent()
    
    test_cases = [
        # SQL Database Queries (Structured Data)
        {
            "query": "Who is Dr. Sandesh BJ?",
            "expected_tools": ["SQL"],
            "reason": "Lecturer information is in SQL database"
        },
        {
            "query": "Tell me about Maaya club",
            "expected_tools": ["SQL"], 
            "reason": "Club information is in SQL database"
        },
        {
            "query": "Show me all professors",
            "expected_tools": ["SQL"],
            "reason": "Lecturer roles/positions are in SQL database"
        },
        {
            "query": "Which clubs were founded in 2020?",
            "expected_tools": ["SQL"],
            "reason": "Club founding years are in SQL database"
        },
        
        # Vector Database Queries (Document Content)
        {
            "query": "What subjects are taught in semester 5?",
            "expected_tools": ["VECTOR_SEARCH"],
            "reason": "Curriculum/semester content is in documents"
        },
        {
            "query": "What is the admission process?", 
            "expected_tools": ["VECTOR_SEARCH"],
            "reason": "Admission procedures are in policy documents"
        },
        {
            "query": "Tell me about course objectives for Computer Science",
            "expected_tools": ["VECTOR_SEARCH"],
            "reason": "Course objectives are in curriculum documents"
        },
        {
            "query": "What are the university policies?",
            "expected_tools": ["VECTOR_SEARCH"],
            "reason": "Policies are in document collections"
        },
        
        # Compound Queries (Multiple Tools)
        {
            "query": "Who is Dr. Arti Arya and what subjects are taught in semester 5?",
            "expected_tools": ["SQL", "VECTOR_SEARCH"],
            "reason": "Lecturer info (SQL) + Curriculum info (Vector)"
        },
        {
            "query": "Tell me about the robotics club and the admission process",
            "expected_tools": ["SQL", "VECTOR_SEARCH"], 
            "reason": "Club info (SQL) + Admission process (Vector)"
        }
    ]
    
    print("🧪 INTELLIGENT ROUTING TEST")
    print("="*80)
    
    total_tests = len(test_cases)
    passed_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        expected_tools = test_case["expected_tools"]
        reason = test_case["reason"]
        
        print(f"\n📝 Test {i}/{total_tests}: {query}")
        print(f"   Expected Tools: {expected_tools}")
        print(f"   Reason: {reason}")
        
        # Get the plan from the planner
        plan = planner.process(query)
        actual_tools = [step.get("tool") for step in plan]
        
        print(f"   Generated Plan: {plan}")
        print(f"   Actual Tools: {actual_tools}")
        
        # Check if routing is correct
        tools_match = set(expected_tools) == set(actual_tools)
        
        if tools_match:
            print(f"   ✅ PASS: Correctly routed to {actual_tools}")
            passed_tests += 1
        else:
            print(f"   ❌ FAIL: Expected {expected_tools}, got {actual_tools}")
        
        print(f"   {'-'*60}")
    
    print(f"\n🎯 RESULTS: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("✅ ALL TESTS PASSED - Intelligent routing is working perfectly!")
    else:
        print(f"⚠️  {total_tests - passed_tests} tests failed - Some routing issues detected")
    
    return passed_tests == total_tests

def test_actual_execution():
    """Test actual execution to verify end-to-end functionality"""
    print(f"\n🚀 END-TO-END EXECUTION TEST")
    print("="*80)
    
    # Initialize agents
    db_session = next(get_db())
    vector_store = VectorStore("data/documents/processed")
    
    sql_agent = TextToSQLAgent(db_session)
    retriever_agent = RetrieverAgent(vector_store)
    
    # Test SQL routing
    print("\n1. Testing SQL Agent (Lecturer Query):")
    sql_result = sql_agent.process("Who is Dr. Sandesh BJ?")
    print(f"   Result: {sql_result[:150]}...")
    sql_success = "Dr. Sandesh BJ" in sql_result
    print(f"   ✅ SQL Agent: {'WORKING' if sql_success else 'FAILED'}")
    
    # Test Vector routing  
    print("\n2. Testing Vector Agent (Curriculum Query):")
    vector_chunks = retriever_agent.process("semester 5 subjects computer science")
    vector_result = f"Found {len(vector_chunks)} relevant chunks"
    if vector_chunks:
        vector_result += f", sample: {vector_chunks[0][:100]}..."
    print(f"   Result: {vector_result}")
    vector_success = len(vector_chunks) > 0
    print(f"   ✅ Vector Agent: {'WORKING' if vector_success else 'FAILED'}")
    
    both_working = sql_success and vector_success
    print(f"\n🎯 Overall System: {'✅ FULLY OPERATIONAL' if both_working else '❌ ISSUES DETECTED'}")
    
    return both_working

if __name__ == "__main__":
    print("🔍 TESTING INTELLIGENT QUERY ROUTING SYSTEM")
    print("This test verifies that different query types are routed to the correct data source\n")
    
    routing_success = test_query_routing()
    execution_success = test_actual_execution()
    
    print(f"\n{'='*80}")
    print("📊 FINAL SUMMARY:")
    print(f"   Routing Intelligence: {'✅ WORKING' if routing_success else '❌ FAILED'}")
    print(f"   Execution Capability: {'✅ WORKING' if execution_success else '❌ FAILED'}")
    
    if routing_success and execution_success:
        print(f"\n🎉 SUCCESS: Your VID system is intelligently routing queries!")
        print("   - Lecturer/Club queries → SQL Database")
        print("   - Curriculum/Policy queries → Vector Database") 
        print("   - Compound queries → Both sources as needed")
    else:
        print(f"\n⚠️ ISSUES DETECTED: Some components need attention")
