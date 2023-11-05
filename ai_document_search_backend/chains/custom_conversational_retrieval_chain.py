from __future__ import annotations

from typing import Any, Dict, List, Optional


from langchain.schema import BaseRetriever
from langchain.schema.language_model import BaseLanguageModel
from langchain.callbacks.manager import (
    CallbackManagerForChainRun,
)
from langchain.chains.base import Chain
from langchain.prompts.base import BasePromptTemplate
from langchain.prompts import PromptTemplate
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.llm import LLMChain


class CustomConversationalRetrievalChain(Chain):
    prompt: BasePromptTemplate = PromptTemplate.from_template("{question}")
    llm: BaseLanguageModel
    condense_question_llm: BaseLanguageModel
    retriever: BaseRetriever
    output_key: str = "text"

    class Config:
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        return self.prompt.input_variables

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        # Condense chat history into single prompt to condense it to a single question

        question = inputs["question"]
        if run_manager:
            run_manager.on_text("\nQuestion:\n" + question)

        chat_history = inputs["chat_history"]
        if len(chat_history) > 4:
            chat_history = chat_history[-4:]
        chat_history_str = ""
        for chat in chat_history:
            chat_str = ""
            chat_str += "Question: " + chat[0] + "\n"
            chat_str += "Answer: " + chat[1] + "\n"
            chat_str += "\n"
            chat_history_str += chat_str

        new_question = question

        if len(chat_history) > 0:
            callbacks = run_manager.get_child()
            question_generator = LLMChain(
                llm=self.condense_question_llm,
                prompt=CONDENSE_QUESTION_PROMPT,
                callbacks=callbacks,
            )
            new_question = question_generator.run(
                question=question, chat_history=chat_history_str, callbacks=callbacks
            )

        # Pass question to retriever
        docs = self.retriever.get_relevant_documents(
            new_question, callbacks=run_manager.get_child()
        )

        if run_manager:
            run_manager.on_text("\nNew question:\n" + new_question)

        # Construct prompt containing metadata and content of retrieved documents
        prompt_template = PromptTemplate.from_template(
            """Answer the question using the context given below, or using your own knowledge. Refer to the origin of your knowledge using the isin, page and shortname in a natural way. If you can't find an answer, say that you don't know. Do not make things up.
        
        Context:
        {context}
                                                       
        Question:
        {question}
                                                       
        Answer:
        """
        )

        context = ""
        for i in range(len(docs)):
            source = docs[i]
            source_string = ""
            source_string += f"Shortname: {source.metadata['shortname']}\n"
            source_string += f"ISIN: {source.metadata['isin']}\n"
            source_string += f"Page: {source.metadata['page']+1}\n"
            source_string += f"Content: {source.page_content}"
            source_string += "\n"
            context += source_string

        prompt_value = prompt_template.format_prompt(context=context, question=new_question)
        if run_manager:
            run_manager.on_text("\nPrompt:\n" + prompt_value.text)

        # Generate response using LLM
        response = self.llm.generate_prompt(
            [prompt_value], callbacks=run_manager.get_child() if run_manager else None
        )

        if run_manager:
            run_manager.on_text("\nAnswer:\n" + str(response.generations[0][0].text))

        return {
            self.output_key: {"answer": response.generations[0][0].text, "source_documents": docs}
        }

    @property
    def _chain_type(self) -> str:
        return "chain_including_metadata_in_context"
