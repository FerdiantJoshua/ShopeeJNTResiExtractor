import csv
import os

from bs4 import BeautifulSoup


DEFAULT_INPUT_DIR = 'input'
DEFAULT_OUTPUT_DIR = 'output'
DEFAULT_OUTPUT_NAME = 'data_resi.csv'
COLUMNS = ['Nama', 'Kota', 'Biaya', 'Resi']

def is_div(name: str) -> bool:
    return name == 'div'

def parse_resi_data_from_file(filename: str) -> list:
    with open(filename, 'r') as f_in:
        soup = BeautifulSoup(f_in, 'lxml')

    complete_resi_data = []

    i = 0
    for object in soup.body.div.contents:
        if not is_div(object.name) or object.div is None:
            continue
        # print(i)
        i += 1
        resi = object.div
        header = resi.div
        barcode_text = header.find_all('div', class_='barcode-text')[0].string
        content = header.next_sibling.next_sibling
        data = content.find_all('div', class_=['data-name', 'data-address-city', 'data-total-fee'])
        name = data[0].contents[0]
        city = data[1].string
        total_fee = data[3].string.replace('Total Biaya: Rp', '').replace('.','')
        complete_resi_data.append([name, city, total_fee, barcode_text])
        # print(complete_resi_data)
        # print()

    return complete_resi_data

def write_to_csv(data: list, output_path: str, prefix: str, filename: str) -> None:
    filename = filename.split('.')[0] + '.csv'
    with open(output_path + '/' + prefix + filename, 'w') as f_out:
        data_resi_writer = csv.writer(f_out)
        data_resi_writer.writerow(COLUMNS)
        for data in data:
            data_resi_writer.writerow(data)
    

def main():
    input_path = DEFAULT_INPUT_DIR
    output_path = DEFAULT_OUTPUT_DIR

    count = 0
    for filename in os.listdir(input_path):
        file_ = input_path + '/' + filename
        try:
            print('Parsing {}...'.format(file_))
            complete_resi_data = parse_resi_data_from_file(file_)
            write_to_csv(complete_resi_data, output_path, 'parsed_', filename)
            count += 1
        except Exception as e:
            print('Unable to parse {}, skipping to next file...'.format(file_))
            print(e)
            continue
    print('Done! Parsed {} file(s)'.format(count))
    
if __name__ == '__main__':
    main()
