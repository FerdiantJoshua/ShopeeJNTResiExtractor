import csv
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import platform
import re

DEFAULT_INPUT_DIR = 'input'
DEFAULT_OUTPUT_DIR = 'output'
DEFAULT_LOG_DIR = 'logs'

DEFAULT_OUTPUT_NAME = 'data_resi.csv'
DEFAULT_LOG_FILE = 'log.txt'
COLUMNS = ['Nama', 'Kota', 'Resi']

os.makedirs(DEFAULT_LOG_DIR, exist_ok=True)

file_logger = logging.getLogger(__name__)
file_logger.level = logging.DEBUG
file_logger.propagate = False
timed_rotating_File_handler = TimedRotatingFileHandler(DEFAULT_LOG_DIR + '/log', when='midnight', backupCount=90, encoding='utf-8')
timed_rotating_File_handler.setLevel(logging.DEBUG)
timed_rotating_File_handler.setFormatter(logging.Formatter('%(message)s'))
file_logger.addHandler(timed_rotating_File_handler)


def parse_resi_data_from_file(file_path: str) -> [dict]:
    python_cmd = 'python' if platform.system() == 'Windows' else 'python3'
    with os.popen('{} pdf2txt.py {}'.format(python_cmd, file_path)) as f_in:
        lines = f_in.read()

    texts = lines.split('\n')

    kode_resi_regex_jnt = re.compile(r'.+:([A-Z]{2}\d{9, 10})')
    kode_resi_regex_anteraja = re.compile(r'.+: ?(\d{14})')
    # berat_regex = re.compile(r'\d+ gr')

    resi_records = []
    resi_record = {}
    nama_countdown = 0
    kota_countdown = 0
    harga_countdown = 0
    for text in texts:
        text = text.strip()
        if len(text) == 0:
            continue

        additional_info = None
        nama_countdown -= 1
        kota_countdown -= 1
        harga_countdown -= 1
        kode_resi = re.match(kode_resi_regex_jnt, text) or re.match(kode_resi_regex_anteraja, text)

        if kode_resi:
            resi_record['Resi'] = kode_resi.groups(0)[0]
            nama_countdown = 2
            additional_info = 'MARK resi. nama_countdown = {}'.format(nama_countdown)
        elif 'alkafgrosir' in text.lower():
            kota_countdown = 3
            additional_info = 'MARK alkafgrosir. kota_countdown = {}'.format(kota_countdown)
        # elif re.match(berat_regex, text):
        #     harga_countdown = 4
        #     additional_info = 'MARK berat. harga_countdown = {}'.format(harga_countdown)
        elif nama_countdown == 0:
            resi_record['Nama'] = text
            additional_info = 'MARK nama'
        elif kota_countdown == 0:
            resi_record['Kota'] = text
            additional_info = 'MARK kota'
        # elif harga_countdown == 0:
        #     resi_record['Biaya'] = text.split('Rp')[-1]
        #     additional_info = 'MARK biaya'

        if len(resi_record) == len(COLUMNS):
            resi_records.append(resi_record)
            additional_info = '' if additional_info is None else additional_info + '; '
            additional_info += 'MARK append record: resi_records = {}'.format(resi_records)
            resi_record = {}

        if additional_info:
            file_logger.debug('%s\t\t=>\t\t%s', text, additional_info)
        else:
            file_logger.debug(text)
    return resi_records


def validate_resi_records(resi_records: [dict]) -> bool:
    if len(resi_records) == 0:
        return False

    for resi_record in resi_records:
        if len(resi_record) != len(COLUMNS):
            return False
    return True


def write_to_csv(resi_records: [dict], output_path: str, prefix: str, filename: str) -> None:
    filename = filename.split('.')[0] + '.csv'
    with open(output_path + '/' + prefix + filename, 'w', newline='\n', encoding='utf-8') as f_out:
        resi_record_writer = csv.writer(f_out)
        resi_record_writer.writerow(COLUMNS)
        for resi_record in resi_records:
            resi_record_writer.writerow([resi_record[key] for key in COLUMNS])
    

def main():
    file_logger.info('========== {} =========='.format(datetime.now().strftime('%A, %d %B %Y at %H:%M:%S')))

    input_path = DEFAULT_INPUT_DIR
    output_path = DEFAULT_OUTPUT_DIR

    count = 0
    for filename in os.walk(input_path).__next__()[-1]:
        file_ = input_path + '/' + filename
        try:
            print('Parsing {}...'.format(file_))
            file_logger.info('---------- {} ----------'.format(file_))
            complete_resi_records = parse_resi_data_from_file(file_)
            is_resi_records_valid = validate_resi_records(complete_resi_records)
            if not is_resi_records_valid:
                print('WARNING: Misparsing probability. Please check {} manually.'.format(file_))
                file_logger.warning('>>>>> INCOMPLETE DATA')
            write_to_csv(complete_resi_records, output_path, 'parsed_', filename)
            count += 1
        except Exception as e:
            print('ERROR: Unable to parse {}, skipping to next file... ({})'.format(file_, e))
            file_logger.error(e, exc_info=True)
            continue
    print('Done! Parsed {} file(s)'.format(count))


if __name__ == '__main__':
    main()
