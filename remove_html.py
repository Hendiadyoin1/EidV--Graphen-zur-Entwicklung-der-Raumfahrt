from html.parser import HTMLParser
import html
from glob import glob
import os
import re

htmlTag = re.compile("(</?[^>]*>)")

if __name__ == "__main__":
	files = glob('*.txt')
	parser = HTMLParser()

	for file in files:

		with open(file) as f:
			content = f.read()

		l1 = len(content)
		content = html.unescape(content)
		l2 = len(content)
		content = htmlTag.sub('',content)
		l3 = len(content)
		print(
			f"{file}:\n"
			f"\t{'html-escapes:':<15}{l1-l2:>10}\n"
			f"\t{'html-tags:':<15}{l2-l3:>10}\n"
			f"\t{'all:':<15}{l1-l3:>10}\n")

		with open(file,'w') as f:
			f.write(content)