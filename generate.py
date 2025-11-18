def build_prompt(question, matches):
    summary = []
    for i, m in enumerate(matches, start=1):
        meta = m["metadata"]
        preview = meta.get("preview", "")

        summary.append({
            "snippet_id": m["id"],
            "job": meta.get("job_id"),
            "step": meta.get("step_name"),
            "status": meta.get("status"),
            "preview": preview
        })

    return {
        "question": question,
        "analysis": "Retrieved top matching CI/CD log chunks based on semantic BERT embeddings.",
        "snippets": summary
    }


def generate_answer(question, matches):
    """
    Return structured reasoning based ONLY on retrieved chunks.
    No LLM. No generation. Only metadata-based explanation.
    """
    prompt = build_prompt(question, matches)

    # basic heuristic analysis
    root_cause = "Unknown"
    explanation = "Not enough evidence found."
    fix = "Check CI/CD logs manually."

    for m in matches:
        meta = m["metadata"]
        text = meta.get("preview", "")

        if "ERROR" in text or meta.get("status") == "ERROR":
            root_cause = "Error detected in pipeline."
            explanation = f"Failure occurred in step '{meta.get('step_name')}' of job '{meta.get('job_id')}'."
            fix = "Inspect failing step’s logs and validate configuration/tests."
            break

        if "failed" in text.lower():
            root_cause = "A step failed."
            explanation = f"Log suggests failure in step '{meta.get('step_name')}'."
            fix = "Review error stack trace or command output."
            break

    return {
        "root_cause": root_cause,
        "explanation": explanation,
        "suggested_fix": fix,
        "matches_used": [m["id"] for m in matches],
        "structured": prompt
    }
