import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from huffman_compression import compress_file
import decompression  


class HuffmanCompressorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Modified Huffman - Compression & Decompression Task")
        self.root.geometry("680x560")
        self.root.configure(bg="#1e1e2e")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(
            self.root,
            text="Modified Huffman Compression & Decompression",
            font=("Helvetica", 16, "bold"),
            fg="#cdd6f4",
            bg="#1e1e2e",
        ).pack(pady=15)

        limit_frame = tk.Frame(self.root, bg="#1e1e2e")
        limit_frame.pack(pady=5)

        tk.Label(
            limit_frame,
            text="Minimum Limit (Probability, 0 to 1):",
            font=("Helvetica", 10, "bold"),
            fg="#bac2de",
            bg="#1e1e2e",
        ).pack(side=tk.LEFT, padx=5)

        self.limit_entry = tk.Entry(
            limit_frame,
            font=("Helvetica", 10),
            width=10,
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="white",
        )
        self.limit_entry.insert(0, "0.05")
        self.limit_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(
            self.root,
            text="Upload & Compress Text File",
            font=("Helvetica", 11, "bold"),
            bg="#a6e3a1",
            fg="#11111b",
            padx=20,
            pady=6,
            command=self.run_compression,
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Decompress Compressed File (.txt + .json)",
            font=("Helvetica", 11, "bold"),
            bg="#89b4fa",
            fg="#11111b",
            padx=20,
            pady=6,
            command=self.run_decompression,
        ).pack(pady=5)

        stats_frame = tk.LabelFrame(
            self.root,
            text=" Results ",
            font=("Helvetica", 10, "bold"),
            fg="#cba6f7",
            bg="#1e1e2e",
            padx=10,
            pady=10,
        )
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.stats_text = tk.Text(
            stats_frame,
            font=("Consolas", 10),
            bg="#181825",
            fg="#a6adc8",
            relief=tk.FLAT,
            wrap=tk.WORD,
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True)

    def run_compression(self):
        file_path = filedialog.askopenfilename(
            title="Select input text file",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not file_path:
            return

        try:
            min_limit = float(self.limit_entry.get())
            if not 0 <= min_limit <= 1:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid limit",
                "Enter a probability between 0 and 1, for example 0.05 or 0.2.",
            )
            return

        input_path = Path(file_path)
        output_txt_path = input_path.with_name(input_path.stem + "_compressed.txt")
        output_header_path = input_path.with_name(input_path.stem + "_header.json")

        try:
            orig_size, comp_bit_count, ratio = compress_file(
                input_path, output_txt_path, output_header_path, min_limit
            )

            self.stats_text.delete("1.0", tk.END)
            self.stats_text.insert(
                tk.END,
                "SUCCESS: File compressed successfully!\n"
                "----------------------------------------\n"
                f"Original File Size       : {orig_size} Bytes\n"
                f"Compressed Bit Stream    : {comp_bit_count} Bits\n"
                f"Payload-only Ratio       : {ratio:.2f}%\n"
                "----------------------------------------\n"
                "Generated Output Files:\n"
                f"1. {output_txt_path}\n"
                f"2. {output_header_path}\n",
            )
            messagebox.showinfo(
                "Success",
                "Compression completed successfully!\n\n"
                f"Compressed data:\n{output_txt_path}\n\n"
                f"Header:\n{output_header_path}",
            )
        except Exception as exc:
            messagebox.showerror("Compression Error", f"Failed to compress:\n{exc}")

    def run_decompression(self):
        txt_path = filedialog.askopenfilename(
            title="Select Compressed Bitstream File (.txt)",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not txt_path:
            return

        json_path = filedialog.askopenfilename(
            title="Select Header File (.json)",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
        )
        if not json_path:
            return

        input_path = Path(txt_path)
        default_output = input_path.with_name(input_path.stem.replace("_compressed", "") + "_decompressed.txt")
        
        output_path = filedialog.asksaveasfilename(
            title="Save Decompressed Text File",
            initialfile=default_output.name,
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not output_path:
            return

        try:
            decompressed_text = decompression.decompress_file(txt_path, json_path, output_path)

            self.stats_text.delete("1.0", tk.END)
            self.stats_text.insert(
                tk.END,
                "SUCCESS: File decompressed successfully!\n"
                "----------------------------------------\n"
                f"Restored File Saved To:\n{output_path}\n"
                "----------------------------------------\n"
                "Preview of Restored Text:\n"
                f"{decompressed_text[:300]}...\n",
            )
            messagebox.showinfo(
                "Success",
                f"Decompression completed successfully!\nSaved to:\n{output_path}",
            )
        except Exception as exc:
            messagebox.showerror("Decompression Error", f"Failed to decompress:\n{exc}")


if __name__ == "__main__":
    root = tk.Tk()
    app = HuffmanCompressorGUI(root)
    root.mainloop()