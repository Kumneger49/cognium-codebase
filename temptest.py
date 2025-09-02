
import os

files = [
        os.path.join("./data", f)
        for f in os.listdir("./data")
        if os.path.isfile(os.path.join("./data", f))
    ]

print(files)