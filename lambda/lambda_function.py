import base64
import json
import os
import re

import boto3

KB_ID = os.environ["KB_ID"]
MODEL_ID = os.environ.get("MODEL_ID", "amazon.nova-lite-v1:0")

agent = boto3.client("bedrock-agent-runtime")
bedrock = boto3.client("bedrock-runtime")

SYSTEM = (
    "You are an AWS CloudOps assistant for cloud administrators. Answer ONLY "
    "using the runbook excerpts provided. Give clear, numbered troubleshooting "
    "steps and include exact commands or console paths when the runbooks have "
    "them. If the answer is not in the excerpts, say you could not find it in "
    "the runbooks and suggest escalating to the Cloud Operations team."
)


def reply(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


NOT_FOUND = "I could not find this in the runbooks. Please escalate to the Cloud Operations team."

STOPWORDS = {"a", "an", "the", "do", "does", "i", "we", "my", "is", "are", "what", "how",
             "many", "much", "can", "get", "for", "of", "to", "in", "on", "it", "which", "me",
             "there", "any", "our", "you", "be", "will", "am", "have", "has"}


def tokens(text):
    return {w.strip("?.,!:()#").lower() for w in text.split()} - STOPWORDS


def best_section(question, results):
    # Fallback for runbooks: return the whole "## heading + steps" section that best matches the question
    words = tokens(question)
    best = (0, None, None)
    for text, source in results:
        for section in re.split(r"\n(?=#+ )", text):
            lines = section.strip().splitlines()
            # Skip the document title ("# Runbook: ...") and match the "## ..." sections
            if len(lines) < 2 or not lines[0].startswith("##"):
                continue
            score = 2 * len(words & tokens(lines[0])) + len(words & tokens(section))
            if score > best[0]:
                best = (score, section.strip(), source)
    if best[0] < 3:
        return None, []
    heading, *steps = best[1].splitlines()
    answer = re.sub(r"^[#\s\d.]+", "", heading) + "\n" + "\n".join(s for s in steps if s.strip())
    return answer[:1200], [best[2]] if best[2] else []


def best_sentences(question, results, n=2):
    # Fallback when the chat model is unavailable: pick the sentences that share the most words with the question
    words = {w.strip("?.,!").lower() for w in question.split()} - STOPWORDS
    scored = []
    for text, source in results:
        for s in re.split(r"(?<=[.!?])\s+", text):
            s = s.strip()
            if len(s) > 15:
                overlap = len(words & {w.strip("?.,!:").lower() for w in s.split()})
                scored.append((overlap, s, source))
    scored.sort(key=lambda x: -x[0])
    # Require a real match (2 shared words, or 1 for one-word questions), otherwise say we could not find it
    if not scored or scored[0][0] < min(2, len(words)):
        return None, []
    top = [x for x in scored[:n] if x[0] == scored[0][0]]
    return " ".join(x[1] for x in top), sorted({x[2] for x in top if x[2]})


def get_question(event):
    # From POST body (JSON, possibly base64-encoded by the Function URL)
    body = event.get("body")
    if body:
        if event.get("isBase64Encoded"):
            body = base64.b64decode(body).decode("utf-8")
        try:
            question = json.loads(body).get("question")
            if question:
                return question.strip()
        except (json.JSONDecodeError, AttributeError):
            pass
    # From query string (?question=...)
    return ((event.get("queryStringParameters") or {}).get("question") or "").strip()


def lambda_handler(event, context):
    question = get_question(event)
    if not question:
        return reply(400, {"error": "Please send a question."})

    # Step 1: retrieve the most relevant runbook chunks from the Knowledge Base
    r = agent.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalQuery={"text": question},
    )
    results = []
    for item in r.get("retrievalResults", []):
        text = item.get("content", {}).get("text", "")
        uri = item.get("location", {}).get("s3Location", {}).get("uri", "")
        results.append((text, uri.split("/")[-1] if uri else ""))

    if not results:
        return reply(200, {"answer": NOT_FOUND, "sources": []})
    chunks = [text for text, _ in results]
    sources = sorted({src for _, src in results if src})

    # Step 2: ask the chat model to answer using only those chunks
    prompt = "Runbook excerpts:\n" + "\n\n---\n\n".join(chunks) + f"\n\nQuestion: {question}"
    try:
        resp = bedrock.converse(
            modelId=MODEL_ID,
            system=[{"text": SYSTEM}],
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 500, "temperature": 0.1},
        )
        answer = resp["output"]["message"]["content"][0]["text"]
    except Exception as e:
        print(f"Chat model unavailable, using extractive fallback: {e}")
        answer, sources = best_section(question, results)
        if not answer:
            answer, sources = best_sentences(question, results)
        if not answer:
            return reply(200, {"answer": NOT_FOUND, "sources": []})

    return reply(200, {"answer": answer, "sources": sources})
