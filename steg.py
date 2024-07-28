#! python3
from PIL import Image
from pathlib import Path
import sys

# <path_to_script> <path_to_image> <encode/decode> <--file/text> <path_to_text_file>
# Only works on RGB images!k

def main():
    command_line()

def read_file(path: str):
    f = open(path, "r")
    s = f.read()
    f.close()
    return s

def command_line():
    path = Path(sys.argv[1])
    if "encode" in sys.argv:
        if sys.argv[3] == "-file":
            text = read_file(sys.argv[4])
            encode(path, text)
        else:
            encode(path, sys.argv[3])
    if "decode" in sys.argv:
        text = decode(path)
        print(text)

def decode(path: Path):
    img = Image.open(path)
    binstr_arr = []
    num_bits = decode_length(path)
    bit_to_use = -1    # index of binary string to be read
    current_byte = ""
    while True:
        for pixel in list(img.getdata())[4:]:
            for rgb in pixel[:3]:
                bin_rgb = bin(rgb)[2:].zfill(8)
                current_byte += bin_rgb[bit_to_use]
                num_bits -= 1
                if len(current_byte) == 8:
                    binstr_arr.append(current_byte)
                    current_byte = ""
                if num_bits == 0:
                    break
            if num_bits == 0:
                break
        if num_bits == 0:
            break
        bit_to_use -= 1
    decoded = binarr_to_str(binstr_arr)
    return decoded
    
def binarr_to_str(binarr):
    binstr = ""
    for byte in binarr:
        binstr += chr(int(byte, 2))
    return binstr

def decode_length(path: Path):
    # extracts the length of the binary string from the first 12 bytes
    im = Image.open(path)
    binLength = ""
    # last 2 bits of first 12 bytes store data length
    for p in list(im.getdata())[:4]:
        for byte in p[:3]:
            bin_byte = bin(byte)[2:].zfill(8)
            binLength += bin_byte[-2:]
    return int(binLength, 2)

def encode_length(path: Path, s):
    img = Image.open(path)
    bin_len = bin(len(s)*8)[2:].zfill(24)
    bin_len_index = 0
    width, height = img.size
    img2 = Image.new("RGB", (width, height))
    for y in range(height):
        for x in range(width):
            new_pixel = list(img.getpixel((x, y)))
            for rgb in range(3):
                if bin_len_index == 24: 
                    return img, img2
                old_byte = bin(new_pixel[rgb])[2:].zfill(8)
                new_byte = old_byte[:-2] + bin_len[bin_len_index:bin_len_index+2]
                new_byte = int(new_byte, 2)
                new_pixel[rgb] = new_byte
                bin_len_index += 2
            img2.putpixel((x, y), tuple(new_pixel))

def encode(path: Path, text):
    img, img2 = encode_length(path, text)
    s = str_to_binarr(text)
    binstr = binarr_to_binstr(s)
    binstr_index = 0
    byte_index = 0
    bit_to_replace = -1     # start with replacing the last bit of each byte, then once each byte has been changed once, change the second last bit
    width, height = img.size
    all_passovers = [[0 for i in range((width*height)*3)] for j in range(8)]
    passes = 0
    while True:
        if (bit_to_replace < -8):
            print("The text is too large to encode in the given image.")
            return
        if binstr_index == len(binstr):
            break
        for y in range(height):
            for x in range(width):
                new_pixel = list(img.getpixel((x, y)))
                for rgb in range(3):
                    if byte_index < 12:
                        byte_index += 1
                        continue
                    if binstr_index == len(binstr):
                        if passes == 0:
                            start_x = x+1
                            start_y = y
                            if start_x > width:
                                start_x = 0
                                start_y += 1
                            build_from_position(img2, img, start_x, start_y).save(path.parent / "new.png", "PNG")
                            return
                        else:
                            break
                    old_byte = bin(new_pixel[rgb])[2:].zfill(8)
                    if bit_to_replace == -1:
                        new_byte = old_byte[:bit_to_replace] + binstr[binstr_index]
                    if bit_to_replace < -1:
                        new_old_byte = all_passovers[passes-1][byte_index]
                        new_byte = new_old_byte[:bit_to_replace] + binstr[binstr_index] + new_old_byte[bit_to_replace+1:]
                    all_passovers[passes][byte_index] = new_byte
                    new_byte = int(new_byte, 2)
                    new_pixel[rgb] = new_byte
                    binstr_index += 1
                    img2.putpixel((x, y), tuple(new_pixel))
                    byte_index += 1
        bit_to_replace -= 1
        byte_index = 0
        passes += 1
    img2.save(path.parent / "new.png", "PNG")

def build_from_position(new_img: Image, base_img: Image, start_x: int, start_y: int):
    reached_position = False
    for y in range(base_img.size[1]):
        if y < start_y:
            continue
        for x in range(base_img.size[0]):
            if x == start_x:
                reached_position = True
            if not reached_position:
                continue
            new_img.putpixel((x, y), base_img.getpixel((x, y)))
    return new_img

def binarr_to_binstr(binarr):
    binstr = ''.join([i for i in binarr])
    return binstr

def str_to_binarr(text):
    # converts string to binary, returns binary character array
    binArray = []
    for char in text:
        if ord(char) > 255:
            continue
        binArray.append(bin(ord(char))[2:].zfill(8))    # each character should be 8 bits long
    return binArray

if __name__ == "__main__":
    sys.exit(main())