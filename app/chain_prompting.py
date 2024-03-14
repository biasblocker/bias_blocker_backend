import os
from enum import Enum
from typing import List, Optional

import langchain_core
from dotenv import load_dotenv
from langchain.cache import SQLiteCache
from langchain.chat_models import ChatOpenAI
from langchain.globals import set_llm_cache
from langchain.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from sentencex import segment

load_dotenv()
set_llm_cache(SQLiteCache(database_path=".langchain.db"))


def read_task_prompt(fname):
    with open(fname, 'r') as f:
        return f.read()


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
    bias_topics: Optional[List[BiasTopic]] = Field(
        description='bias topics that are gender, ethnicity/race, age, migration, religion, political')
    bias_types: Optional[List[BiasType]] = Field(description='List of bias types that is seen in the text')


class Revision(BaseModel):
    revised_article: str = Field(description="place here the revised article")


class ChatGPTChain:
    def __init__(self):
        bias_parser = PydanticOutputParser(pydantic_object=BiasTypes)
        bias_parser.get_format_instructions()
        prompt_task_1 = ChatPromptTemplate.from_template(read_task_prompt(fname='prompts/chain_prompts/task_1.txt'),
                                                         partial_variables={
                                                             "format_instructions": bias_parser.get_format_instructions()})

        revision_parser = PydanticOutputParser(pydantic_object=Revision)
        revision_parser.get_format_instructions()

        prompt_task_2 = ChatPromptTemplate.from_template(read_task_prompt(fname='prompts/chain_prompts/task_2.txt'),
                                                         partial_variables={
                                                             "format_instructions": revision_parser.get_format_instructions()})

        prompt_task_3 = ChatPromptTemplate.from_template(read_task_prompt(fname='prompts/chain_prompts/task_3.txt'))

        model = ChatOpenAI(temperature=0.7,
                           openai_api_key=os.getenv('OPENAI_API_KEY'),
                           model_name=os.getenv('CHATGPT_MODEL'),
                           verbose=True)
        self.bias_types = read_task_prompt(fname='prompts/chain_prompts/bias_types.txt')
        self.temperature = os.environ["OPENAI_TEMPERATURE"]
        self.chain_task_1 = prompt_task_1 | model | bias_parser
        self.chain_task_2 = prompt_task_2 | model | revision_parser
        self.chain_task_3 = prompt_task_3 | model | JsonOutputParser()

    def aggregate_results(self, full_article, results):
        aggregated_result = {}
        aggregated_result["biased"] = True
        bias_topics = list()
        bias_types = list()
        for result in results:
            bias_topics.extend(result['bias_topics'])
            bias_types.extend(result['bias_types'])

            full_article = full_article.replace(result['sentence'], result["revised_article"])

        # comment out if you want to assign the most common
        # aggregated_result['bias_topics'] =  max(set(bias_topics), key=bias_topics.count)

        aggregated_result['bias_topics'] = list(set(bias_topics))
        aggregated_result['bias_types'] = bias_types
        aggregated_result['revised_article'] = full_article

        return aggregated_result

    def inference(self, query):
        full_article = query
        sentences = list(segment("en", query))

        results = []
        for sentence in sentences:
            if len(sentence) <= 2:
                # potentially it will create hallucinations
                continue
            sentence = sentence.rstrip()

            if len(sentence) == 0:
                print("it is not a sentence, a whitespace.")
                continue
            try:
                output = self.chain_task_1.invoke({"bias_types": self.bias_types, "article": sentence})
                output = output.dict()
                if output["bias_topics"]:
                    output["bias_topics"] = list(map(lambda x: x.value, output["bias_topics"]))
            except langchain_core.exceptions.OutputParserException as e:
                output = self.chain_task_3.invoke({"json_input": output})

            if bool(output["biased"]):
                detected_bias_spans = ''
                for detected_bias in output['bias_types']:
                    bias_span = detected_bias['span']
                    detected_bias_spans += f'{bias_span}\n'

                    try:
                        revised_from_model = self.chain_task_2.invoke(
                            {"detected_bias_spans": detected_bias_spans, "article": sentence})
                        revised_from_model = revised_from_model.dict()
                    except langchain_core.exceptions.OutputParserException as e:
                        revised_from_model = self.chain_task_3.invoke({"json_input": revised_from_model})
                output["revised_article"] = revised_from_model["revised_article"]
                output["sentence"] = sentence
                results.append(output)
        if len(results) > 0:
            output = self.aggregate_results(full_article, results)
        else:
            output = {
                "biased": "biased",
                "bias_types": [],
                "bias_topic": [],
                "revised_article": None,
                "model_raw_output": None,
            }

        return output, None


if __name__ == '__main__':
    prompt = '''An Israeli hostage freed from Gaza three months ago has accused the world of forgetting those still held by Hamas and urged the Israeli government to do whatever it takes to bring them home.  Itay Regev, 19, told the BBC he was held in "horrific" conditions by "very, very vicious" captors and he did not think he would get out alive.  He was kidnapped from the Nova music festival with his sister and a friend.  Talks on a ceasefire and hostage exchange have been ongoing for weeks.  But as yet there is no deal, with reported sticking points including Hamas's demand for a permanent ceasefire and Israeli troop withdrawal from Gaza, which Israeli Prime Minister Benjamin Netanyahu has called "delusional".  However, Itay - who was released along with his sister, Maya, and 103 other hostages in return for some 240 Palestinian prisoners in Israeli jails during a brief truce in November - is clear about what needs to happen.  "I think we should do anything we possibly can to get them out of there, whatever the cost... It's people's lives," he said, speaking to the BBC in London in his first UK interview.  "I'm sure if anyone had their child kidnapped, they wouldn't really care about what price needed to be paid. We need to return the hostages at any cost."  About 130 hostages, including Itay's friend Omer, are still being held in Gaza. Israeli officials have said they believe about 30 of those still in Gaza are dead.  Itay is in London to raise their plight with British MPs - he said he was there to "scream their cries from Gaza" - and wants the international community to do more to secure their release.  "The hostages have been there for five months now. The answer is unequivocally, no they're not doing enough," he said.  "For five months not to see the sunlight and you don't know what's happening with your family, for five months to be in horrific conditions and hungry... They have to be taken out of there as quickly as possible. They have the horrible feeling of not knowing what their fate will be from one second to the next."  Describing his 54 days of captivity, Itay said he had to come to terms with the fact that he might be killed.  "We were very, very hungry. I didn't have a shower for 54 days. My captors were very, very vicious. They didn't care. I had wounds in my legs, big holes in my legs.  "And you lived there in a horrific sense of fear. Every second that you live with this feeling is a terrible feeling, that you don't really know if you're going to wake up in the morning, or in a minute, if a missile is going to fall on you, if they're going to come in with a Kalashnikov and start spraying us with bullets. The conditions are very, very difficult there."'''

    client = ChatGPTChain()
    output, _ = client.inference(prompt)

    print(output)
