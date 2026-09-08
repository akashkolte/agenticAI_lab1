from agent import run_agent

questions = [
    "What is 1247 divided by 43, rounded to 2 decimals?",  # calculator
    "What does the file 'course_info.txt' say?",           # file_reader
    "Tell me something about the University at Buffalo.",   # lookup
    "Read 'numbers.txt' and sum all numbers in it.",       # two steps
    "What is the meaning of life?",                        # ambiguous -> fail
    "Read the file 'secrets.txt' and summarize it.",       # missing -> fail
]
for q in questions:
    result = run_agent(q, verbose=True)
    # save each full trace to a log file in logs/
