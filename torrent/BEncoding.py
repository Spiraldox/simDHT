# -*- coding: utf-8 -*-
#!python3

from collections import OrderedDict
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(filename)s %(funcName)s %(lineno)d: %(message)s")

def _parse_int(data, index):
    bin_num = ""
    while data[index] != ord(b'e'):
        if data[index] >= ord(b'0') and data[index] <= ord(b'9'):
            bin_num += chr(data[index])
        else:
            logging.error("bad char to decode for integer in data: %d" % data[index])
            return None, index
        index += 1
    return int(bin_num), index+1

def _parse_str(data, index):
    bin_num = ""
    while data[index] != ord(b':'):
        if data[index] >= ord(b'0') and data[index] <= ord(b'9'):
            bin_num += chr(data[index])
        else:
            logging.error("bad char to decode for string in data: %r" % data[index])
            return None, index
        index += 1
    begin = index+1
    end = begin+int(bin_num)
    ret = data[begin:end]
    return ret, end

def _parse_list(data, index):
    ret = []
    while data[index] != ord(b'e'):
        ele, index = _do_BEncoding_decode(data, index)
        if ele is None:
            return None, index
        ret.append(ele)
    return ret, index+1

def _parse_dict(data, index):
    ret = {}
    while data[index] != ord(b'e'):
        _key, index = _parse_str(data, index)
        if _key is None:
            return None, index
        ele, index = _do_BEncoding_decode(data, index)
        ret[_key.decode()] = ele
    return ret, index+1

def _do_BEncoding_decode(data, index):
    ret = None
    if data[index] == ord(b'l'):
        ret, index = _parse_list(data, index+1)
    elif data[index] == ord(b'd'):
        ret, index = _parse_dict(data, index+1)
    elif data[index] == ord(b'i'):
        ret, index = _parse_int(data, index+1)
    elif data[index] <= ord(b'9') and data[index] >= ord(b'0'):
        ret, index = _parse_str(data, index)
    else:
        logging.error("bad char to decode in data: %r" % data[index])
        print(data)
    return ret, index

def BEncoding_decode(data):
    if not isinstance(data, bytes):
        logging.error("decoded data must be bytes")
        return None
    return _do_BEncoding_decode(data, 0)[0]

def _encode_str(data):
    ret = "%d:" % len(data)
    if isinstance(data, str):
        data = data.encode()
    elif not isinstance(data, bytes):
        return None
    ret = ret.encode() + data
    return ret

def _encode_int(data):
    ret = "i%se" % str(data)
    return ret.encode()

def _encode_dict(data):
    ret = b"d"
    for _k, _v in data.items():
        if (not isinstance(_k, str)) and \
        (not isinstance(_k, bytes)):
            logging.error("dict key is not str: %r" % _k)
            return None

        k = _encode_str(_k)
        v = _do_BEncoding_encode(_v)
        if v is None:
            logging.error("dict value is illegal: %r" % _v)
            return None
        ret += k + v
    ret += b"e"
    return ret

def _encode_list(data):
    ret = b"l"
    for _i in data:
        i = _do_BEncoding_encode(_i)
        if i is None:
            logging.error("element is illegal: %r" % _i)
            return None
        ret += i
    ret += b"e"
    return ret

def _do_BEncoding_encode(data):
    if isinstance(data, dict):
        return _encode_dict(data)
    elif isinstance(data, list):
        return _encode_list(data)
    elif isinstance(data, str) or isinstance(data, bytes):
        return _encode_str(data)
    elif isinstance(data, int):
        return _encode_int(data)
    else:
        return None

def BEncoding_encode(data):
    return _do_BEncoding_encode(data)

if __name__ == "__main__":
    f_in = open("b.torrent", "rb")
    _data = f_in.read()
    f_in.close()
    _ele = BEncoding_decode(_data)
    _data_out = BEncoding_encode(_ele)
    print(_data == _data_out)
    print(_ele)
