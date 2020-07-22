import csv
import os
import re


DEFAULT_INPUT_DIR = 'input'
DEFAULT_OUTPUT_DIR = 'output'
DEFAULT_OUTPUT_NAME = 'data_resi.csv'
DEFAULT_LOG_FILE = 'log.txt'
COLUMNS = ['Nama', 'Kota', 'Biaya', 'Resi']

def parse_resi_data_from_file(file_path: str) -> [dict]:
    lines = os.popen('python pdf2txt.py {}'.format(file_path)).read()

    with open(DEFAULT_LOG_FILE, 'w') as f_log:
        f_log.write(lines)

    texts = lines.split('\n')

    kode_resi_regex = re.compile(r'.+:([A-Z]{2}\d{10})')
    berat_regex = re.compile(r'\d+ gr')

    data = []
    one_data = {}
    nama_countdown = 0
    kota_countdown = 0
    harga_countdown = 0
    for text in texts:
        text = text.strip()
        if len(text) == 0:
            continue

        nama_countdown -= 1
        kota_countdown -= 1
        harga_countdown -= 1
        kode_resi = re.match(kode_resi_regex, text)

        if kode_resi:
            one_data['Resi'] = kode_resi.groups(0)[0]
            nama_countdown = 2
        elif 'alkafgrosir' in text.lower():
            kota_countdown = 3
        elif re.match(berat_regex, text):
            harga_countdown = 2
        elif nama_countdown == 0:
            one_data['Nama'] = text
        elif kota_countdown == 0:
            one_data['Kota'] = text
        elif harga_countdown == 0:
            one_data['Biaya'] = text.split('Rp')[-1]

        if len(one_data) == len(COLUMNS):
            data.append(one_data)
            one_data = {}
    return data

def write_to_csv(data: [dict], output_path: str, prefix: str, filename: str) -> None:
    filename = filename.split('.')[0] + '.csv'
    with open(output_path + '/' + prefix + filename, 'w', newline='\n', encoding='utf-8') as f_out:
        data_resi_writer = csv.writer(f_out)
        data_resi_writer.writerow(COLUMNS)
        for one_data in data:
            data_resi_writer.writerow([one_data[key] for key in COLUMNS])
    

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
