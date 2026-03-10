import os.path
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Дозволи для редагування Документів та копіювання файлів у Драйві
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            # Цей рядок виведе посилання в консоль замість відкриття браузера
            creds = flow.run_local_server(port=0, open_browser=False)
            
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        print("✅ Токен успішно створено та збережено в token.pickle")

if __name__ == '__main__':
    main()