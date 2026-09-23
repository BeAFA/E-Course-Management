import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]

# Đọc file Test_User.txt ngay trong thư mục credentials cùng cấp
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "credentials", "Test_User.txt")

config = {}
with open(TOKEN_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        config[key.strip()] = value.strip()

client_config = {
    "installed": {
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost:8080/"]
    }
}

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
creds = flow.run_local_server(port=8080, access_type='offline   ', prompt='consent')

print("\n" + "=" * 60)
print("REFRESH TOKEN MỚI CỦA BẠN LÀ:")
print(creds.refresh_token)
print("=" * 60 + "\n")