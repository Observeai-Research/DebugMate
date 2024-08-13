# DebugBench Evaluation

Evaluate DebugMate using DebugBench with the following steps:

## Setup

1. **LeetCode Account**: Log in to LeetCode

2. **EditThisCookie Browser Extension**: Install from https://chromewebstore.google.com/detail/fngmhnnpilhplaeedifhccceomclgfbg

3. **Retrieve Tokens**:
    - Open any LeetCode problem
    - Use EditThisCookie to find `LEETCODE_SESSION` and `LEETCODE_CSRF_TOKEN`

4. **Set Environment Variables**:
    ```sh
    export LEETCODE_SESSION="<leetcode_session>"
    export LEETCODE_CSRF_TOKEN="<csrf_token>"
    ```

## Instructions

1. **Paste DebugBench Error**:
    - Open `debugbench_source.py` and paste the errors (e.g., `python_condition_errors` is a list of all python_condition errors)

2. **Import Error in `debugbench_eval.py`**:
    - Import the specific error list
    - Set `lang` to `python3`, `java`, or `cpp`
    - Set `error_type` for naming the result file

3. **Run Evaluation**:
    ```sh
    python debugbench_eval.py
    ```

4. **View Results**:
    - Results will be stored in `debugbench_results/<error_type>_score.txt`

## Example

1. **Set Environment Variables**:
    ```sh
    export LEETCODE_SESSION="your_leetcode_session"
    export LEETCODE_CSRF_TOKEN="your_leetcode_csrf_token"
    ```

2. **Paste Error**:
    ```python
    # debugbench_source.py
    python_condition_errors = [
        # Error details
    ]
    ```

3. **Import and Set Parameters**:
    ```python
    # debugbench_eval.py
    from debugbench_source import python_condition_errors

    lang = "python3"
    error_type = "python_condition"
    ```

4. **Run**:
    ```sh
    python debugbench_eval.py
    ```

5. **View Results**:
    - Check `debugbench_results/python_condition_score.txt`
