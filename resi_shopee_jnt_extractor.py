import csv
import os
import re

import fitz


DEFAULT_INPUT_DIR = 'input'
DEFAULT_OUTPUT_DIR = 'output'
DEFAULT_OUTPUT_NAME = 'data_resi.csv'
DEFAULT_LOG_FILE = 'log.txt'
COLUMNS = ['Nama', 'Kota', 'Biaya', 'Resi']

def parse_resi_data_from_file(filename: str) -> list:
    f_log = open(DEFAULT_LOG_FILE, 'w')

    texts = []
    doc = fitz.open(filename)
    for page in doc:
        text = page.getText()
        texts.append(text.split('\n'))

    kode_resi_regex = r'([A-Z]{3}-)?([A-Z]{3})[0-9]{3}'
    kode_pos_regex = r'[0-9]{5}'

    data = []
    for text in texts:
        nama_countdown = 0
        kota_countdown = 0
        harga_countdown = 0
        resi_countdown = 0
        datum = []
        for i in range(len(text)):
            print(text[i], file=f_log)
            nama_countdown -= 1
            kota_countdown -= 1
            harga_countdown -= 1
            resi_countdown -= 1
            if nama_countdown == 0:
                datum.append(text[i].strip())
            elif kota_countdown == 0:
                j = 0
                kota = ''
                found_correct_kode_pos = False
                while not found_correct_kode_pos:
                    while not re.match(kode_pos_regex, text[i+j]):
                        kota += ' ' + text[i+j]
                        j += 1
                    if len(kota.split(',')) < 2:
                        print(f'Mis-parsing possibility. Please check {datum[0]} manually..')
                        j += 1
                    else:
                        kota = kota.split(',')[-2].strip()
                        found_correct_kode_pos = True
                datum.append(kota)
            elif harga_countdown == 0:
                datum.append(text[i].split('Rp ')[-1].strip())
            elif resi_countdown == 0:
                datum.append(text[i].strip())
                data.append(datum.copy())
                datum = []
            elif re.match(kode_resi_regex, text[i]):
                nama_countdown = 1
                kota_countdown = 3
            elif text[i] == 'Biaya':
                harga_countdown = 1
            elif text[i] == 'Daftar Produk':
                resi_countdown = 7

    f_log.close()
    return data

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
    for filename in os.walk(input_path).__next__()[-1]:
        file_ = input_path + '/' + filename
        try:
            print('Parsing {}...'.format(file_))
            complete_resi_data = parse_resi_data_from_file(file_)
            write_to_csv(complete_resi_data, output_path, 'parsed_', filename)
            count += 1
        except Exception as e:
            print('Unable to parse {}, skipping to next file...'.format(file_))
            continue
    print('Done! Parsed {} file(s)'.format(count))
    
if __name__ == '__main__':
    main()
