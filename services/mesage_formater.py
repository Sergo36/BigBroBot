from datetime import datetime

import peewee


def table_message(data: peewee.ModelNamedTupleCursorWrapper, start: int, end: int):
    if data.count == 0:
        return "Нет данных"
    body = []
    stop = min(len(data), end)
    for index in range(start, stop):
        string_data = []
        for i in range(len(data[index])):
            if type(data[index][i]) == datetime:
                string_data.append(data[index][i].strftime("%d.%m.%-y %H:%M:%S"))
                continue
            string_data.append(str(data[index][i]))
        body.append(string_data)

    header =[]
    for i in range(len(data.columns)):
        header.append(data.columns[i])

    table = [header]
    table.extend(body)


    column_width = get_column_width(table, len(data.columns))
    return get_table(table, column_width)


def get_column_width(data, count):
    res = []
    for col in range(count):
        width = 0
        for row in range(len(data)):
            if width < len(data[row][col]):
                width = len(data[row][col])
        res.append(width)
    return res


def get_table(table, column_width):
    res = []
    for row in table:
        for i in range(len(row)):
            dif = column_width[i] - len(row[i])
            if dif != 0:
                row[i] = row[i] + ' ' * dif
        res.append('|'.join(row))
    return "\n".join(res)
