import json
import math
from pathlib import Path

from huffman_tree import build_modified_huffman_tree, OTHERS


def build_original_codes(text):
    """
    Assign a fixed-width binary code to every distinct symbol.
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
    """
    Compress text using the existing Modified Huffman algorithm.
    Returns the compressed bit stream and its header.
    """
    if not 0 <= min_limit <= 1:
        raise ValueError(
            "Minimum probability limit must be between 0 and 1."
        )

    if not text:
        return "", {
            "algorithm": "Modified Huffman",
            "min_probability_limit": min_limit,
            "codes": {},
            "original_codes": {},
            "original_code_length": 4,
            "rare_symbols": [],
        }

    _, codes, rare_symbols = build_modified_huffman_tree(
        text, min_limit
    )

    original_codes, original_code_length = build_original_codes(text)

    compressed_bits = []

    for char in text:
        if char in rare_symbols:
            compressed_bits.append(
                codes[OTHERS] + original_codes[char]
            )
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


def bits_to_bytes(bit_stream):
    """
    Convert the compressed bit stream into actual binary bytes.
    """
    padding = (8 - len(bit_stream) % 8) % 8
    padded_bits = bit_stream + "0" * padding

    binary_data = bytearray()

    for i in range(0, len(padded_bits), 8):
        byte = padded_bits[i:i + 8]
        binary_data.append(int(byte, 2))

    return bytes(binary_data), padding



def save_binary_file(bit_stream, overhead, output_bin_path):
    """
    Save ONLY the compressed bit stream as actual binary bytes.
    """
    compressed_bytes, padding = bits_to_bytes(bit_stream)

    with open(output_bin_path, "wb") as file:
        file.write(compressed_bytes)




def format_header_for_text(overhead):
    """
    Format the compression tables for display in the text output.
    """
    lines = [
        "",
        "=" * 40,
        "MODIFIED HUFFMAN TABLES",
        "=" * 40,
        f"Algorithm: {overhead['algorithm']}",
        (
            "Minimum probability limit: "
            f"{overhead['min_probability_limit']}"
        ),
        "",
        "HUFFMAN CODES:",
    ]

    for symbol, code in overhead["codes"].items():
        lines.append(f"{repr(symbol)} : {code}")

    lines.extend([
        "",
        "ORIGINAL SYMBOL CODES:",
    ])

    for symbol, code in overhead["original_codes"].items():
        lines.append(f"{repr(symbol)} : {code}")

    lines.extend([
        "",
        f"Original code length: {overhead['original_code_length']}",
        f"Rare symbols: {overhead['rare_symbols']}",
        "=" * 40,
    ])

    return "\n".join(lines)


def compress_file(
    input_file_path,
    output_txt_path,
    output_header_path,
    min_limit
):
    """
    Produce:
    1. A text file containing compressed bits and readable tables.
    2. A JSON header file, preserving the existing output format.
    3. A binary .bin file containing the header and compressed bytes.
    """
    input_path = Path(input_file_path)

    text = input_path.read_text(encoding="utf-8")

    bit_stream, overhead = compress_text(text, min_limit)

    # Save the compressed bits followed by readable tables.
    text_output = bit_stream + format_header_for_text(overhead)

    Path(output_txt_path).write_text(
        text_output, encoding="utf-8"
    )

    # Preserve the separate JSON header for existing code compatibility.
    Path(output_header_path).write_text(
        json.dumps(overhead, ensure_ascii=False, indent=4),
        encoding="utf-8"
    )

    # Automatically create a .bin file beside the text output.
    output_bin_path = Path(output_txt_path).with_suffix(".bin")

    save_binary_file(
        bit_stream,
        overhead,
        output_bin_path
    )

    original_size = len(text.encode("utf-8"))
    compressed_bit_count = len(bit_stream)

    ratio = (
        (1 - compressed_bit_count / (original_size * 8)) * 100
        if original_size > 0
        else 0.0
    )

    return original_size, compressed_bit_count, ratio

