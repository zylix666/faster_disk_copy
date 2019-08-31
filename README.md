# faster_disk_copy
The project can let you create any threads to copy files in parallel. 

Pre-requisite:
1. Python runtime
2. Python Qt5

How to use it?
Suppose you have a source directory called, ./test_256.
You want to copy all files in test_256 to destination folder, ./copy_dst

(base) # python faster_file_copy.py --help
usage: faster_file_copy.py [-h] [-src SRC_DIR] [-dst DST_DIR] [-sec SECTION]

optional arguments:
  -h, --help            show this help message and exit
  -src SRC_DIR, --src_dir SRC_DIR
                        source of dataset
  -dst DST_DIR, --dst_dir DST_DIR
                        destination of dataset
  -sec SECTION, --section SECTION
                        The threads for copying
                        
The program will split the file list according to threads.
