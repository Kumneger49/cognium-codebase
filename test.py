

from main import main
import asyncio


# print("This is the testing file calling the main file")
# print(asyncio.run(main(query="what is the summary of the document I provided?", file_path="data/RockefellerData.pdf")))
user_query = "Could you summarize what is in page 15?"
question = f"""You are acting as a research assistant for an investment company. You will receive a document (e.g., financial report, news article, company profile, or market analysis). 
        Your task is to carefully read and analyze the document from the perspective of an investor. Based on the document, answer the following user query:
        User Query: {user_query}
        When responding, highlight information that is most relevant to investment decisions, such as: financial performance, growth potential, competitive positioning, risks, management quality, and market opportunities. 
        If the document does not contain enough information to answer fully, acknowledge the gaps clearly. Always respond in a structured, concise, and professional manner"""
print(asyncio.run(main(question)))
# print(asyncio.run(main(query="who is rockefeller writing these letters for?")))


