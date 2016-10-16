#!/usr/bin/env python

"""mftdump.py: Display the specified MFT file to standard output."""

from __future__ import print_function

import argparse
import mmap
import os
import struct
import sys

__author__ = "Igor Mironov"
__copyright__ = "Copyright 2016, Igor Mironov"
__license__ = "Apache v2.0"

# Default record size in $MFT file
DEFAULT_RECORD_SIZE = 1024

# Default size of FILE record header up to the update sequence number
RECORD_HEADER_SIZE = 0x30

FILE_RECORD_TYPE = 'FILE'  # the type code of the file record
BAD_RECORD_TYPE = 'BAAD'  # the type of an MFT record that is flagged as 'bad'


class MFTFile(object):
    def __init__(self, file_name, file_data):
        self.file_name = file_name
        self.file_data = file_data
        self.record_size = DEFAULT_RECORD_SIZE

    def dump(self):
        file_size = self.file_data.size()
        record_header_size = RECORD_HEADER_SIZE
        record_number = 0
        record_offset = 0
        column_headings_printed = False
        while record_offset < file_size:
            record_end = record_offset + record_header_size
            record_data = self.file_data[record_offset:record_end]
            (record_type, sequence_number, link_count, attr_offset, file_flags)\
                = struct.unpack('4s12x4H24x', record_data)
            if not valid_record_type(record_type):
                print_error('Record %d has unknown type: %r' %
                            (record_number, record_type))
            if not column_headings_printed:
                print('rec_offset\trecord\ttype\tseq_num\tlinks\tflags')
                print('----------\t------\t----\t-------\t-----\t-----')
                column_headings_printed = True
            print('{:#010x}\t{:d}\t{:s}\t{:d}\t{:d}\t{:#06b}'.format(
                record_offset, record_number, record_type, sequence_number,
                link_count, file_flags))
            record_number += 1
            record_offset += self.record_size


def valid_record_type(record_type):
    return record_type == FILE_RECORD_TYPE or record_type == BAD_RECORD_TYPE


def dump_file(file_name):
    st = os.stat(file_name)
    # Windows cannot mmap empty files so check this case separately
    if not st.st_size:
        print_error('Empty file: %s' % file_name)
        return
    with open(file_name, mode='rb') as in_file:
        file_data = mmap.mmap(in_file.fileno(), 0, access=mmap.ACCESS_READ)
        MFTFile(file_name, file_data).dump()
        file_data.close()


def print_error(error_message):
    print(error_message, file=sys.stderr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Display the specified MFT'
                                                 ' file to standard output.')
    parser.add_argument('file_name', metavar='FILE', help='input file')
    args = parser.parse_args()
    dump_file(args.file_name)
