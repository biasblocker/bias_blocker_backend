import unittest
import json


class TestParser(unittest.TestCase):

    def test_parser_func(self):
        test_text = """
    {
    "input": "On the heels of winning the female Ballon d’Or award on Monday, Rapinoe demanded that male soccer stars speak up on her political causes.",
    "revised_article": "After being awarded the Ballon d’Or on Monday, Rapinoe called for male soccer stars to voice their support for her political beliefs.",
    "bias_types": [
    {
    "type": "Framing Bias",
    "explanation": "The word 'demanded' implies a sense of entitlement and urgency, potentially framing Rapinoe as aggressive or confrontational. The revised phrase 'called for' maintains the same meaning while avoiding this connotation."
    },
    {
    "type": "Demographic Bias",
    "explanation": "The phrase 'male soccer stars' could be seen as reinforcing gender divisions and stereotypes. The revised phrase 'soccer stars' omits this potential bias."
    }
    ]
    }
    
    Explanation:
    
    The original sentence contains two potential biases. First, the word "demanded" could be seen as framing Rapinoe's request as aggressive or confrontational, rather than simply expressing her opinion. The revised phrase "called for" maintains the same meaning while avoiding this connotation.
    
    Second, the phrase "male soccer stars" could be seen as reinforcing gender divisions and stereotypes. The revised phrase "soccer stars" omits this potential bias by using a more inclusive term that encompasses all soccer players, regardless of gender.
    """

        # print(test_text)

        generated_output = parse_output(input_text=test_text.strip())
        desired_output = json.loads("""    {
    "input": "On the heels of winning the female Ballon d’Or award on Monday, Rapinoe demanded that male soccer stars speak up on her political causes.",
    "revised_article": "After being awarded the Ballon d’Or on Monday, Rapinoe called for male soccer stars to voice their support for her political beliefs.",
    "bias_types": [
    {
    "type": "Framing Bias",
    "explanation": "The word 'demanded' implies a sense of entitlement and urgency, potentially framing Rapinoe as aggressive or confrontational. The revised phrase 'called for' maintains the same meaning while avoiding this connotation."
    },
    {
    "type": "Demographic Bias",
    "explanation": "The phrase 'male soccer stars' could be seen as reinforcing gender divisions and stereotypes. The revised phrase 'soccer stars' omits this potential bias."
    }
    ]
    }""")
        self.assertEqual(generated_output, desired_output)

        test_text = """{
"input": "Orange Is the New Black" star Yael Stone is renouncing her U.S. green card to return to her native Australia in order to fight climate change.
"biased": yes
"revised_article": "Yael Stone, known for her role in 'Orange Is the New Black,' has announced her decision to renounce her U.S. green card and return to her native Australia in order to combat climate change."
"bias_topic": ["migration"]
"bias_types":
[
{
"bias_type": "framing bias - word choice",
"span": "renouncing her U.S. green card",
"explanation": "The use of the word 'renouncing' implies a negative connotation and could be seen as taking a political stance on the issue of immigration."
},
{
"bias_type": "framing bias - labeling",
"span": "in order to fight climate change",
"explanation": "The phrase 'in order to fight climate change' could be seen as implying that the author supports
"""

    desired_output = json.loads("""{
       "input": "Orange Is the New Black" star Yael Stone is renouncing her U.S. green card to return to her native Australia in order to fight climate change.",
"biased": yes,
"revised_article": "Yael Stone, known for her role in 'Orange Is the New Black,' has announced her decision to renounce her U.S. green card and return to her native Australia in order to combat climate change.",
"bias_topic": ["migration"],
"bias_types":
[
{
"bias_type": "framing bias - word choice",
"span": "renouncing her U.S. green card",
"explanation": "The use of the word 'renouncing' implies a negative connotation and could be seen as taking a political stance on the issue of immigration."
},
{
"bias_type": "framing bias - labeling",
"span": "in order to fight climate change",
"explanation": "The phrase 'in order to fight climate change' could be seen as implying that the author supports}}
       """)


if __name__ == '__main__':
    unittest.main()
