# -*- coding: utf-8 -*-
#!python3

import os
from collections.abc import MutableSequence
import sys
import logging
import hashlib
from collections import OrderedDict, namedtuple
from .BEncoding import BEncoding_decode, BEncoding_encode

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(filename)s %(funcName)s %(lineno)d: %(message)s")

SingleFile = namedtuple("SingleFile", ["path", "filename", "length"])

class Torrent:
    def __init__(self, filename=None):
        self._filename = filename
        self._single = False
        self._valid = False
        self._announce_list = []
        self._torrent_name = ""
        self._piece = b""
        self._piece_length = -1
        self._file_list = []
        self._info_hash = None

    def __repr__(self):
        class_name = type(self).__name__
        hash_hex = self._info_hash.hexdigest() if self._info_hash else None
        return "{}({!r}, {!r})".format(class_name,
                                       self._torrent_name,
                                       hash_hex)

    def __str__(self):
        return str(self._torrent_name)

    def __eq__(self, other):
        return self._info_hash.hexdigest() == other.info_hash.hexdigest()

    def __hash__(self):
        return hash(self._info_hash)

    def __bool__(self):
        return self._valid

    def parse(self):
        self._valid = False
        if not isinstance(self._filename, str):
            logging.error("torrent filename is invalid: %r" % self._filename)
            return False
        if not os.path.exists(self._filename):
            logging.error("torrent file does not exist: %r" % self._filename)
            return False

        _f_in = open(self._filename, "rb")
        self._raw_data = _f_in.read()
        _f_in.close()
        self._torrent_content = BEncoding_decode(self._raw_data)
        #torrent file is a dict
        if not isinstance(self._torrent_content, OrderedDict):
            logging.error("torrent content is invalid")
            return False
        #parse announce
        self._announce_list = []
        self._announce_list.append(self._torrent_content.setdefault("announce"))
        _l = self._torrent_content.setdefault("announce-list", [])
        for _al in _l:
            if isinstance(_al, MutableSequence):
                for _a in _al:
                    self._announce_list.append(_a)
            else:
                self._announce_list.append(_al)

        if None in self._announce_list : self._announce_list.remove(None)
        #get hash of info dict
        self._info_dict = self._torrent_content.setdefault("info", OrderedDict())
        self._info_hash = hashlib.sha1(BEncoding_encode(self._info_dict))
        #get detailed content from hash dict
        return self._do_parse_info()

    def _do_parse_info(self):
        self._torrent_name = self._info_dict.setdefault("name", b"").decode()
        self._piece_length = self._info_dict.setdefault("piece length", 0)
        self._piece = self._info_dict.setdefault("pieces", b"")
        self._file_list = []
        if "length" in self._info_dict:
            self._single = True
            self._file_list.append(SingleFile([], self._torrent_name,
                                              self._info_dict["length"]))
        elif "files" in self._info_dict:
            self._single = False
            _files = self._info_dict["files"]
            for each_file in _files:
                self._file_list.append(SingleFile([x.decode() for x in each_file["path"][:-1]],
                                                  each_file["path"][-1].decode(),
                                                  each_file["length"]))
        else:
            return False

        self._valid = True
        return True

    @property
    def single(self):
        return self._single

    @property
    def valid(self):
        return self._valid

    @property
    def announce_list(self):
        return self._announce_list

    @property
    def torrent_name(self):
        return self._torrent_name

    @property
    def piece(self):
        return self._piece

    @property
    def piece_length(self):
        return self._piece_length

    @property
    def file_list(self):
        return self._file_list

    @property
    def info_hash(self):
        return self._info_hash


if __name__ == "__main__":
    torrent = Torrent("1.torrent")
    torrent.parse()
    torrent2 = Torrent("4.torrent")
    torrent2.parse()
    torrent3 = Torrent("1.torrent")
    torrent3.parse()

    print(torrent._torrent_content)
    print(torrent == torrent2)
    print(torrent == torrent3)

    print(torrent.valid)
    print(torrent.single)
    print(torrent.torrent_name)
    print(torrent.announce_list)
#    print(torrent.get_piece())
    print(torrent.piece_length)
    print(torrent.file_list)
    print(torrent.info_hash.hexdigest())
