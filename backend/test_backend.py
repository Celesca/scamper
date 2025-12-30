import requests

def test_api():
    url = "http://localhost:5000/analyze"
    
    test_cases = [
        {
            "name": "Safe Google",
            "data": {
                "url": "https://www.google.com",
                "title": "Google",
                "text": "Search the world's information, including webpages, images, videos and more."
            }
        },
        {
            "name": "Phishing PayPal",
            "data": {
                "url": "http://pay-pal-security-update.xyz/login",
                "title": "PayPal: Log In",
                "text": "Please login to verify your account and update your billing information immediately."
            }
        },
        {
            "name": "Suspicious Bank",
            "data": {
                "url": "http://my-bank-login.com",
                "title": "Secure Login",
                "text": "Welcome to your bank. Please enter your credentials to continue."
            }
        }
    ]

    for case in test_cases:
        print(f"Testing: {case['name']}")
        try:
            response = requests.post(url, json=case['data'])
            print(f"Result: {response.json()}\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    test_api()
