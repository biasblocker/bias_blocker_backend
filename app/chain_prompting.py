import os
from typing import List, Any, Dict

import langchain
from dotenv import load_dotenv
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

langchain.verbose = True


def read_task_prompt(fname):
    with open(fname, 'r') as f:
        return f.read()


# prompt_task_2 = ChatPromptTemplate.from_template(read_task_prompt(fname='chain_prompts/prompts/task_2.txt'))


class BiasClassification(BaseModel):
    biased: bool = Field(description='if text is biased, it returns True. Otherwise, it returns False')


class BiasType(BaseModel):
    bias_type: str = Field(description='the detected bias type')
    span: str = Field(description='text span containing the bias')
    explanation: str = Field(description='explanation')


class BiasTypes(BaseModel):
    bias_types: List[BiasType]


class Revision(BaseModel):
    revised_article: str = Field(description="place here the revised article")


parser = PydanticOutputParser(pydantic_object=BiasTypes)
parser.get_format_instructions()

prompt_task_1 = ChatPromptTemplate.from_template(read_task_prompt(fname='prompts/chain_prompts/task_1.txt'),
                                                 partial_variables={
                                                     "format_instructions": parser.get_format_instructions()})

model = ChatOpenAI(temperature=0,
                   openai_api_key=os.getenv('OPENAI_API_KEY'),
                   model_name=os.getenv('CHATGPT_MODEL'),
                   verbose=True)

# model_parser = model | StrOutputParser()

article_input = {"article": RunnablePassthrough()}

chain_task_1 = prompt_task_1 | model | StrOutputParser()

# chain_task_2 = {"article": article_input, "language": chain_task_1} | prompt_task_2 | model | StrOutputParser()
#
# chain_task_3 = {"article": article_input, "language": chain_task_1,
#                 "entities": chain_task_2} | prompt_task_3 | model | StrOutputParser()

article = '''
The letter, is a follow-up to an initial letter Johnson sent after leading 64 House Republicans to Eagle Pass, Texas, in early January. In that initial letter, Johnson cited reporting from Breitbart News that the DHS took steps to hide the severity of the crisis from the Congressional delegation visit — commonly referred to as a CODEL in Washington. Johnson also raised questions about the DHS granting access to CBS cameras for a favorable piece on Mayorkas’s department while denying the Congressional delegation from taking photographs.
Mayorkas responded to that letter without providing the requested documents and information regarding the DHS’s preparation for the visit and whether the agency altered border enforcement for the Congressmen. According to Johnson’s follow-up letter:
Additionally, the DHS Response did not provide documents related to the transportation and release of illegal aliens in and around the Del Rio sector of the southwest border, or the Eagle Pass CBP facility, within the timeframe of our CODEL. The DHS Response also did not cite or produce documents related to any specific statute or regulation prohibiting Members from taking photos at a CBP facility, and merely made a passing reference to CBP “policy.” Lastly, the DHS Response made no attempt to explain the discrepancy between the media’s ability— specifically Face the Nation’s ability—to photograph a CBP facility, while elected Members were prohibited from doing the same.
Johnson and the two chairmen told Mayorkas they wanted answers within two weeks or they would utilize their subpoena powers.
Concerns about the collapse of the southern border have increased in Washington and throughout the nation, with the Congressmen’s letter stating the problem “is currently the number one issue that concerns the American people, whether they live in a border state or not.” They mention the killings of Kayla Hamilton and Laken Riley, both allegedly by foreign nationals illegally in the country who were released due to Biden-endorsed border and immigration policies.
'''


class CustomHandler(BaseCallbackHandler):
    def on_llm_start(
            self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        formatted_prompts = "\n".join(prompts)
        print(f"Prompt:\n{formatted_prompts}")


output = chain_task_1.invoke({"article": article})

print("result is here")
print(output)
