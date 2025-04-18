import pymupdf
import re

def find_largest_number_in_pdf(filename):
    doc = pymupdf.open(filename)
    maxVal = 0
    units = { # units that can be used
        "billion": 1_000_000_000,
        "million": 1_000_000,
        "thousand": 1_000,
        "K": 1_000,
        "M": 1_000_000,
        "B": 1_000_000_000
    }
    for page in doc: # iterate through the pages
        text = page.get_text()
        multiplier = 1
        numPattern = re.compile(r"\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+\.\d+") # number regex
        lines = text.splitlines()
        for line in lines:
            # we search stated values line-wise instead of page-wise because when the page mentions 
            #(in millions) it typically refers to numbers that are on lines below it on the page
            if re.search(r"in?\s+millions", line, re.IGNORECASE): 
                multiplier = 1000000
            if re.search(r"in?\s+thousands", line, re.IGNORECASE):
                multiplier = 1000
            try: #if a number is by itself on a line
                newLine = line.strip()
                if newLine.startswith("$"):
                    newLine = newLine[1:]
                newLine = newLine.replace(",", "")
                floatVal = float(newLine)
                # we use the multiplier only on lines with a number by itself because 
                #(in millions) typically refers to numbers in tables, which are in lines by themselves
                floatVal = floatVal * multiplier 
                maxVal = max(floatVal, maxVal)
                continue
            except ValueError:
                pass
            # this is for numbers within text with a stated unit value
            for unit, factor in units.items():
                pattern = re.compile(r"(\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+\.\d+)\s*"+ re.escape(unit), re.IGNORECASE)
                nums = pattern.findall(line)
                for num in nums:
                    num = num.replace(",", "")
                    value = float(num) * factor
                    maxVal = max(value, maxVal)

            # this is for just general numbers within the text
            nums = numPattern.findall(line)
            for num in nums:
                num = num.replace(",", "")
                value = float(num)
                maxVal = max(value, maxVal)

    doc.close()
    return maxVal
result = find_largest_number_in_pdf("example.pdf")
print("Largest value found:", result)