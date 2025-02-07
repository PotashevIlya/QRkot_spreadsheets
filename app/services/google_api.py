from copy import deepcopy
from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings
from .exceptions import DBDataBiggerThanTableException


DATE_FORMAT = '%Y/%m/%d %H:%M:%S'
ROW_COUNT = 100
COLUMN_COUNT = 11
SPREADSHEET_BODY = dict(
    properties=dict(
        title='',
        locale='ru_RU',
    ),
    sheets=[dict(properties=dict(
        sheetType='GRID',
        sheetId=0,
        title='Лист1',
        gridProperties=dict(
            rowCount=ROW_COUNT,
            columnCount=COLUMN_COUNT,
        )
    ))]
)
TABLE_VALUES = [
    ['Отчёт от', ''],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]
DB_DATA_BIGGER_THAN_TABLE_MESSAGE = (
    'Ошибка при вставке данных\n'
    'Строк в таблице: {table_rows}\n'
    'Строк занимают данные из БД: {db_rows}\n'
    'Столбцов в таблице: {table_cols}\n'
    'Столбцов занимают данные из БД: {db_cols}'
)


async def spreadsheets_create(wrapper_services: Aiogoogle) -> tuple:
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = deepcopy(SPREADSHEET_BODY)
    spreadsheet_body['properties']['title'] = (
        f'Отчёт от {datetime.now().strftime(DATE_FORMAT)}'
    )
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    return response['spreadsheetId'], response['spreadsheetUrl']


async def set_user_permissions(
        spreadsheetid: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheetid,
            json=permissions_body,
            fields="id"
        )
    )


async def spreadsheets_update_value(
        spreadsheet_id: str,
        charity_projects: list,
        wrapper_services: Aiogoogle
) -> None:
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = deepcopy(TABLE_VALUES)
    table_values[0][1] = datetime.now().strftime(DATE_FORMAT)
    table_values = [
        *table_values,
        *[list(map(str, [
            charity_project.name,
            charity_project.close_date - charity_project.create_date,
            charity_project.description]))
            for charity_project in charity_projects
          ]
    ]
    from_db_rows_count = len(table_values)
    from_db_columns_count = len(max(table_values, key=len))
    if from_db_rows_count > ROW_COUNT or from_db_columns_count > COLUMN_COUNT:
        raise DBDataBiggerThanTableException(
            DB_DATA_BIGGER_THAN_TABLE_MESSAGE.format(
                table_rows=ROW_COUNT,
                db_rows=from_db_rows_count,
                table_cols=COLUMN_COUNT,
                db_cols=from_db_columns_count
            )
        )
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{from_db_rows_count}C{from_db_columns_count}',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
