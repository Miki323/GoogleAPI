from google.oauth2.service_account import Credentials
import gspread
import apiclient.discovery

# Ваш API-ключ должен быть в формате JSON и находиться в той же директории, где находится скрипт.
API_KEY_FILE = 'auth.json'

# Адреса электронной почты пользователей, которым хотим предоставить доступ
USER_EMAILS = ['radkovichsiarhei@gmail.com', 'example@example.com']


def get_google_sheets_client(api_key_file):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(api_key_file, scopes=scope)
    client = gspread.authorize(creds)
    return client


def get_google_drive_service(api_key_file):
    creds = Credentials.from_service_account_file(api_key_file)
    drive_service = apiclient.discovery.build('drive', 'v3', credentials=creds)
    return drive_service


def grant_access_to_users(drive_service, spreadsheet_id, user_emails, role='writer'):
    # Предоставление доступа пользователям
    for email in user_emails:
        drive_service.permissions().create(
            fileId=spreadsheet_id,
            body={'type': 'user', 'role': role, 'emailAddress': email},
            fields='id'
        ).execute()
        print(f"Доступ к таблице предоставлен пользователю с адресом {email}.")


def create_new_sheet(client, sheet_name):
    # Создание новой таблицы в Google Диске
    sheet = client.create(sheet_name)
    return sheet


def list_all_files(drive_service):
    # Получение списка всех файлов в Google Диске
    results = drive_service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
    files = results.get('files', [])
    return files


def get_spreadsheet_by_id(client, spreadsheet_id):
    # Получение таблицы по ее идентификатору
    try:
        return client.open_by_key(spreadsheet_id)
    except gspread.exceptions.SpreadsheetNotFound:
        print("Таблица с указанным идентификатором не найдена.")
        return None


def view_data(sheet):
    # Просмотр данных в таблице
    worksheet = sheet.get_worksheet(0)
    data = worksheet.get_all_values()
    for row in data:
        print(row)


def write_data(sheet, data):
    # Запись данных в таблицу
    worksheet = sheet.get_worksheet(0)
    for row in data:
        worksheet.append_row(row)
    print("Данные успешно добавлены в таблицу.")


def clear_data(sheet):
    # Очистка данных из таблицы
    worksheet = sheet.get_worksheet(0)
    worksheet.clear()
    print("Данные успешно удалены из таблицы.")


def delete_sheet(drive_service, spreadsheet_id):
    drive_service.files().delete(fileId=spreadsheet_id).execute()
    print(f"Таблица с ID {spreadsheet_id} успешно удалена.")


def read_data_from_user():
    data_to_write_str = input('\nВведите данные в формате [["column", "column"], ["column", "column"]]: \n')
    try:
        data_to_write = eval(data_to_write_str)
        if isinstance(data_to_write, list):
            return data_to_write
        else:
            print("Некорректный формат данных.")
            return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None


def write_data_action(sheet):
    data_to_write = read_data_from_user()
    if data_to_write:
        write_data(sheet, data_to_write)
    else:
        print("Некорректные данные. Повторите попытку.")


def main():
    client = get_google_sheets_client(API_KEY_FILE)
    drive_service = get_google_drive_service(API_KEY_FILE)

    actions = {
        "1": lambda: create_new_sheet(client, input("Введите имя новой таблицы: \n")),
        "2": lambda: [print(f"{i}. {file['name']} (Идентификатор: {file['id']}) URL таблицы: https://docs.google.com/spreadsheets/d/{file['id']}'\n") for i, file in enumerate(list_all_files(drive_service), start=1)],
        "3": lambda: select_and_handle_sheet(drive_service, client),
        "0": lambda: None
    }

    while True:
        print("")
        print("Главное меню:")
        print("1. Создать новую таблицу")
        print("2. Просмотреть список доступных таблиц")
        print("3. Выбрать таблицу по номеру")
        print("0. Выход\n")

        choice = input("Введите номер действия: \n")
        if choice in actions:
            if choice == "0":
                break
            actions[choice]()
        else:
            print("Некорректный ввод. Повторите попытку.\n")


def select_and_handle_sheet(drive_service, client):
    files = list_all_files(drive_service)
    for i, file in enumerate(files, start=1):
        print(
            f"{i}. {file['name']} (Идентификатор: {file['id']}) URL таблицы: https://docs.google.com/spreadsheets/d/{file['id']}'\n")

    while True:
        choice = input("Введите номер таблицы, которую хотите использовать: \n")
        if not choice.isnumeric():
            print("Пожалуйста, введите число.\n")
            continue

        choice = int(choice)
        if 1 <= choice <= len(files):
            break
        else:
            print("Нет такого номера таблицы. Повторите попытку.\n")

    selected_file = files[choice - 1]
    spreadsheet_id = selected_file.get('id')
    name = selected_file.get('name')
    sheet = get_spreadsheet_by_id(client, spreadsheet_id)
    if not sheet:
        print("Таблица не найдена.\n")
        return
    while True:
        print(
            f"{name} (Идентификатор: {spreadsheet_id}) URL таблицы: https://docs.google.com/spreadsheets/d/{spreadsheet_id}'\n")
        print("1. Записать данные в выбранную таблицу")
        print("2. Просмотреть данные выбранной таблицы")
        print("3. Очистить данные выбранной таблицы")
        print("4. Удалить выбранную таблицу")
        print("5. Предоставить доступ к таблице")
        print("0. Вернуться в главное меню\n")

        choice = input("Введите номер действия: \n")
        try:
            if choice == "1":
                write_data_action(sheet)
            elif choice == "2":
                view_data(sheet)
            elif choice == "3":
                clear_data(sheet)
            elif choice == "4":
                delete_sheet(drive_service, spreadsheet_id)
            elif choice == "5":
                grant_access_to_users(drive_service, spreadsheet_id, USER_EMAILS)
            elif choice == "0":
                break
            else:
                print("Некорректный ввод. Повторите попытку.\n")
        except Exception as e:
            print(e)
            break


if __name__ == '__main__':
    main()
