import logging
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FINAL_INSTRUCTION = """Perform a comprehensive review, following all instructions of the given, 
        then produce MDX documentation.
        """

READ_CODE = """
        Read the code provided, and then perform a comprehensive evaluation.
        Write a documentation with the following sections:
            1. Element Details: Answer the following for each element (function/class):
                - What is the element for?
                - What actions can it perform?
                - How can one implement their own?
                - Provide sample code implementation. 
            2. Simple Example: Provide a simple example of how to use the element.

            
        The top of each MDX output shall contain the following elements and in this format:
        ---
        title: [the class or module name]
        description: [One sentense describing the content]
        ---
        THE ONLY OUTPUT IS MDX DOCUMENTATION.
    """

READ_FILE_CODE_WELCOME = """
    Write a documentation with the following sections:
        1. Introduction: A brief introduction to the code.
        2. Overview: A general overview of what the code does.

    Skip the following:
        - Running Tests or anything concernting tests
        - Code Structure
        - Copyright and License
        - Conclusion or Footnotes

    The top of MDX output shall contain the following elements and in this format:
        ---
        title: "MAUD"
        sidebarTitle: "Welcome"
        description: [One sentense describing the content]
        ---
    THE ONLY OUTPUT IS MDX DOCUMENTATION.
    """

READ_FILE_CODE_QUICK = """
    Write a documentation with the following sections:
        1. Introduction: A brief introduction on this quickstart.
        2. Quickstarts: Simple examples or use cases.

    Skip the following:
        - Running Tests or anything concernting tests
        - Code Structure
        - Copyright and License
        - Conclusion or Footnotes

    The top of MDX output shall contain the following elements and in this format:
        ---
        title: "Quick Start"
        description: [One sentense describing the content]
        ---
    THE ONLY OUTPUT IS MDX DOCUMENTATION.
    """

READ_FILE_WHAT_IS_IT = """
    Write a documetation for this code descibing what it is. You are answering the question:
    What is this code?

    Skip the following:
        - Running Tests or anything concernting tests
        - Code Structure
        - Copyright and License
        - Conclusion or Footnotes

        
    The top of MDX output shall contain the following elements and in this format:
        ---
        title: "what Is It?"
        description: [One sentense describing the content]
        ---
    THE ONLY OUTPUT IS MDX DOCUMENTATION.
    """

READ_FILE_HOW_IT_WORKS = """
    Write a documetation for this code descibing how it works. You are answering the question:
    How does this work?

    Skip the following:
        - Running Tests or anything concernting tests
        - Code Structure
        - Copyright and License
        - Conclusion or Footnotes

    The top of MDX output shall contain the following elements and in this format:
        ---
        title: "How Does It Work?"
        description: [One sentense describing the content]
        ---
    THE ONLY OUTPUT IS MDX DOCUMENTATION.
    """

class AIDocumentationGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.client = OpenAI()
        self.model="gpt-4-1106-preview"
        self.max_requests_per_minute = (
            20  # change this only if you know they should be different
        )
        self.max_tokens_per_minute = (
            40000  # change this only if you know they should be different
        )
        self.available_request_capacity = self.max_requests_per_minute
        self.available_token_capacity = self.max_tokens_per_minute
        self.last_update_time = time.time()
        self.logger.info("Initialized")

    def wait_for_rate_limit(self):
        self.logger.debug("Waiting for rate limit availability")
        while True:
            current_time = time.time()
            seconds_since_update = current_time - self.last_update_time

            self.available_request_capacity = min(
                self.available_request_capacity
                + self.max_requests_per_minute * seconds_since_update / 60.0,
                self.max_requests_per_minute,
            )
            self.available_token_capacity = min(
                self.available_token_capacity
                + self.max_tokens_per_minute * seconds_since_update / 60.0,
                self.max_tokens_per_minute,
            )

            if (
                self.available_request_capacity >= 1
                and self.available_token_capacity >= 1000
            ):  # Assuming 1000 tokens per request
                self.available_request_capacity -= 1
                self.available_token_capacity -= (
                    1000  # Deduct estimated tokens used per request
                )
                self.last_update_time = current_time
                self.logger.debug(
                    "Available request capacity: %s, token capacity: %s",
                    self.available_request_capacity,
                    self.available_token_capacity,
                )
                break

            time.sleep(1)

    def openai_chat_completion(self, messages):
        self.logger.debug("OpenAI Chat Completion")
        # self.wait_for_rate_limit()
        
        responses = self.client.chat.completions.create(
            model=self.model, 
            messages=messages,
            # temperature=0,
        )
        results = [
            choice.message.content.strip()
            for choice in responses.choices
            if choice.message.role == "assistant"
        ]
        self.logger.debug("OpenAI Chat Completion results: %s", results)
        return results
    
    def generate_codebase_overview_prompt(self, codebase_structure):
        self.logger.debug("Generating codebase overview prompt")
        prompt = "Generate a comprehensive documentation for a Python codebase. Here is an overview of the codebase structure:\n\n"

        for file_path, code_content in codebase_structure.items():
            module_path = file_path.replace('/', ' > ').replace('.py', '')
            prompt += f"### {module_path}\n"
            prompt += f"```python\n{code_content}\n```\n\n"

        self.logger.debug(f"Generated prompt (first 500 characters): {prompt[:500]}...")
        return prompt

    def generate_file_documentation(self, code_info):
        system_message = READ_CODE

        prompt = f"""
        Analyze this code:

        {code_info}

        {READ_CODE}
        """

        messages = [{
            'role': 'system',
            'content': system_message
        }, {
            'role': 'user',
            'content': prompt
        }]

        self.logger.debug("OpenAI Chat Completion messages: %s", messages)

        return self.openai_chat_completion(messages)
    
    def generate_custom_docs(self, all_code, doc_type):
        self.logger.debug("Generating custom docs")
        self.logger.debug("Doc type: %s", doc_type)
        
        system_message = ""  # Initialize system message variable

        if doc_type == "welcome":
            system_message = READ_FILE_CODE_WELCOME
        elif doc_type == "quickstart":
            system_message = READ_FILE_CODE_QUICK
        elif doc_type == "what-is-it":
            system_message = READ_FILE_WHAT_IS_IT
        elif doc_type == "how-it-works":
            system_message = READ_FILE_HOW_IT_WORKS
        else:
            logging.warning(f"Unknown documentation type: {doc_type}")
            return

        code_info = self.generate_codebase_overview_prompt(all_code)

        prompt = f"""
        Analyze this code:

        {code_info}

        {FINAL_INSTRUCTION}
        """

        messages = [{
            'role': 'system',
            'content': system_message
        }, {
            'role': 'user',
            'content': prompt
        }]

        self.logger.debug("OpenAI Chat Completion messages: %s", messages)

        return self.openai_chat_completion(messages)

    