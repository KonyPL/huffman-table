import os
import pickle

class HuffmanTable:
    def __init__(self, path):
            self.path = path
            self.codes = {}
            self.decodes = {}
            self.leading_zeroes = 8
            self.dictionary_len = 0

    def get_linked_code(self,code, huff_table, id):
            if(huff_table[huff_table[id][2]][2] == None):
                code += huff_table[id][1]
                return code
            else:
                code = self.get_linked_code(code, huff_table, huff_table[id][2])
                code += huff_table[id][1]
                return code
        

    def build_code_table(self, frequency):
        table = []
        
        all_symbols = 0
        everything = 0

        for key in frequency:
            table.append([key, frequency[key]])
            all_symbols += frequency[key]

        table = sorted(table, key= lambda x:x[1])

        # for col in table:
        #     col[1] = col[1] / all_symbols
        #     everything += col[1]

        #make 2N - 1 list for calculations
        huff_table = []
        for i in range(2 * len(table) - 1):
            if i < len(table):
                huff_table.append([table[i][1], None, None])
            else:
                huff_table.append([None, None, None])

        next_empty = len(table)
        while(huff_table[len(huff_table) - 1][0] is None):
            min1 = [None, all_symbols]
            min2 = [None, all_symbols]
            for i in range(next_empty):
                if( huff_table[i][0] < min1[1] and huff_table[i][1] is None):
                    min1 = [i, huff_table[i][0]]
            
            for i in range(min1[0] + 1, next_empty):
                if( huff_table[i][0] < min2[1] and huff_table[i][1] is None):
                    min2 = [i, huff_table[i][0]]

            huff_table[next_empty][0] = min1[1] + min2[1]
            #add Binary value and link
            huff_table[min1[0]][1] = '0'
            huff_table[min1[0]][2] = next_empty
            huff_table[min2[0]][1] = '1'
            huff_table[min2[0]][2] = next_empty

            next_empty += 1

        #get code from linked columns and revert
        for i in range(len(table)):
            code = ""
            code = self.get_linked_code(code, huff_table, i)
            self.codes[table[i][0]] = code

    # functions for compression:

    def make_frequency_dict(self, text):
        frequency = {}
        for character in text:
            if not character in frequency:
                frequency[character] = 0
            frequency[character] += 1
        return frequency

    def get_encoded_text(self, text):
        encoded_text = ""
        for character in text:
            encoded_text += self.codes[character]
        return encoded_text

    def add_leading_zeros(self, val, leading_z):
        padding = leading_z - len(val)
        pad = ""
        for i in range(padding):
            pad += "0"
        return pad + val

    def gen_dict(self):
        bindict = ""
        maxLength = 0
        for key in self.codes:
            length = len(self.codes[key])
            if length > maxLength:
                maxLength = length

        if maxLength > 16:
            self.leading_zeroes = 24
        elif maxLength > 8:
            self.leading_zeroes = 16

        for key in self.codes:
            #make dictionary with bytes of Char an it's Code
            if self.leading_zeroes == 8:
                bindict += "{0:08b}".format(ord(key)) + self.add_leading_zeros(self.codes[key], 8)
            elif self.leading_zeroes == 16:
                bindict += "{0:08b}".format(ord(key)) + self.add_leading_zeros(self.codes[key], 16)
            elif self.leading_zeroes == 24:
                bindict += "{0:08b}".format(ord(key)) + self.add_leading_zeros(self.codes[key], 24)

        return bindict


    def pad_encoded_text(self, encoded_text):
        extra_padding = 8 - len(encoded_text) % 8
        for i in range(extra_padding):
            encoded_text += "0"

        padded_info = "{0:08b}".format(extra_padding)
        # dict_len = "{0:08b}".format(len(self.codes))
        # dictionary = self.gen_dict()
        # leading_z = "{0:08b}".format(self.leading_zeroes)

        encoded_text = padded_info + encoded_text

        return encoded_text

    def get_byte_array(self, padded_encoded_text):
        if(len(padded_encoded_text) % 8 != 0):
            print("Encoded text not padded properly")
            exit(0)

        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return b


    def compress(self):
        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + ".bin"
        dict_path = filename + "_huffman_codes.bin"

        with open(self.path, 'r+') as file, open(output_path, 'wb') as output:
            text = file.read()
            text = text.rstrip()

            frequency = self.make_frequency_dict(text)
            self.build_code_table(frequency)
            

            encoded_text = self.get_encoded_text(text)
            padded_encoded_text = self.pad_encoded_text(encoded_text)

            b = self.get_byte_array(padded_encoded_text)
            output.write(bytes(b))

        dict_file = open(dict_path, 'wb')
        pickle.dump(self.codes, dict_file)
        dict_file.close()
        self.codes = {}

        print("Compressed")
        return output_path


    """ functions for decompression: """
    def del_leading_zeros(self, val):
        if int(val, 2) == 0:
            return "0"
        if int(val, 2) == 1:
            return "1"

        for i in range(1,len(val)):
            zero = val[:i]
            if int(zero, 2) != 0:
                if(val[i-1:] != ""):
                    return val[i-1:]
            

    def decode_dict(self, encoded_dict):
        self.decodes = {}
        for i in range(self.dictionary_len):
            character = encoded_dict[:8]
            encoded_dict = encoded_dict[8:]
            val = chr(int(character, 2))

            code = encoded_dict[:self.leading_zeroes]
            encoded_dict = encoded_dict[self.leading_zeroes:]
            key = self.del_leading_zeros(code)

            self.decodes[key] = val


    def remove_padding(self, padded_encoded_text):
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)
        padded_encoded_text = padded_encoded_text[8:] 

        # leading_z_info = padded_encoded_text[:8]
        # self.leading_zeroes = int(leading_z_info, 2)
        # padded_encoded_text = padded_encoded_text[8:] 

        # dict_len_info = padded_encoded_text[:8]
        # self.dictionary_len = int(dict_len_info, 2)
        # padded_encoded_text = padded_encoded_text[8:] 

        # total_dict_len = self.dictionary_len * (8 + self.leading_zeroes)

        # dictionary_info = padded_encoded_text[:total_dict_len]
        # self.decode_dict(dictionary_info)
        # padded_encoded_text = padded_encoded_text[total_dict_len:] 

        encoded_text = padded_encoded_text[:-1*extra_padding]

        return encoded_text

    def decode_text(self, encoded_text):
        self.decodes = {v: k for k, v in self.codes.items()}
        current_code = ""
        decoded_text = ""

        for bit in encoded_text:
            current_code += bit
            if(current_code in self.decodes):
                character = self.decodes[current_code]
                decoded_text += character
                current_code = ""

        return decoded_text


    def decompress(self, input_path):
        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + "_decompressed" + ".txt"
        dict_path = filename + "_huffman_codes.bin"

        dict_file = open(dict_path, 'rb')
        self.codes = pickle.load(dict_file)
        dict_file.close()

        with open(input_path, 'rb') as file, open(output_path, 'w') as output:
            bit_string = ""

            byte = file.read(1)
            while(len(byte) > 0):
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, '0')
                bit_string += bits
                byte = file.read(1)

            encoded_text = self.remove_padding(bit_string)

            decompressed_text = self.decode_text(encoded_text)
            
            output.write(decompressed_text)

        print("Decompressed")
        return output_path