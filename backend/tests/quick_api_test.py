"""Quick test of API endpoint"""

import json

import requests

try:
    # Test course endpoint
    response = requests.get("http://127.0.0.1:8000/api/courses", timeout=10)
    print("Status Code:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        print("Courses:", json.dumps(data, indent=2))

        # Test query endpoint
        query_response = requests.post(
            "http://127.0.0.1:8000/api/query",
            json={"query": "What is RAG?", "session_id": None},
            timeout=30,
        )

        print("\nQuery Status:", query_response.status_code)

        if query_response.status_code == 200:
            query_data = query_response.json()
            print("Answer:", query_data.get("answer", "No answer")[:200])
            print("Sources:", len(query_data.get("sources", [])))
        else:
            print("Query Error:", query_response.text)
    else:
        print("Error:", response.text)

except Exception as e:
    print("Exception:", str(e))
