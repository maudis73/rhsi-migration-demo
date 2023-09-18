import requests
import time

def greet_api(name):
    url = "http://localhost:6000/api/greet"
    params = {"name": name}

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data['message']
        else:
            return f"Failed to get response. Status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to send request. {e}")


if __name__ == "__main__":
    i = 1
    while True:
        name = str(i)
        try:
            greeting = greet_api(name)
            print(greeting)
        except ConnectionError as e:
            print(f"Connection error for '{name}'. Retrying...")
            time.sleep(1)  # Wait for 1 second before retrying
            continue
        else:
            i +=  1
        time.sleep(1)  # Wait for 1 second before sending the next request


