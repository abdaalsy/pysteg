pysteg - A steganography tool built with Python. 

This program hides text in an input image's RGB data with unnoticeable changes to the image itself. The text can then be extracted at a later time.

Usage: py <path_to_script> <path_to_image> encode "text in quotes"\n
       py <path_to_script> <path_to_image> encode -file <path_to_text_file>\n
       py <path_to_script> <path_to_script> decode
