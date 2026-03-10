import os
import sys
import time
import random
import pickle
import re
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from src.playwright_bot import ChatGPTBot
from src.generator import load_vacancies, build_prompt, parse_response

load_dotenv()

# --- Конфігурація Google ---
TEMPLATE_ID = os.getenv("TEMPLATE_ID")
FOLDER_ID = os.getenv("FOLDER_ID")

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_google_creds():
    """Отримує або оновлює токен доступу Google"""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
            print("🔄 Google токен автоматично оновлено.")
        except Exception as e:
            print(f"❌ Не вдалося оновити токен: {e}")
            return None
    return creds

def format_as_bullets(docs_service, document_id):
    """Знаходить рядки, що починаються з '-', і перетворює їх на марковані списки"""
    doc = docs_service.documents().get(documentId=document_id).execute()
    content = doc.get('body').get('content')
    
    requests = []
    for element in content:
        if 'paragraph' in element:
            paragraph = element.get('paragraph')
            text_elements = paragraph.get('elements')
            full_paragraph_text = "".join([el.get('textRun', {}).get('content', '') for el in text_elements])
            
            if full_paragraph_text.strip().startswith('-'):
                start_index = element.get('startIndex')
                end_index = element.get('endIndex')
                
                requests.append({
                    'createBullet': {
                        'range': {'startIndex': start_index, 'endIndex': end_index},
                        'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
                    }
                })
                requests.append({
                    'deleteContentRange': {
                        'range': {'startIndex': start_index, 'endIndex': start_index + 2}
                    }
                })

    if requests:
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

def apply_formatting(docs_service, document_id):
    """Шукає **текст** у документі, робить його жирним та видаляє зірочки"""
    doc = docs_service.documents().get(documentId=document_id).execute()
    content = doc.get('body').get('content')
    
    full_text = ""
    for element in content:
        if 'paragraph' in element:
            for run in element.get('paragraph').get('elements'):
                full_text += run.get('textRun', {}).get('content', '')

    pattern = re.compile(r'\*\*(.*?)\*\*')
    matches = list(pattern.finditer(full_text))
    
    if not matches:
        return

    formatting_requests = []
    for match in reversed(matches):
        start, end = match.span()
        formatting_requests.append({
            'updateTextStyle': {
                'range': {'startIndex': start, 'endIndex': end},
                'textStyle': {'bold': True},
                'fields': 'bold'
            }
        })
        formatting_requests.append({'deleteContentRange': {'range': {'startIndex': end - 2, 'endIndex': end}}})
        formatting_requests.append({'deleteContentRange': {'range': {'startIndex': start, 'endIndex': start + 2}}})

    if formatting_requests:
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': formatting_requests}).execute()

def clean_unused_placeholders(docs_service, document_id):
    """Видаляє всі теги {{...}}, які залишилися порожніми"""
    requests = [{
        'replaceAllText': {
            'containsText': {'text': r'\{\{.*?\}\}', 'matchCase': False},
            'replaceText': '' 
        }
    }]
    docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

def upload_to_google_docs(title: str, parsed: dict):
    creds = get_google_creds()
    if not creds: return

    drive_service = build("drive", "v3", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)

    try:
        safe_title = title.replace('/', '_').replace('\\', '_')
        copy_metadata = {'name': f"CV_Bohdan_{safe_title}", 'parents': [FOLDER_ID]}
        new_file = drive_service.files().copy(fileId=TEMPLATE_ID, body=copy_metadata).execute()
        doc_id = new_file.get('id')

        requests = []
        for key, value in parsed.items():
            if value:
                clean_key = key.upper()
                
                if "BULLETS" in clean_key:
                    lines = [line.strip() for line in value.split('\n') if line.strip()]
                    final_text = '\n'.join(lines)
                elif clean_key == "TITLE":
                    final_text = value
                elif "JOB_TITLE_" in clean_key:
                    final_text = value.upper()
                else:
                    final_text = value
                
                requests.append({
                    'replaceAllText': {
                        'containsText': {'text': '{{' + key + '}}', 'matchCase': True},
                        'replaceText': final_text
                    }
                })

        if requests:
            docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

        time.sleep(2)

        clean_unused_placeholders(docs_service, doc_id)
        format_as_bullets(docs_service, doc_id)
        apply_formatting(docs_service, doc_id)
        
        print(f"✨ CV Створено: https://docs.google.com/document/d/{doc_id}")
        
    except Exception as e:
        print(f"❌ Помилка Google API: {e}")

def main():

    # 🔹 ВИБІР JSON ФАЙЛУ
    vacancies_file = sys.argv[1] if len(sys.argv) > 1 else "vacancies.json"

    print(f"📄 Використовується файл вакансій: {vacancies_file}")

    vacancies = load_vacancies(vacancies_file)
    bot = ChatGPTBot()
    
    print(f"🚀 Запуск генерації для {len(vacancies)} вакансій...\n")

    try:
        for i, vacancy in enumerate(vacancies):
            job_title = vacancy.get('title', 'Position')
            print(f"⏳ ({i+1}/{len(vacancies)}) Працюю над: {job_title}")
            
            bot.send_prompt(build_prompt(vacancy))
            
            print("   ⏳ ChatGPT генерує відповідь...")
            for _ in range(180):
                time.sleep(1)
                if bot.page.locator("button[aria-label='Stop streaming']").count() == 0:
                    break
            
            response = bot.get_response()
            if not response:
                continue

            parsed = parse_response(response)
            upload_to_google_docs(job_title, parsed)

            if i < len(vacancies) - 1:
                wait = random.uniform(20, 35)
                print(f"⏸ Пауза {wait:.1f} сек...\n")
                time.sleep(wait)
                
    except Exception as e:
        print(f"🔥 Критична помилка: {e}")
    finally:
        bot.close()
        print("\n🎉 Процес завершено!")

if __name__ == "__main__":
    main()