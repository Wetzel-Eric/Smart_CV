import json

def save_feedback(feedback, record_id):
    with open("logs/user_feedback.jsonl", "a") as f:
        f.write(json.dumps({
            "record_id": record_id,
            **feedback
        }) + "\n")
