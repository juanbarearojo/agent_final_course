import os
import logging
import gradio as gr
import requests
import pandas as pd

from agent import BasicAgent
from smolagents import OpenAIServerModel
from tools.utils import download_file

# --- Configure Logging ---
logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# --- Constants ---
DEFAULT_API_URL = "https://agents-course-unit4-scoring.hf.space"


def run_and_submit_all(profile: gr.OAuthProfile | None):
    if not profile:
        return "Please login to Hugging Face.", None

    username = profile.username.strip()
    logger.info(f"User logged in: {username}")

    # Instantiate model and agent
    try:
        api_key = os.getenv("clave_open_ai", "").strip()
        model = OpenAIServerModel(
            model_id="gpt-4.1-2025-04-14",
            api_key=api_key
        )
        agent = BasicAgent(model, max_steps=10)
        logger.info(f"Agent initialized with model {model.model_id}")
    except Exception as e:
        logger.error(f"Error initializing agent: {e}")
        return f"Initialization failed: {e}", None

    # Fetch questions
    questions_url = f"{DEFAULT_API_URL}/questions"
    logger.info(f"Fetching questions from: {questions_url}")
    try:
        resp = requests.get(questions_url, timeout=15)
        resp.raise_for_status()
        questions = resp.json()
        logger.info(f"Fetched {len(questions)} questions.")
    except Exception as e:
        logger.error(f"Failed to fetch questions: {e}")
        return f"Fetch error: {e}", None

    # Run agent on each question
    results = []
    answers_payload = []
    for item in questions:
        tid = item.get("task_id")
        text = item.get("question", "")
        file_name = item.get("file_name")
        path = None
        try:
            if file_name:
                path = download_file(f"{DEFAULT_API_URL}/files/{tid}", file_name)
            ans = agent(text, path)
            answers_payload.append({"task_id": tid, "submitted_answer": str(ans)})
            results.append({"Task ID": tid, "Answer": ans})
            logger.info(f"Answered task {tid}")
        except Exception as e:
            logger.warning(f"Agent error on {tid}: {e}")
            results.append({"Task ID": tid, "Answer": f"ERROR: {e}"})

    # Submit everything once
    submission = {
        "username": username,
        "agent_code": f"https://huggingface.co/spaces/{os.getenv('SPACE_ID')}/tree/main",
        "answers": answers_payload
    }
    submit_url = f"{DEFAULT_API_URL}/submit"
    logger.info(f"Submitting {len(answers_payload)} answers...")
    try:
        r = requests.post(submit_url, json=submission, timeout=30)
        r.raise_for_status()
        data = r.json()
        status = (
            f"Submission Successful: {data.get('score')}% "
            f"({data.get('correct_count')}/{data.get('total_attempted')})"
        )
        logger.info(status)
    except Exception as e:
        logger.error(f"Submission failed: {e}")
        status = f"Submit error: {e}"

    df = pd.DataFrame(results)
    return status, df


# --- Gradio Interface ---
with gr.Blocks() as demo:
    gr.Markdown("# Agent Runner")
    gr.LoginButton()
    run_btn = gr.Button("Run & Submit")
    status_out = gr.Textbox(interactive=False)
    df_out = gr.DataFrame()

    run_btn.click(fn=run_and_submit_all, outputs=[status_out, df_out])

if __name__ == "__main__":
    logger.info("Starting app...")
    demo.launch(debug=False, share=False)

