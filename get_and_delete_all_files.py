from google.oauth2.service_account import Credentials
import googleapiclient.discovery
from config import API_KEY_FILE


# Функция для получения доступа к Google Drive API
def get_google_drive_service(api_key_file):
    creds = Credentials.from_service_account_file(api_key_file, scopes=['https://www.googleapis.com/auth/drive'])
    service = googleapiclient.discovery.build('drive', 'v3', credentials=creds)
    return service


# Функция для получения списка всех файлов в Google Диске
def list_all_files(service):
    results = service.files().list().execute()
    files = results.get('files', [])
    return files


# Функция для удаления файла по его идентификатору
def delete_file(service, file_id):
    service.files().delete(fileId=file_id).execute()


def main():
    # Получение доступа к Google Drive API
    drive_service = get_google_drive_service(API_KEY_FILE)

    # Получение списка всех файлов в Google Диске
    files = list_all_files(drive_service)

    if not files:
        print("Нет файлов в Google Диске.")
    else:
        print("Список всех файлов в Google Диске:")
        for file in files:
            print(f"Имя файла: {file['name']}, Идентификатор: {file['id']}")
            # Удаление файла (раскомментируйте строку ниже, если вы хотите удалить файлы)
            # delete_file(drive_service, file['id'])


if __name__ == '__main__':
    main()
