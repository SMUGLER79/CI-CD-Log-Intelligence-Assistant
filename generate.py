import json
import requests
from typing import Optional, List, Dict

OLLAMA_MODEL = "llama3.1"
OLLAMA_URL = "http://localhost:11434/api/generate"

def build_prompt(question: str, matches: List[Dict]) -> str:
    prompt = (
        "You are a CI/CD debugging assistant.\n"
        "Use ONLY the provided log snippets to answer the question.\n"
        "Structure the response with: root cause -> short explanation -> concrete fix steps -> snippet ids used.\n\n"
        f"Question: {question}\n\n"
        "Snippets:\n"
    )

    for i, m in enumerate(matches, start=1):
        meta = m.get("metadata", {})
        preview = meta.get("preview", "").strip()
        prompt += (
            f"[SNIPPET {i} | id={m.get('id')} | job={meta.get('job_id')} | "
            f"step={meta.get('step_name')} | status={meta.get('status')}]\n"
            f"{preview}\n\n"
        )

    prompt += "\nAnswer:\n"
    return prompt

def generate_answer(
    question: str,
    matches: List[Dict],
    max_tokens: int = 400,
    temperature: float = 0.1
) -> Dict:
    """Uses Ollama local API to generate a grounded answer."""

    prompt = build_prompt(question, matches)

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "options": {"temperature": temperature, "num_predict": max_tokens}
    }

    resp = _post_ollama(payload)
    return {
        "answer": _parse_ollama_response(resp),
        "prompt": prompt
    }


def _post_ollama(payload: Dict) -> requests.Response:
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    except Exception as e:
        raise RuntimeError(f"Failed to contact Ollama at {OLLAMA_URL}: {e}")

    if resp.status_code != 200:
        raise RuntimeError(f"Ollama returned {resp.status_code}: {resp.text}")

    return resp


def _extract_answer(fragment) -> str: 
    if fragment is None:
        return ""
    if isinstance(fragment, list):
        return " ".join(map(str, fragment))
    return str(fragment)


def _parse_json_body(resp: requests.Response) -> Optional[str]:
    """Attempt normal JSON decoding."""
    try:
        data = resp.json()
        return _extract_answer(
            data.get("response")
            or data.get("text")
            or data.get("data")
        ).strip()
    except ValueError:
        return None


def _parse_streaming(resp: requests.Response) -> str:
    full_text = ""
    for line in resp.iter_lines(decode_unicode=True):
        if not line:
            continue

        try:
            obj = json.loads(line)
            chunk = obj.get("response") or obj.get("data") or obj.get("text")
            full_text += _extract_answer(chunk)

        except Exception:
            continue

    return full_text.strip()


def _parse_ollama_response(resp: requests.Response) -> str:
    direct = _parse_json_body(resp)
    if direct is not None:
        return direct

    try:
        return _parse_streaming(resp)

    except Exception as e:
        raise RuntimeError(f"Could not parse Ollama response: {e}")


def clean_matches(matches): 
    cleaned = []
    for m in matches:
        cleaned.append({
            "id": str(m.get("id")),
            "score": float(m.get("score", 0)),
            "metadata": {
                k: (str(v) if not isinstance(v, (int, float, str)) else v)
                for k, v in m.get("metadata", {}).items()
            }
        })

    return cleaned