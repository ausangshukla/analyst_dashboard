import os
import shutil
import asyncio
import pandas as pd
import PyPDF2
import docx
import json
from pydantic_ai import Agent

class DashboardGenerator:
    def __init__(self, download_directory: str):
        self.download_directory = download_directory
        self.extracted_texts = {}

    async def generate_dashboard(self):
        print(f"Starting dashboard generation for directory: {self.download_directory}")
        
        pdf_files = []
        word_files = []
        csv_files = []
        html_js_files = []
        other_files = []

        for root, _, files in os.walk(self.download_directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file.lower().endswith(".pdf"):
                    pdf_files.append(file_path)
                elif file.lower().endswith((".doc", ".docx")):
                    word_files.append(file_path)
                elif file.lower().endswith(".csv"):
                    csv_files.append(file_path)
                elif file.lower().endswith((".html", ".js")):
                    html_js_files.append(file_path)
                else:
                    other_files.append(file_path)

        if pdf_files:
            print("Processing PDF files:")
            for pdf_file in pdf_files:
                await self._process_pdf(pdf_file)
        
        if word_files:
            print("Processing Word files:")
            for word_file in word_files:
                await self._process_word(word_file)

        if csv_files:
            print("Processing CSV files:")
            for csv_file in csv_files:
                await self._process_csv(csv_file)

        if html_js_files:
            print("Processing HTML/JS files:")
            for html_js_file in html_js_files:
                await self._process_text_file(html_js_file)

        if other_files:
            print("Processing other files:")
            for other_file in other_files:
                await self._process_text_file(other_file)

        # Clean up the directory after processing (optional, depending on requirements)
        # shutil.rmtree(self.download_directory)
        
        output_json_path = os.path.join(self.download_directory, "extracted_texts.json")
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(self.extracted_texts, f, indent=2)
        print(f"Extracted texts saved to: {output_json_path}")
        print(f"Finished dashboard generation for directory: {self.download_directory}")

        await self._generate_and_save_dashboard_files()

    async def _generate_and_save_dashboard_files(self):
        """
        Runs the AI agent to generate HTML and JS for the dashboard and saves them.
        """
        ai_agent = self.create_ai_agent()
        detailed_prompt = self.get_dashboard_prompt()

        print("Generating dashboard HTML and JS using AI agent...")
        try:
            response_text = await ai_agent.run(detailed_prompt)
            
            html_content = ""
            js_content = ""
            
            html_start_tag = "```html"
            html_end_tag = "```"
            js_start_tag = "```javascript"
            js_end_tag = "```"

            html_start_index = response_text.find(html_start_tag)
            html_end_index = response_text.find(html_end_tag, html_start_index + len(html_start_tag))
            
            if html_start_index != -1 and html_end_index != -1:
                html_content = response_text[html_start_index + len(html_start_tag):html_end_index].strip()
            else:
                print("Warning: Could not find HTML content in agent response.")

            js_start_index = response_text.find(js_start_tag)
            js_end_index = response_text.find(js_end_tag, js_start_index + len(js_start_tag))

            if js_start_index != -1 and js_end_index != -1:
                js_content = response_text[js_start_index + len(js_start_tag):js_end_index].strip()
            else:
                print("Warning: Could not find JavaScript content in agent response.")

            generated_html_path = os.path.join(self.download_directory, "dashboard.html")
            generated_js_path = os.path.join(self.download_directory, "dashboard.js")

            with open(generated_html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Generated HTML saved to: {generated_html_path}")

            with open(generated_js_path, "w", encoding="utf-8") as f:
                f.write(js_content)
            print(f"Generated JavaScript saved to: {generated_js_path}")

            html_content, js_content = await self._check_generated_files_for_errors(html_content, js_content)

        except Exception as e:
            print(f"Error generating dashboard with AI agent: {e}")

    async def _process_pdf(self, file_path: str):
        print(f"  Processing PDF: {file_path}")
        text = ""
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n"
            self.extracted_texts[os.path.basename(file_path)] = text
        except Exception as e:
            print(f"    Error processing PDF {file_path}: {e}")
            self.extracted_texts[os.path.basename(file_path)] = f"Error: {e}"

    async def _process_word(self, file_path: str):
        print(f"  Processing Word: {file_path}")
        text = ""
        try:
            document = docx.Document(file_path)
            for para in document.paragraphs:
                text += para.text + "\n"
            self.extracted_texts[os.path.basename(file_path)] = text
        except Exception as e:
            print(f"    Error processing Word {file_path}: {e}")
            self.extracted_texts[os.path.basename(file_path)] = f"Error: {e}"

    async def _process_csv(self, file_path: str):
        print(f"  Processing CSV: {file_path}")
        text = ""
        try:
            df = pd.read_csv(file_path)
            text = df.to_string() # Convert DataFrame to string
            self.extracted_texts[os.path.basename(file_path)] = text
        except Exception as e:
            print(f"    Error reading CSV {file_path}: {e}")
            self.extracted_texts[os.path.basename(file_path)] = f"Error: {e}"

    async def _process_text_file(self, file_path: str):
        print(f"  Processing text file: {file_path}")
        text = ""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            self.extracted_texts[os.path.basename(file_path)] = text
        except Exception as e:
            print(f"    Could not read {file_path} as text: {e}")
            self.extracted_texts[os.path.basename(file_path)] = f"Error: {e}"

    def get_dashboard_prompt(self) -> str:
        """
        Constructs a detailed static prompt for the AI agent to generate an HTML/JS dashboard.
        """
        extracted_content_str = json.dumps(self.extracted_texts, indent=2)

        html_template_path = os.path.join(self.download_directory, "dashboard.html")
        js_template_path = os.path.join(self.download_directory, "app.js")

        # Read the content of the template files
        try:
            with open(html_template_path, 'r', encoding='utf-8') as f:
                html_template = f.read()
        except FileNotFoundError:
            html_template = "<!-- index.html template not found -->"
            print(f"Warning: {html_template_path} not found.")
        
        try:
            with open(js_template_path, 'r', encoding='utf-8') as f:
                js_template = f.read()
        except FileNotFoundError:
            js_template = "// dashboard.js template not found"
            print(f"Warning: {js_template_path} not found.")

        prompt = f"""
            You are a senior financial analyst and an expert web developer. Your task is to analyze the provided financial documents (PDF and Word files) and other data, and then generate an interactive HTML/JavaScript dashboard.

            Here is the extracted text content from the documents:
            ```json
            {extracted_content_str}
            ```

            Based on this data, perform the following steps:
            1.  **Analyze the financial data**: Identify key financial metrics, trends, and insights relevant to a senior financial analyst. Focus on extracting actionable information.
            2.  **Generate HTML**: Create a single `index.html` file that serves as the main structure for the dashboard. This HTML should be similar to the provided `html_template` but populated with the necessary elements (e.g., charts, tables, summary sections) to display the financial insights. Ensure it links to a `dashboard.js` file.
            3.  **Generate JavaScript**: Create a single `dashboard.js` file that contains all the logic for rendering the interactive dashboard. This JavaScript should:
                *   Parse and utilize the financial data extracted from the documents.
                *   Create interactive visualizations (e.g., using a simple charting library or plain JavaScript for basic charts).
                *   Populate the HTML elements dynamically.
                *   Be similar in structure to the provided `js_template`.

            **Important Considerations:**
            *   The HTML and JavaScript files should be complete and self-contained.
            *   Do NOT include any external CSS frameworks unless explicitly requested. Use inline styles or a `<style>` block in the HTML if necessary.
            *   Focus on clarity and readability in both HTML and JavaScript.
            *   The dashboard should be interactive, allowing users to potentially filter data or view details (even if basic interactivity).
            *   Provide only the HTML and JavaScript code in your response, clearly separated.

            **HTML Template for reference:**
            ```html
            {html_template}
            ```

            **JavaScript Template for reference:**
            ```javascript
            {js_template}
            ```

            Your output should be two distinct code blocks, one for `index.html` and one for `dashboard.js`.
            """
        return prompt

    def create_ai_agent(self):
        """
        Creates and returns a Pydantic AI agent configured for Gemini 2.5 Flash.
        """
        # Assuming GEMINI_API_KEY is set as an environment variable
        # For local development, you might need to load it from a .env file
        # import os
        # from dotenv import load_dotenv
        # load_dotenv()
        # api_key = os.getenv("GEMINI_API_KEY")

        # Using the recommended 'google-gla' provider prefix for Gemini models
        agent = Agent('google-gla:gemini-2.5-flash') # Changed to 1.5 flash as 2.5 flash is not available
        return agent

    async def _check_generated_files_for_errors(self, html_content: str, js_content: str):
        """
        Uses the AI agent to check and correct the generated HTML and JS for errors.
        Retries up to 3 times.
        """
        ai_agent = self.create_ai_agent()
        
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            print(f"\nAttempt {attempt} to check and correct generated HTML and JS...")
            
            review_prompt = f"""
                You are an expert web developer and a meticulous code reviewer. Your task is to review the provided HTML and JavaScript code for any errors, inconsistencies, or potential issues. If you find any errors, you MUST provide the corrected HTML and JavaScript code in separate code blocks (```html...``` and ```javascript...```). If there are no errors, state that the code looks good and do NOT provide any code blocks.

                **HTML Code to Review:**
                ```html
                {html_content}
                ```

                **JavaScript Code to Review:**
                ```javascript
                {js_content}
                ```

                Please provide a detailed review, pointing out any:
                -   Syntax errors
                -   Logical errors
                -   Best practice violations
                -   Potential performance issues
                -   Suggestions for improvement

                If there are no errors, state that the code looks good. If there are errors, provide the corrected code.
                """
            try:
                review_response = await ai_agent.run(review_prompt)
                review_output = review_response.output # Assuming agent.run returns an object with an 'output' attribute
                print("AI Agent's Code Review:")
                print(review_output)

                if "code looks good" in review_output.lower() and "```html" not in review_output and "```javascript" not in review_output:
                    print("AI Agent confirmed no errors. Exiting correction loop.")
                    return html_content, js_content
                else:
                    print("AI Agent found errors or suggested changes. Attempting to apply corrections.")
                    # Parse the response to extract corrected HTML and JS
                    corrected_html = ""
                    corrected_js = ""
                    
                    html_start_tag = "```html"
                    html_end_tag = "```"
                    js_start_tag = "```javascript"
                    js_end_tag = "```"

                    html_start_index = review_output.find(html_start_tag)
                    html_end_index = review_output.find(html_end_tag, html_start_index + len(html_start_tag))
                    
                    if html_start_index != -1 and html_end_index != -1:
                        corrected_html = review_output[html_start_index + len(html_start_tag):html_end_index].strip()
                    
                    js_start_index = review_output.find(js_start_tag)
                    js_end_index = review_output.find(js_end_tag, js_start_index + len(js_start_tag))

                    if js_start_index != -1 and js_end_index != -1:
                        corrected_js = review_output[js_start_index + len(js_start_tag):js_end_index].strip()

                    if corrected_html and corrected_js:
                        html_content = corrected_html
                        js_content = corrected_js
                        print(f"Corrections applied. Retrying (Attempt {attempt + 1})...")
                    else:
                        print("AI Agent provided a review but no corrected code blocks. Cannot retry with corrections.")
                        return html_content, js_content # Return current content if no corrections provided

            except Exception as e:
                print(f"Error during AI agent code review (Attempt {attempt}): {e}")
                # If an error occurs during agent run, we might want to break or continue based on the error type
                # For now, we'll just print and let the loop continue if there are retries left.
        
        print(f"\nFailed to get error-free code after {max_retries} attempts. Returning last generated code.")
        return html_content, js_content