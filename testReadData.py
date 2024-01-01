import httpx
import base64

access_token = "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"
username = "Nusab19"
repo = "data"
filename = "push.py"
branch = "main"

client = httpx.Client(headers={"Authorization": f"Bearer {access_token}"})

response = client.get(f"https://api.github.com/repos/{username}/{repo}/contents/{filename}?ref={branch}")

if response.status_code == 200:
    content = response.json()["content"]
    decoded_content = base64.b64decode(content).decode("utf-8")
    print(decoded_content)
else:
    print(f"Error: {response.status_code} - {response.text}")

client.close()