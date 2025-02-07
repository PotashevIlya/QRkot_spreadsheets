from copy import deepcopy
from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings


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
    if (len(table_values) > ROW_COUNT or
            len(max(table_values, key=len)) > COLUMN_COUNT):
        raise IndexError()
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=(
                f'R1C1:R{len(table_values)}C{len(max(table_values, key=len))}'
            ),
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
