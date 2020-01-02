import copy
import re
import sys

import fitz

filename = sys.argv[1]

texts = []
doc = fitz.open(f'input/{filename}')
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
        nama_countdown -= 1
        kota_countdown -= 1
        harga_countdown -= 1
        resi_countdown -= 1
        if nama_countdown == 0:
            datum.append(text[i].strip())
        elif kota_countdown == 0:
            j = 0
            kota = ''
            while not re.match(kode_pos_regex, text[i+j]):
                kota += f' {text[i+j]}'
                j += 1
            kota = kota.split(',')[-2].strip()
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

print(data)

with open('output/test.txt', 'w') as f_out:
    for text in texts:
        for line in text:
            f_out.writelines(f'{line}\n')
