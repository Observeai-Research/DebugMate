import os
from leetcode_hard_gym_main.leetcode_env.environment import LeetCodeEnv
from leetcode_hard_gym_main.leetcode_env.types import (
    LeetCodeSubmission,
    ProgrammingLanguage,
)


# LEETCODE_CSRF_TOKEN
LEETCODE_SESSION_COOKIE = os.environ["LEETCODE_SESSION"]


class LeetCodeTester(object):
    def __init__(self):
        os.environ["LEETCODE_SESSION"] = LEETCODE_SESSION_COOKIE

        self.env = LeetCodeEnv(cooldown=15)
        self.lang_dict = {
            "python3": ProgrammingLanguage.PYTHON3,
            "java": ProgrammingLanguage.JAVA,
            "cpp": ProgrammingLanguage.CPP,
        }

    def test(self, code: str, task_id: str, language: str) -> tuple[bool, dict]:
        lang = self.lang_dict.get(language)
        sub = LeetCodeSubmission(code=code, lang=lang, question_slug=task_id)
        status, reward, done, submission_result = self.env.step(sub)
        return reward, submission_result


if __name__ == "__main__":
    from agents.debugmate_agent import DebugMateAgent
    from debugbench_source import python_condition_errors

    lang = "python3"
    error_type = "python_condition"
    with open(f"debugbench_results/{error_type} score.txt", "w") as f:
        f.write(f"{error_type} results")
    with open("debugbench_results/output.txt", "w") as f:
        f.write(f"{error_type} output")
    for error in python_condition_errors:
        debugmate_agent = DebugMateAgent(model="gpt-4-0613", temp=0.1, streaming=False)
        prompt = f"""
            "description": "{error['description']}",
            "examples": {error['examples']},
            "constraints": "{error['constraints']}",
            "buggy_code": "{error['buggy_code']}"
            Fix the buggy {lang} code and return exactly the correct code as your final answer and nothing else.
            DO NOT use Code Search as all the code is provided in "buggy code".
            For example, you final answer should look like:
            "class Solution ... "
            No comments allowed. You are NOT allowed to use Confluence Search or Code Search in this question.
            Only include the solution class, DO NOT include any other classes in your answer.
        """
        # Some DebugBench 'java' errors accidentally have python code in them
        # if "def " in error['buggy_code']:
        #     with open("debugbench_results/java_variable score.txt", "a") as f:
        #         f.write("\nNA ('def' in code)")
        #     continue
        code = debugmate_agent.run(prompt)
        print(code)
        start_index = code.find("class")
        code = code[start_index:]
        end_index = code.find("```")
        code = code[:end_index]
        print(code)
        tester = LeetCodeTester()
        task_id = error["slug"]
        result = tester.test(code, task_id, lang)
        print(result)
        try:
            print(result[0], result[1]["total_correct"], result[1]["total_testcases"])
            with open(f"debugbench_results/{error_type} score.txt", "a") as f:
                f.write(
                    "\n"
                    + str(result[1]["total_correct"] / result[1]["total_testcases"])
                )
            print(result[1]["total_correct"] / result[1]["total_testcases"])
        except Exception:
            print("error")
            with open(f"debugbench_results/{error_type} score.txt", "a") as f:
                f.write("\nerror: " + str(result))
        with open("debugbench_results/output.txt", "a") as f:
            f.write(f"\n{result}")
