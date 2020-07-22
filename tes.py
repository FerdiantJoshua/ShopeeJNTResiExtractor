import copy
import re
import sys
import os

DEFAULT_LOG_FILE = 'log.txt'
COLUMNS = ['Nama', 'Kota', 'Biaya', 'Resi']

filename = sys.argv[1]

def parse_resi_data_from_file(filename: str) -> list:
    lines = os.popen('python pdf2txt.py input/{}'.format(filename)).read()

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
            one_data['Harga'] = text.split('Rp')[-1]

        if len(one_data) == len(COLUMNS):
            data.append(one_data)
            one_data = {}
    return data

print(parse_resi_data_from_file(filename))
