

from main import main
import asyncio


# print("This is the testing file calling the main file")
# print(asyncio.run(main(query="what is the summary of the document I provided?", file_path="data/RockefellerData.pdf")))
user_query = "Could you summarize what is in page 15?"
question = f"""
You are acting as a research assistant for an investment company. 
You will receive a document (financial report, news article, company profile, or market analysis). 

Your task: Carefully analyze the document and directly answer the user query. 
- Use only the content relevant to the query. 
- If the query asks broadly, highlight information investors care about (e.g., financial performance, growth potential, risks, competitive positioning, management quality, market opportunities). 
- If the query is specific, focus only on that aspect. Do not introduce unrelated metrics. 
- If the document lacks enough detail, acknowledge the gaps clearly. 

User Query: {user_query}
"""

print(asyncio.run(main(question)))
# print(asyncio.run(main(query="who is rockefeller writing these letters for?")))

 









