
import os
import os.path
import sys

PATH = "."
for (path, dir, files) in os.walk(PATH):
    for filename in files:
        ext = os.path.splitext(filename)[-1]
	print("1, %s" % (ext)) # 확장자 출력
	print("2, %s" % (filename))
