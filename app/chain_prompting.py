import os
import json
from enum import Enum
from typing import List

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough
from sentencex import segment

load_dotenv()


# langchain.verbose = True


def read_task_prompt(fname):
    with open(fname, 'r') as f:
        return f.read()


# prompt_task_2 = ChatPromptTemplate.from_template(read_task_prompt(fname='chain_prompts/prompts/task_2.txt'))


class BiasType(BaseModel):
    bias_type: str = Field(description='the detected bias type')
    span: str = Field(description='text span containing the bias')
    explanation: str = Field(description='explanation')


class BiasTopic(Enum):
    GENDER = 'gender'
    ETHINICITY_RACE = 'ethnicity/race'
    AGE = 'age'
    MIGRATION = 'migration'
    RELIGION = 'religion'
    POLITICAL = 'political'


class BiasTypes(BaseModel):
    biased: bool = Field(description='if text is biased, return True. Otherwise, it returns False')
    bias_topics: List[BiasTopic] = Field(
        description='bias topics that are gender, ethnicity/race, age, migration, religion, political')
    bias_types: List[BiasType] = Field(description='List of bias types that is seen in the text')


class Revision(BaseModel):
    revised_article: str = Field(description="place here the revised article")


bias_parser = PydanticOutputParser(pydantic_object=BiasTypes)
bias_parser.get_format_instructions()

bias_types = read_task_prompt(fname='prompts/chain_prompts/bias_types.txt')
prompt_task_1 = ChatPromptTemplate.from_template(read_task_prompt(fname='prompts/chain_prompts/task_1.txt'),
                                                 partial_variables={
                                                     "format_instructions": bias_parser.get_format_instructions()})


revision_parser = PydanticOutputParser(pydantic_object=Revision)
revision_parser.get_format_instructions()

prompt_task_2 = ChatPromptTemplate.from_template(read_task_prompt(fname='prompts/chain_prompts/task_2.txt'),
                                                 partial_variables={
                                                     "format_instructions": revision_parser.get_format_instructions()})

model = ChatOpenAI(temperature=0.7,
                   openai_api_key=os.getenv('OPENAI_API_KEY'),
                   model_name=os.getenv('CHATGPT_MODEL'),
                   verbose=True)

# model_parser = model | StrOutputParser()

chain_task_1 = prompt_task_1 | model | StrOutputParser()
chain_task_2 = prompt_task_2 | model | StrOutputParser()

article = '''
The letter, is a follow-up to an initial letter Johnson sent after leading 64 House Republicans to Eagle Pass, Texas, in early January. In that initial letter, Johnson cited reporting from Breitbart News that the DHS took steps to hide the severity of the crisis from the Congressional delegation visit — commonly referred to as a CODEL in Washington. Johnson also raised questions about the DHS granting access to CBS cameras for a favorable piece on Mayorkas’s department while denying the Congressional delegation from taking photographs.
Mayorkas responded to that letter without providing the requested documents and information regarding the DHS’s preparation for the visit and whether the agency altered border enforcement for the Congressmen. According to Johnson’s follow-up letter:
Additionally, the DHS Response did not provide documents related to the transportation and release of illegal aliens in and around the Del Rio sector of the southwest border, or the Eagle Pass CBP facility, within the timeframe of our CODEL. The DHS Response also did not cite or produce documents related to any specific statute or regulation prohibiting Members from taking photos at a CBP facility, and merely made a passing reference to CBP “policy.” Lastly, the DHS Response made no attempt to explain the discrepancy between the media’s ability— specifically Face the Nation’s ability—to photograph a CBP facility, while elected Members were prohibited from doing the same.
Johnson and the two chairmen told Mayorkas they wanted answers within two weeks or they would utilize their subpoena powers.
Concerns about the collapse of the southern border have increased in Washington and throughout the nation, with the Congressmen’s letter stating the problem “is currently the number one issue that concerns the American people, whether they live in a border state or not.” They mention the killings of Kayla Hamilton and Laken Riley, both allegedly by foreign nationals illegally in the country who were released due to Biden-endorsed border and immigration policies.
'''

sentences = list(segment("en", article))
for sentence in sentences:
    sentence = sentence.rstrip()

    if len(sentence) == 0:
        print("it is not a sentence, a whitespace.")
        continue

    output = chain_task_1.invoke({"bias_types": bias_types, "article": sentence})

    output = output.replace('```json', '').replace('`','')

    output = json.loads(output)
    output["input"] = sentence

    if bool(output["biased"]):
        detected_bias_spans = ''
        for detected_bias in output['bias_types']:
            bias_span = detected_bias['span']
            detected_bias_spans += f'{bias_span}\n'
            revised_from_model = chain_task_2.invoke({"detected_bias_spans": detected_bias_spans, "article": sentence})
            revised_from_model = revised_from_model.replace('```json', '').replace('`', '')
            revised_from_model = json.loads(revised_from_model)
        output["revised_article"] = revised_from_model["revised_article"]

    print("===output===")
    print(output)