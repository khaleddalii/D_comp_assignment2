import json
import math
from pathlib import Path
from huffman_tree import build_modified_huffman_tree, OTHERS


def build_original_codes(text):
    """
    Assign every distinct input symbol a fixed-width original code.
    The width is at least 4 bits, matching the assignment's example
    (a=0000, b=0001, c=0010, ...). It grows if the file has >16 symbols.
    The mapping is stored in the header, so it can be decoded unambiguously.
    """
    symbols = sorted(set(text))
    if not symbols:
        return {}, 4

    width = max(4, math.ceil(math.log2(len(symbols))))
    original_codes = {
        symbol: format(index, f"0{width}b")
        for index, symbol in enumerate(symbols)
    }
    return original_codes, width


def compress_text(text, min_limit):
    if not 0 <= min_limit <= 1:
        raise ValueError("Minimum probability limit must be between 0 and 1.")

    if not text:
        return "", {
            "algorithm": "Modified Huffman",
            "min_probability_limit": min_limit,
            "codes": {},
            "original_codes": {},
            "original_code_length": 4,
            "rare_symbols": [],
        }

    _, codes, rare_symbols = build_modified_huffman_tree(text, min_limit)
    original_codes, original_code_length = build_original_codes(text)

    compressed_bits = []
    for char in text:
        if char in rare_symbols:
            compressed_bits.append(codes[OTHERS] + original_codes[char])
        else:
            compressed_bits.append(codes[char])

    bit_stream = "".join(compressed_bits)

    overhead = {
        "algorithm": "Modified Huffman",
        "min_probability_limit": min_limit,
        "codes": codes,
        "original_codes": original_codes,
        "original_code_length": original_code_length,
        "rare_symbols": sorted(rare_symbols),
    }
    return bit_stream, overhead

def compress_file(input_file_path, output_txt_path, output_header_path, min_limit):
    input_path = Path(input_file_path)
    text = input_path.read_text(encoding="utf-8")

    bit_stream, overhead = compress_text(text, min_limit)

    Path(output_txt_path).write_text(bit_stream, encoding="utf-8")
    Path(output_header_path).write_text(
        json.dumps(overhead, ensure_ascii=False, indent=4), encoding="utf-8"
    )

    original_size = len(text.encode("utf-8"))
    compressed_bit_count = len(bit_stream)
    ratio = (
        (1 - compressed_bit_count / (original_size * 8)) * 100
        if original_size > 0
        else 0.0
    )
    return original_size, compressed_bit_count, ratio