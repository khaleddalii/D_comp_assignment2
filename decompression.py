import json
from pathlib import Path
from huffman_tree import OTHERS


def decompress_text(bit_stream, overhead):
    codes = overhead["codes"]
    original_codes = overhead["original_codes"]
    original_code_length = overhead["original_code_length"]

    reverse_codes = {v: k for k, v in codes.items()}
    others_prefix = codes.get(OTHERS, "")
    others_prefix_len = len(others_prefix)

    reverse_original_codes = {v: k for k, v in original_codes.items()}

    decompressed_chars = []
    i = 0
    n = len(bit_stream)

    while i < n:
        if others_prefix and bit_stream.startswith(others_prefix, i):
            i += others_prefix_len
            orig_bits = bit_stream[i : i + original_code_length]
            i += original_code_length
            if orig_bits in reverse_original_codes:
                decompressed_chars.append(reverse_original_codes[orig_bits])
        else:
            matched = False
            for length in range(1, n - i + 1):
                prefix = bit_stream[i : i + length]
                if prefix in reverse_codes:
                    symbol = reverse_codes[prefix]
                    decompressed_chars.append(symbol)
                    i += length
                    matched = True
                    break
            if not matched:
                break

    return "".join(decompressed_chars)


def decompress_file(input_txt_path, input_header_path, output_file_path):
    bit_stream = Path(input_txt_path).read_text(encoding="utf-8")
    overhead = json.loads(Path(input_header_path).read_text(encoding="utf-8"))

    decompressed_text = decompress_text(bit_stream, overhead)

    Path(output_file_path).write_text(decompressed_text, encoding="utf-8")
    return decompressed_text