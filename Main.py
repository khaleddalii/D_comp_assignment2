
import json
from pathlib import Path

import huffman_compression
import decompression


# Save output files beside Main.py.
BASE_DIR = Path(__file__).resolve().parent


def bits_to_bytes(bit_string):
    padding = (8 - len(bit_string) % 8) % 8
    padded_bits = bit_string + "0" * padding

    byte_array = bytearray()

    for i in range(0, len(padded_bits), 8):
        byte = padded_bits[i:i + 8]
        byte_array.append(int(byte, 2))

    return bytes(byte_array), padding


def bytes_to_bits(data_bytes, padding):
    bit_string = "".join(
        format(byte, "08b") for byte in data_bytes
    )

    if padding:
        bit_string = bit_string[:-padding]

    return bit_string


def save_binary_file(bit_stream, overhead):
    output_path = BASE_DIR / "compressed.bin"

    compressed_bytes, padding = bits_to_bytes(bit_stream)

    header = overhead.copy()
    header["padding"] = padding

    header_bytes = json.dumps(
        header, ensure_ascii=False
    ).encode("utf-8")

    header_length = len(header_bytes).to_bytes(
        4, byteorder="big"
    )

    with open(output_path, "wb") as file:
        file.write(header_length)
        file.write(header_bytes)
        file.write(compressed_bytes)

    return output_path


def load_binary_file(input_path):
    with open(input_path, "rb") as file:
        length_bytes = file.read(4)

        if len(length_bytes) != 4:
            raise ValueError("Invalid binary file.")

        header_length = int.from_bytes(
            length_bytes, byteorder="big"
        )

        header_bytes = file.read(header_length)

        if len(header_bytes) != header_length:
            raise ValueError("Incomplete binary header.")

        overhead = json.loads(
            header_bytes.decode("utf-8")
        )

        compressed_bytes = file.read()

    padding = overhead.get("padding", 0)
    bit_stream = bytes_to_bits(
        compressed_bytes, padding
    )

    return bit_stream, overhead


def compress():
    print("\n========== COMPRESSION ==========")

    filename = input(
        "Enter input text file [original.txt]: "
    ).strip()

    if not filename:
        filename = "original.txt"

    input_path = Path(filename)

    if not input_path.is_absolute():
        input_path = BASE_DIR / input_path

    if not input_path.is_file():
        print(f"Error: Input file not found: {input_path}")
        return

    try:
        min_limit = float(
            input("Enter minimum probability limit (0-1): ")
        )

        if not 0 <= min_limit <= 1:
            print("Error: Limit must be between 0 and 1.")
            return

        text = input_path.read_text(encoding="utf-8")

        # Use the existing compression algorithm.
        bit_stream, overhead = (
            huffman_compression.compress_text(
                text, min_limit
            )
        )

        # Save the compressed bit stream as text.
        stream_path = BASE_DIR / "compressed_stream.txt"
        stream_path.write_text(
            bit_stream, encoding="utf-8"
        )

        # Save the header and code tables.
        header_path = BASE_DIR / "compressed_header.json"
        header_path.write_text(
            json.dumps(
                overhead,
                ensure_ascii=False,
                indent=4
            ),
            encoding="utf-8"
        )

        # Save the compressed data as a real binary file.
        binary_path = save_binary_file(
            bit_stream, overhead
        )

        print("\nCompression completed successfully!")
        print(f"Compressed bits: {stream_path}")
        print(f"Header and tables: {header_path}")
        print(f"Binary file: {binary_path}")
        print(
            f"Binary file size: "
            f"{binary_path.stat().st_size} bytes"
        )

    except (ValueError, OSError, KeyError) as error:
        print(f"Compression error: {error}")


def decompress():
    print("\n========== DECOMPRESSION ==========")

    filename = input(
        "Enter binary file [compressed.bin]: "
    ).strip()

    if not filename:
        filename = "compressed.bin"

    input_path = Path(filename)

    if not input_path.is_absolute():
        input_path = BASE_DIR / input_path

    if not input_path.is_file():
        print(f"Error: Binary file not found: {input_path}")
        return

    try:
        # Read the compressed binary file.
        bit_stream, overhead = load_binary_file(input_path)

        # Decompress using the existing algorithm.
        restored_text = decompression.decompress_text(
            bit_stream, overhead
        )

        # Save the restored text file.
        text_path = BASE_DIR / "restored.txt"
        text_path.write_text(
            restored_text, encoding="utf-8"
        )

        # Save the original text as actual binary bytes.
        binary_path = BASE_DIR / "decompress_binary.bin"
        binary_path.write_bytes(
            restored_text.encode("utf-8")
        )

        print("\nDecompression completed successfully!")
        print(f"Restored text: {text_path.resolve()}")
        print(f"Binary file: {binary_path.resolve()}")
        print(
            f"Binary file size: "
            f"{binary_path.stat().st_size} bytes"
        )

    except (ValueError, OSError, KeyError) as error:
        print(f"Decompression error: {error}")


def main():
    while True:
        print("\n========== MODIFIED HUFFMAN ==========")
        print("1. Compression")
        print("2. Decompression")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            compress()
        elif choice == "2":
            decompress()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()

