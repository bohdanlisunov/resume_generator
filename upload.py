import os
import pickle
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv()
FOLDER_ID = os.getenv("FOLDER_ID")
TEMPLATE_ID = os.getenv("TEMPLATE_ID") # Додай ID шаблону в .env

def get_creds():
    if not os.path.exists("token.pickle"):
        raise Exception("❌ token.pickle не знайдено! Запусти скрипт авторизації.")
    with open("token.pickle", "rb") as f:
        creds = pickle.load(f)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open("token.pickle", "wb") as f:
                pickle.dump(creds, f)
    return creds

def update_document_content(doc_id, parsed_data):
    """Замінює плейсхолдери {{KEY}} на реальний текст"""
    docs_service = build("docs", "v1", credentials=get_creds())
    
    requests = []
    for key, value in parsed_data.items():
        requests.append({
            'replaceAllText': {
                'containsText': {
                    'text': '{{' + key + '}}',
                    'matchCase': True
                },
                'replaceText': value
            }
        })

    if requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id, 
            body={'requests': requests}
        ).execute()

def create_from_template(title, parsed):
    drive_service = build("drive", "v3", credentials=get_creds())
    
    # 1. Копіюємо шаблон у потрібну папку
    copy_metadata = {
        "name": f"Resume — {title}",
        "parents": [FOLDER_ID]
    }
    
    new_file = drive_service.files().copy(
        fileId=TEMPLATE_ID, 
        body=copy_metadata
    ).execute()
    
    new_doc_id = new_file.get('id')

    # 2. Заповнюємо копію даними
    update_document_content(new_doc_id, parsed)
    
    print(f"✅ Готово: Resume — {title}")
    print(f"🔗 https://docs.google.com/document/d/{new_doc_id}/edit")

# Твій парсер залишається майже таким самим, 
# але переконайся, що ключі в parsed збігаються з {{TAGS}} у доці.