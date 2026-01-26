"""
Test script for RAG endpoint
Run this from the backend/src directory: python -m routers.test_rag
"""
import asyncio
import httpx
import sys
import time
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

BASE_URL = "http://localhost:8000"

# Test credentials for different roles
TEST_USERS = {
    "partner": {"email": "bob.vance@lawfirm.com", "password": "password123", "role": "PARTNER"},
    "associate": {"email": "jane.doe@lawfirm.com", "password": "password123", "role": "ASSOCIATE"},
    "staff": {"email": "pam.beesly@lawfirm.com", "password": "password123", "role": "STAFF"},
    "client": {"email": "admin@techcorp.com", "password": "password123", "role": "CLIENT"}
}

# Test queries
TEST_QUERIES = [
    "What is the merger purchase price for AI_Startup?",
    "Who are the key employees identified for retention?",
    "What is the patent number in the TechCorp lawsuit?",
    "What is the monthly rent for the Millennium Tower lease?"
]

async def login(client: httpx.AsyncClient, email: str, password: str) -> str:
    """Login and return access token"""
    resp = await client.post(
        f"{BASE_URL}/auth/login",
        data={"username": email, "password": password}
    )
    
    if resp.status_code != 200:
        print(f"❌ Login failed: {resp.status_code}")
        print(f"   Response: {resp.text}")
        return None
    
    token = resp.json().get("access_token")
    return token

async def search(client: httpx.AsyncClient, token: str, query: str) -> dict:
    """Send a search query"""
    resp = await client.post(
        f"{BASE_URL}/search/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": query}
    )
    
    if resp.status_code != 200:
        print(f"❌ Search failed: {resp.status_code}")
        print(f"   Response: {resp.text}")
        return None
    
    return resp.json()

async def test_user_role(user_type: str, user_info: dict):
    """Test RAG for a specific user role"""
    test_start = time.time()
    
    print(f"\n{'='*80}")
    print(f"🧪 Testing as {user_type.upper()} ({user_info['email']})")
    print(f"   Expected Access Level: {user_info['role']}")
    print(f"{'='*80}\n")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Login
        print("Step 1: Logging in...")
        login_start = time.time()
        token = await login(client, user_info['email'], user_info['password'])
        login_time = time.time() - login_start
        
        if not token:
            print("❌ Cannot proceed without login\n")
            return
        print(f"✅ Login successful (token: {token[:30]}...) [{login_time:.3f}s]\n")
        
        # 2. Test first query
        query = TEST_QUERIES[0]
        print(f"Step 2: Asking question...")
        print(f"❓ Query: \"{query}\"")
        
        search_start = time.time()
        result = await search(client, token, query)
        search_time = time.time() - search_start
        
        if not result:
            print("❌ Search failed\n")
            return
        
        # 3. Display results
        total_time = time.time() - test_start
        print(f"\n✅ Response received! [Search: {search_time:.3f}s, Total: {total_time:.3f}s]")
        print(f"\n📝 AI Answer:")
        print(f"{result['ai_answer']}")
        
        print(f"\n📚 Sources ({len(result['sources'])} documents):")
        for i, source in enumerate(result['sources'], 1):
            print(f"   {i}. {source['filename']}")
            print(f"      Sensitivity: {source['sensitivity']}")
            print(f"      Relevance Score: {source['score']:.4f}")
        
        print(f"\n⏱️  Performance Summary:")
        print(f"   Login: {login_time:.3f}s")
        print(f"   RAG Query: {search_time:.3f}s")
        print(f"   Total: {total_time:.3f}s")

async def test_all_roles():
    """Test RAG with all user roles"""
    suite_start = time.time()
    
    print("\n" + "="*80)
    print("🚀 LEXI-RAG SYSTEM TEST")
    print("="*80)
    
    # Test PARTNER role (should see everything)
    await test_user_role("partner", TEST_USERS["partner"])
    
    # Test STAFF role (should see limited documents)
    await test_user_role("staff", TEST_USERS["staff"])
    
    # Test CLIENT role (should see only public documents)
    await test_user_role("client", TEST_USERS["client"])
    
    suite_time = time.time() - suite_start
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETE")
    print(f"⏱️  Total Test Suite Time: {suite_time:.3f}s")
    print("="*80 + "\n")

async def quick_test():
    """Quick test with just one query as PARTNER"""
    test_start = time.time()
    
    print("\n" + "="*80)
    print("🚀 LEXI-RAG QUICK TEST (Partner Role)")
    print("="*80 + "\n")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Login as partner
        print("🔐 Logging in as pam.beesly@lawfirm.com...")
        login_start = time.time()
        token = await login(client, "pam.beesly@lawfirm.com", "password123")
        login_time = time.time() - login_start
        
        if not token:
            print("❌ Login failed. Is the server running?\n")
            return
        print(f"✅ Login successful [{login_time:.3f}s]\n")
        
        # Ask question
        query = "What does the $5,000,000 figure refer to in the documents?"
        print(f"❓ Question: \"{query}\"\n")
        print("⏳ Searching and generating answer...\n")
        
        search_start = time.time()
        result = await search(client, token, query)
        search_time = time.time() - search_start
        
        if not result:
            print("❌ Search failed\n")
            return
        
        total_time = time.time() - test_start
        
        # Display answer
        print("="*80)
        print("🤖 LEXI'S ANSWER:")
        print("="*80)
        print(result['ai_answer'])
        print("\n" + "="*80)
        print(f"📚 SOURCES ({len(result['sources'])} documents):")
        print("="*80)
        for i, source in enumerate(result['sources'], 1):
            print(f"{i}. {source['filename']} [{source['sensitivity']}] (score: {source['score']:.3f})")
        print("="*80)
        print(f"\n⏱️  PERFORMANCE METRICS:")
        print(f"   🔐 Login: {login_time:.3f}s")
        print(f"   🔍 RAG Query (Vector Search + LLM): {search_time:.3f}s")
        print(f"   ⏱️  Total Test Time: {total_time:.3f}s")
        print("="*80 + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        # Run full test with all roles
        asyncio.run(test_all_roles())
    else:
        # Run quick test
        asyncio.run(quick_test())
        print("\n💡 Tip: Run with '--full' flag to test all user roles:")
        print("   python -m routers.test_rag --full\n")
