import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Важливо: додаємо Drive для копіювання файлів і Documents для редагування
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

def get_creds():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            # Використовуємо open_browser=False для WSL
            creds = flow.run_local_server(port=0, open_browser=False)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

if __name__ == "__main__":
    get_creds()
    print("✅ Авторизація успішна! Токен збережено.")