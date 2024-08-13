from agents import DebugMateAgent
import os
import glob
import pickle

# delete intermediate_steps from previous executions
files = glob.glob("agents/intermediate_steps/*")
for f in files:
    os.remove(f)

if not os.path.exists("agents/intermediate_steps"):
    os.makedirs("agents/intermediate_steps")

# save empty list in intermediate_steps_locations
with open(
    "agents/intermediate_steps/intermediate_steps_locations.pickle", "wb"
) as handle:
    pickle.dump([], handle, protocol=pickle.HIGHEST_PROTOCOL)

debugmate_agent = DebugMateAgent(model="gpt-4-0613", temp=0.1, streaming=False)

# optional stack trace
try:
    with open("tools/stack_trace.txt") as f:
        stack_trace = f.read()
except Exception:
    print("tools/stack_trace.txt not found. continuing without stack trace.")

print(
    debugmate_agent.run("""explain why this is happening and suggest what changes I should make.
                         During user sync process, some of the user ids in teams seem to be going missing.
                         start debugging with the <class_name> class <function_name> function.
                          """)
)
