import unittest

import diff_match_patch as dmp_module


class TestParser(unittest.TestCase):

    def test_diff_text(self):
        dmp = dmp_module.diff_match_patch()
        # 1 means added, 0 means no change, -1 means remove

        sentence = "Itay Regev, 19, told the BBC he was held in \"horrific\" conditions by \"very, very vicious\" captors and he did not think he would get out alive."
        revised_sentence = "Itay Regev, 19, told the BBC he was held in conditions by captors and he did not think he would get out alive."

        diff = dmp.diff_main(sentence, revised_sentence)
        # Result: [(-1, "Hell"), (1, "G"), (0, "o"), (1, "odbye"), (0, " World.")]
        dmp.diff_cleanupSemantic(diff)
        # Result: [(-1, "Hello"), (1, "Goodbye"), (0, " World.")]
        print(diff)




if __name__ == '__main__':
    unittest.main()
