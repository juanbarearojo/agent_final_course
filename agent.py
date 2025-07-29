import os
from pathlib import Path
from typing import Optional
from smolagents import CodeAgent, PythonInterpreterTool, WikipediaSearchTool, VisitWebpageTool, FinalAnswerTool
from tools.utils import reverse_string, process_excel_file, is_text_file, execute_python_file
from tools.youtube import load_youtube
from tools.audio import transcribe_audio
from tools.web import optimized_web_search


class BasicAgent:
    def __init__(self, model, max_steps: int = 10):
        self._model = model
        self._agent = CodeAgent(
            tools=[
                PythonInterpreterTool(),
                WikipediaSearchTool(),
                VisitWebpageTool(),
                FinalAnswerTool(),
                optimized_web_search,
                reverse_string,
                process_excel_file,
                is_text_file,
                load_youtube,
                execute_python_file,
                transcribe_audio
            ],
            additional_authorized_imports=[
                '*', 'subprocess', 'markdownify', 'chess', 'random',
                'time', 'itertools', 'pandas', 'webbrowser', 'requests', 'csv', 'openpyxl', 'json', 'yaml'
            ],
            model=model,
            add_base_tools=True,
            max_steps=max_steps
        )
        print("BasicAgent initialized.")

    def __call__(self, question: str, file_path: Optional[str] = None) -> str:
        prompt = question
        if file_path and os.path.exists(file_path):
            try:
                file = Path(file_path)
                if is_text_file(file_path):
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        file_content = f.read()
                    if file.suffix == '.py':
                        prompt += f"\nAttached Python code file: {file_path}"
                    else:
                        prompt += f"\nAttached File Content:\n{file_content}"
                else:
                    if file.suffix == '.mp3':
                        prompt += (
                            "\nUse the 'transcribe_audio' tool to extract text from the mp3 file."
                            f"\nAttached mp3 file: {file_path}"
                        )
                    else:
                        prompt += f"\nAttached File Path: {file_path}"
            except Exception as e:
                print(f"Failed to read file: {e}")
        print(prompt)
        answer = self._agent.run(prompt)
        return answer
