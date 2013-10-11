import sys
import re

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        text = f.read()
    text = " ".join(text.split())
    matches = re.findall(r"<TITLE>(.*?)</TITLE>.*?<BODY>(.*?)</BODY>", text)
    for title, body in matches:
        title = title.lower()
        body = body.lower()
        with open("-".join(title.split()), "w") as f:
            f.write(title + "\n\n" + body)
