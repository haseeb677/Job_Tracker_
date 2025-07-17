import requests

def search_jobs(query, location="", skills=""):
    url = "https://jsearch.p.rapidapi.com/search"

    headers = {
        "X-RapidAPI-Key": "1b9814f49emsh4b9960259691c2bp13eee4jsn38c82952b3a9",  # 🔑 Replace this with your actual RapidAPI key
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    params = {
        "query": f"{query} {skills}",
        "location": location,
        "page": "1",
        "num_pages": "1"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])  # ✅ Extract the jobs list
        else:
            print(f"API error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception during job search: {e}")
        return []
