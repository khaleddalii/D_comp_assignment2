import heapq
from collections import Counter


OTHERS = "Others"


class HuffmanNode:
    def __init__(self, symbol, freq, order=0):
        self.symbol = symbol
        self.freq = freq
        self.order = order
        self.left = None
        self.right = None

    def __lt__(self, other):
        # Stable tie-breaking makes the generated codes reproducible.
        return (self.freq, self.order) < (other.freq, other.order)


def build_modified_huffman_tree(text, min_limit):
    """
    Build a Huffman tree for symbols whose probability is greater than
    min_limit. All symbols with probability <= min_limit are represented
    by the single pseudo-symbol "Others".
    """
    if not 0 <= min_limit <= 1:
        raise ValueError("Minimum probability limit must be between 0 and 1.")

    if not text:
        return None, {}, set()

    counts = Counter(text)
    total_chars = len(text)
    significant_freqs = {}
    rare_symbols = set()

    # Sort symbols so equal-frequency inputs always produce repeatable results.
    for symbol in sorted(counts):
        count = counts[symbol]
        probability = count / total_chars
        if probability > min_limit:
            significant_freqs[symbol] = count
        else:
            rare_symbols.add(symbol)

    if rare_symbols:
        significant_freqs[OTHERS] = sum(counts[symbol] for symbol in rare_symbols)

    heap = []
    order = 0
    for symbol, freq in significant_freqs.items():
        heapq.heappush(heap, HuffmanNode(symbol, freq, order))
        order += 1

    if not heap:
        return None, {}, rare_symbols

    if len(heap) == 1:
        only_node = heap[0]
        root = HuffmanNode(None, only_node.freq, order)
        root.left = only_node
        return root, {only_node.symbol: "0"}, rare_symbols

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq, order)
        order += 1
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    root = heap[0]
    codes = {}

    def generate_codes(node, prefix):
        if node is None:
            return
        if node.symbol is not None:
            codes[node.symbol] = prefix
            return
        generate_codes(node.left, prefix + "0")
        generate_codes(node.right, prefix + "1")

    generate_codes(root, "")
    return root, codes, rare_symbols
