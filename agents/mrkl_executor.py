from typing import Dict, List, Tuple, Optional
import os
from langchain.schema import AgentAction, AgentFinish
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.agents.agent import AgentExecutor
from langchain_core.utils.input import get_color_mapping
from .prompts import BRANCHING_INSTRUCTIONS
import time
from typing import (
    Any,
)


class ExceptionTool(BaseTool):
    name = "_Exception"
    description = "Exception tool"

    def _run(self, query: str) -> str:
        print("exceptionTool _run query:", query)
        return query

    async def _arun(self, query: str) -> str:
        print("exceptionTool _arun query:", query)
        return query


class RetryAgentExecutor(AgentExecutor):
    """Agent executor that retries on output parser exceptions."""

    # for backwards compatibility
    handle_parsing_errors: bool = True

    def _call(
        self,
        inputs: Dict[str, str],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Run text through and get agent response."""
        # Construct a mapping of tool name to tool for easy lookup
        name_to_tool_map = {tool.name: tool for tool in self.tools}
        # We construct a mapping from each tool to a color, used for logging.
        color_mapping = get_color_mapping(
            [tool.name for tool in self.tools], excluded_colors=["green", "red"]
        )
        intermediate_steps: List[Tuple[AgentAction, str]] = []
        # Let's start tracking the number of iterations and time elapsed
        iterations = 0
        time_elapsed = 0.0
        start_time = time.time()
        import pickle

        with open(
            "agents/intermediate_steps/intermediate_steps_locations.pickle", "rb"
        ) as handle:
            intermediate_steps_locations = pickle.load(handle)
            # print("current intermediate_steps_locations:", intermediate_steps_locations)
        if intermediate_steps_locations:
            with open(
                f"agents/intermediate_steps/{intermediate_steps_locations[-1]}", "rb"
            ) as handle:
                intermediate_steps = pickle.load(handle)
                prompt_input = inputs["input"]
                prompt_input = prompt_input[prompt_input.find("\n\n") :]
                intermediate_steps.append(
                    (
                        AgentAction(
                            tool="special_instruction",
                            tool_input="",
                            log=BRANCHING_INSTRUCTIONS.format(
                                prompt_input=prompt_input
                            ),
                        ),
                        "",
                        # BRANCHING_INSTRUCTIONS.format(prompt_input=prompt_input)
                    )
                )
                """if input("print intermediate_steps? y or n: ") == "y":
                    for i in intermediate_steps:
                        # print("\n\n\n")
                        for c in i:
                            # print("\n")
                            # print(c)
                            pass"""
        else:
            pass
            # print("(empty) intermediate_steps: ", intermediate_steps)
        intermediate_steps_locations.append(str(len(intermediate_steps_locations) + 1))
        # print(f"appended to {intermediate_steps_locations}: {len(intermediate_steps_locations)}")
        with open(
            "agents/intermediate_steps/intermediate_steps_locations.pickle", "wb"
        ) as handle:
            pickle.dump(intermediate_steps_locations, handle)
        # We now enter the agent loop (until it returns something).
        while self._should_continue(iterations, time_elapsed):
            with open(
                f"agents/intermediate_steps/{intermediate_steps_locations[-1]}", "wb"
            ) as handle:
                # print("current intermediate_steps_locations:", intermediate_steps_locations)
                pickle.dump(intermediate_steps, handle)

            next_step_output = self._take_next_step(
                name_to_tool_map,
                color_mapping,
                inputs,
                intermediate_steps,
                run_manager=run_manager,
            )
            if isinstance(next_step_output, AgentFinish):
                try:
                    os.remove(
                        f"agents/intermediate_steps/{len(intermediate_steps_locations)}"
                    )
                    intermediate_steps_locations.pop()
                    # print("popped from intermediate_steps_locations: ", intermediate_steps_locations)
                except Exception:
                    # print("error removing", f"agents/intermediate_steps/{len(intermediate_steps_locations)}")
                    pass
                with open(
                    "agents/intermediate_steps/intermediate_steps_locations.pickle",
                    "wb",
                ) as handle:
                    # print("storing intermediate steps locations")
                    pickle.dump(intermediate_steps_locations, handle)
                # print("time_elapsed:", time_elapsed)
                return self._return(
                    next_step_output, intermediate_steps, run_manager=run_manager
                )
            """from openai import OpenAI
            import os
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            client = OpenAI()
            summary = []
            for i in range(len(next_step_output)):
                messages = [
                    {"role": "system", "content":
                        RMRKL_NEXT_STEP_INPUT.format(log=next_step_output[i][0].log,
                                                     tool_input=next_step_output[i][0].tool_input)},
                    {"role": "user", "content": next_step_output[i][1]},
                ]
                summary.append((
                    next_step_output[i][0],
                    client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages
                    ).choices[0].message.content
                ))
            if 'Could not parse LLM output' in next_step_output[-1][1]:
                summary = next_step_output[-1][1]"""
            intermediate_steps.extend(next_step_output)
            if len(next_step_output) == 1:
                next_step_action = next_step_output[0]
                # See if tool should return directly
                tool_return = self._get_tool_return(next_step_action)
                if tool_return is not None:
                    # print("time_elapsed:", time_elapsed)
                    return self._return(
                        tool_return, intermediate_steps, run_manager=run_manager
                    )
            iterations += 1
            time_elapsed = time.time() - start_time
            # print("time_elapsed:", time_elapsed)
        output = self.agent.return_stopped_response(
            self.early_stopping_method, intermediate_steps, **inputs
        )

        return self._return(output, intermediate_steps, run_manager=run_manager)
