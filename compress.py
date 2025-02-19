import argparse

"""
def flush():
  global rle_count
  global rle_byte
  global raw_bytes
  global prev_byte
  global out_f
  if len(raw_bytes) > 1:
    if raw_bytes[-1] == rle_byte:
      rle_count = rle_count + 1
      raw_bytes= raw_bytes[:-1]
  if len(raw_bytes) > 0:
    bytes = [len(raw_bytes) - 1]
    out_f.write(bytearray(bytes))
    out_f.write(bytearray(raw_bytes))
  raw_bytes.clear()
  if rle_count != 0:
    bytes = [128 + rle_count, rle_byte]
    out_f.write(bytearray(bytes))
    rle_count = 0

def compress_file(input_file, output_file):
  global rle_count
  global rle_byte
  global raw_bytes
  global prev_byte
  global out_f
  rle_count = 0
  rle_byte = 0
  raw_bytes = []
  prev_byte = 256
  out_f = open(output_file, "wb")
  with open(input_file, "rb") as f:
    byte = f.read(1)
    prev_byte = byte
    rle_count = 0
    while True:
      if len(raw_bytes) == 128:
        flush()
      if rle_count == 127:
        flush()
      if len(byte) == 0:
        flush()
        bytes = [128]
        out_f.write(bytearray(bytes))
        return
      if byte == prev_byte:
        rle_byte = byte[0]
        rle_count = rle_count + 1
      else:
        if rle_count > 2:
          flush()
        else:
          for x in range(0, rle_count):
            raw_bytes.append(rle_byte)
        raw_bytes.append(byte[0])
        rle_count = 0
      prev_byte = byte
      byte = f.read(1)
"""

MAX_MATCH_LEN = 127
MAX_MATCH_DIST = 127

def flush(out_f, type: int, len: int, dist: int, data: bytes):
  if len == 0:
    return
  if type == 0:
    bytes_list = [len]
    for x in range(dist, dist + len):
      bytes_list.append(data[x])
    out_f.write(bytearray(bytes_list))
  else:
    bytes_list = [128 + len, 255 - (dist - 1)]
    out_f.write(bytearray(bytes_list))

def compress_file(input_file, output_file):
  out_f = open(output_file, "wb")
  in_f = open(input_file, "rb")
  in_bytes = in_f.read()
  in_pos = 3
  unmatched_bytes = 3
  while in_pos < len(in_bytes):
    # find match
    min_match_dist = in_pos - MAX_MATCH_DIST
    if min_match_dist < 0:
      min_match_dist = 0
    longest_match = 0
    longest_match_pos = 0
    for pos in range(min_match_dist, in_pos - 1):
      max_match_len = in_pos - pos
      len_left = len(in_bytes) - in_pos
      if max_match_len > len_left:
        max_match_len = len_left
      match_len = 0
      match_pos = pos
      for size in range(0, max_match_len):
        if in_bytes[match_pos + size] == in_bytes[in_pos + size]:
          match_len = match_len + 1
        else:
          break
      if match_len > longest_match:
          longest_match = match_len
          longest_match_pos = match_pos

    if longest_match >= 3:
      flush(out_f, 0, unmatched_bytes, in_pos - unmatched_bytes, in_bytes)
      flush(out_f, 1, longest_match, in_pos - longest_match_pos, in_bytes)
      in_pos = in_pos + longest_match
      unmatched_bytes = 0
    else:
      unmatched_bytes = unmatched_bytes + 1
      in_pos = in_pos + 1
    if unmatched_bytes >= 127:
      flush(out_f, 0, unmatched_bytes, in_pos - unmatched_bytes, in_bytes)
      unmatched_bytes = 0
  flush(out_f, 0, unmatched_bytes, in_pos - unmatched_bytes, in_bytes)
  bytes_list = [0]
  out_f.write(bytearray(bytes_list))

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", help="Output file") 
parser.add_argument("-i", "--input", help="Input file")
args = parser.parse_args()
compress_file(args.input, args.output)
