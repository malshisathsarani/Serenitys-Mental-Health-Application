"""Test registration endpoint to debug 400 error"""
import httpx
import json
import asyncio

async def test_registration():
    """Test the registration endpoint"""
    async with httpx.AsyncClient() as client:
        test_data = {
            "username": "testuser",
            "email": "test@gmail.com",
            "password": "Passw9rd9",  # 9 chars, uppercase + digit
            "full_name": "Test User"
        }
        
        try:
            print("[SEND] Sending registration request...")
            print(f"Data: {json.dumps(test_data, indent=2)}")
            
            response = await client.post(
                "http://localhost:8001/api/auth/register",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"\n[RESPONSE] Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"Body: {response.text}")
            
            if response.status_code != 200:
                print(f"\n[ERROR] Error Response:")
                try:
                    error_detail = response.json()
                    print(json.dumps(error_detail, indent=2))
                except:
                    print(response.text)
            else:
                print(f"\n[SUCCESS] Registration successful!")
                
        except Exception as e:
            print(f"[EXCEPTION] {e}")

if __name__ == "__main__":
    asyncio.run(test_registration())
