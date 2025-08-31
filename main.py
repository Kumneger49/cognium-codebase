


import asyncio
from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.llm.ollama import ollama_model_complete, _ollama_model_if_cache, ollama_embed
from lightrag.utils import EmbeddingFunc

from dotenv import load_dotenv
load_dotenv()

async def main(query:str, file_path:str):
    # Set up API configuration
    api_key = ""
    # base_url = "your-base-url"  # Optional

    # Create RAGAnything configuration
    config = RAGAnythingConfig(
        working_dir="./rag_storage",
        parser="mineru",  # Parser selection: mineru or docling
        parse_method="auto",  # Parse method: auto, ocr, or txt
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
    )

    # Define LLM model function
    def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        return openai_complete_if_cache(
            "gpt-4o-mini",
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=api_key,
            # base_url=base_url,
            **kwargs,
        )
    
    """For ollama implementation"""
    # def llm_model_func_ollama(prompt, system_prompt=None, history_messages=[], **kwargs):
    #     return _ollama_model_if_cache( 
    #         "phi3:mini",
    #         prompt,
    #         # no need for local models
    #         # system_prompt=system_prompt,
    #         # history_messages=history_messages,
    #         # api_key=api_key,
    #         # base_url=base_url,
    #         # **kwargs,
    #         )

    # Define vision model function for image processing
    def vision_model_func(
        prompt, system_prompt=None, history_messages=[], image_data=None, messages=None, **kwargs
    ):
        # If messages format is provided (for multimodal VLM enhanced query), use it directly
        if messages:
            return openai_complete_if_cache(
                "gpt-4o-mini",
                "",
                system_prompt=None,
                history_messages=[],
                messages=messages,
                api_key=api_key,
                # base_url=base_url,
                **kwargs,
            )
        # Traditional single image format
        elif image_data:
            return openai_complete_if_cache(
                "gpt-4o-mini",
                "",
                system_prompt=None,
                history_messages=[],
                messages=[
                    {"role": "system", "content": system_prompt}
                    if system_prompt
                    else None,
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                },
                            },
                        ],
                    }
                    if image_data
                    else {"role": "user", "content": prompt},
                ],
                api_key=api_key,
                # base_url=base_url,
                **kwargs,
            )
        # Pure text format
        else:
            return llm_model_func(prompt, system_prompt, history_messages, **kwargs)
            # return llm_model_func_ollama(prompt, system_prompt, history_messages, **kwargs)

    # Define embedding function
    embedding_func = EmbeddingFunc(
        embedding_dim=3072,
        max_token_size=8192,
        func=lambda texts: openai_embed(
            texts,
            model="text-embedding-3-large",
            api_key=api_key,
            # base_url=base_url,
        ),
    )

    """For ollama implementation"""
    # embedding_func_ollama = EmbeddingFunc(
    #     embedding_dim=3072,
    #         max_token_size=8192,
    #         func=lambda texts: ollama_embed(                
    #         texts,
    #         embed_model="phi3:mini",
    #         # api_key=api_key, no need for local models
    #         # base_url=base_url,
    #         ),
    # )

    # Initialize RAGAnything
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        vision_model_func=vision_model_func,
        embedding_func=embedding_func,
    )

    # Process a document
    await rag.process_document_complete(
        # file_path="./data/RockefellerData.pdf",
        file_path=f"./{file_path}",
        output_dir="./output",
        parse_method="txt"
    )

    # Query the processed content
    # Pure text query - for basic knowledge base search
    text_result = await rag.aquery(
        # "What are the main findings shown in the figures and tables?",
        # "What do you know about Weaviate?",
        # "Give me the summary of the document I provided",
        # "What is the Total revenues of Q3-2023 of Tesla",
        # "Explain 'SCost of goods sold per vehicle' chart using numbers",

        query=query,
        mode="hybrid"
    )
    # print("Text query result:", text_result)
    return text_result

    # Multimodal query with specific multimodal content
#     multimodal_result = await rag.aquery_with_multimodal(
#     "Explain this formula and its relevance to the document content",
#     multimodal_content=[{
#         "type": "equation",
#         "latex": "P(d|q) = \\frac{P(q|d) \\cdot P(d)}{P(q)}",
#         "equation_caption": "Document relevance probability"
#     }],
#     mode="hybrid"
# )
#     print("Multimodal query result:", multimodal_result)

if __name__ == "__main__":
    asyncio.run(main())

 

