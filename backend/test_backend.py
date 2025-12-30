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
            "name": "Typosquat PayPal (Homoglyph)",
            "data": {
                "url": "http://p4ypal.xyz",
                "title": "PayPal Security",
                "text": "Login to your account",
                "localScore": 25,
                "localReasons": ["Suspicious TLD"]
            }
        },
        {
            "name": "Lookalike K-Bank (1-char diff)",
            "data": {
                "url": "http://k-bank.net",
                "title": "KBank Online",
                "text": "ยืนยันตัวตน",
                "localScore": 30,
                "localReasons": ["Thai keywords detected"]
            }
        },
        {
            "name": "Lookalike Shopee (Similarity)",
            "data": {
                "url": "http://shopee-sale.com",
                "title": "Shopee Mall",
                "text": "Special discount for you",
                "localScore": 20,
                "localReasons": ["Login form detected"]
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
