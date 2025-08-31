

from main import main
import asyncio


print("This is the testing file calling the main file")
# print(asyncio.run(main(query="what is the summary of the document I provided?", file_path="data/RockefellerData.pdf")))
print(asyncio.run(main(query="what is the summary of the document I provided?", file_path="data/TSLA-Q3-2023-Update-3.pdf")))