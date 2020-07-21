import json


def remove_dict_items(dictionary, key_list):
    list(map(dictionary.pop, key_list))
    return dictionary


def clean_duplicate_2d(arr2d):
    return list(set(map(tuple, arr2d)))


def write_json(filename, dictionary):
    with open(filename, '+w', encoding='utf-8') as f:
        json.dump(dictionary, f, indent=4, ensure_ascii=False)


def json2sell_buy(file_list):
    stock_json = {}
    FILE_NAME_FLAG = 0
    for file in file_list:
        with open(f'data/{file}', '+r', encoding='utf-8') as f:
            _stock_json = json.load(f)
            order_type = file.split('.')[FILE_NAME_FLAG]
            stock_json[order_type] = _stock_json
    return stock_json


def extract_digits_from_string(strings):
    return "".join([s for s in strings if s.isdigit()])


def clean_price_value(string):
    return string.replace(",", "")


def get_selected_table_row(table_name):
    return [x.text() for x in table_name.selectedItems()]


def get_table_header(table_name):
    n_columns = table_name.columnCount()
    return [table_name.horizontalHeaderItem(idx).text() for idx in range(n_columns)]


def table_row2dict(table_name):
    row = get_selected_table_row(table_name)
    header = get_table_header(table_name)

    if len(row) != len(header):
        return False
    else:
        return dict(zip(header, row))


def id_equal(first_id, second_id):
    if id(first_id) == id(second_id):
        return True
    else:
        return False


def empty_check(var):
    if not var:
        return True
