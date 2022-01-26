from huffmanTable import HuffmanTable
import sys

path = "litPL.txt"

h = HuffmanTable(path)

output_path = h.compress()
print("Compressed file path: " + output_path)

decom_path = h.decompress(output_path)
print("Decompressed file path: " + decom_path)