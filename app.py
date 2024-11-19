import streamlit as st
import google.generativeai as genai
import re
from typing import Dict, Tuple

# Set your page config first
st.set_page_config(
    page_title="🤖 AI-Powered Python Code Reviewer",
    page_icon="💻",
    layout="centered"  # This centers the content
)

# Read the Gemini API key from the file
def load_api_key(file_path: str) -> str:
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except Exception as e:
        st.error(f"Error reading API key: {str(e)}")
        return ""

# Set your Gemini API key directly from the file
GEMINI_API_KEY = load_api_key("C:\\Users\\mdimr\\Downloads\\AI_Code_Reviwer\\Aireviewer_Key.txt")

class CodeReviewer:
    def __init__(self):
        """Initialize the CodeReviewer with Gemini AI."""
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None

    def review_code(self, code: str) -> Tuple[Dict, str]:
        """
        Review the provided code using Gemini AI.
        Returns a tuple of (issues_dict, fixed_code).
        """
        if not self.model:
            return {"bugs": [], "improvements": []}, ""

        try:
            # Prompt engineering for better code review results
            prompt = f"""
            Please review the following Python code and provide:
            1. A list of potential bugs and issues
            2. Code quality improvements
            3. A corrected version of the code
            
            Here's the code to review:
            ```python
            {code}
            ```
            
            Please format your response exactly as shown below:
            ISSUES:
            - [issue description]
            
            IMPROVEMENTS:
            - [improvement suggestion]
            
            FIXED_CODE:
            ```python
            [corrected code]
            ```
            
            Please ensure to maintain this exact format in your response.
            """
            
            # Get response from Gemini
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Initialize dictionary to store issues
            issues = {'bugs': [], 'improvements': []}
            
            # Extract issues
            issues_match = re.findall(r'ISSUES:\n(.*?)(?=IMPROVEMENTS:|FIXED_CODE:|$)', response_text, re.DOTALL)
            if issues_match:
                issues['bugs'] = [bug.strip() for bug in issues_match[0].split('\n') if bug.strip()]

            # Extract improvements
            improvements_match = re.findall(r'IMPROVEMENTS:\n(.*?)(?=FIXED_CODE:|$)', response_text, re.DOTALL)
            if improvements_match:
                issues['improvements'] = [imp.strip() for imp in improvements_match[0].split('\n') if imp.strip()]
            
            # Extract fixed code
            fixed_code_match = re.findall(r'```python\n(.*?)```', response_text, re.DOTALL)
            fixed_code = fixed_code_match[-1].strip() if fixed_code_match else ""
            
            return issues, fixed_code
        
        except Exception as e:
            st.error(f"Error during code review: {str(e)}")
            return {"bugs": [], "improvements": []}, ""


def main():
    # Centering the content using custom CSS
    st.markdown(
        """
        <style>
        .stApp {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .main-container {
            width: 60%;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 10px;
            background-color: #f9f9f9;
        }
        .header-image {
            width: 100%;
            height: auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Main content area inside a container for centering
    with st.container():
        st.markdown(f'<img src="https://th.bing.com/th/id/OIP.lfaO7fPyuO2IXUHMjYqlywHaCe?rs=1&pid=ImgDetMain" alt="AI Code Reviewer" class="header-image" />', unsafe_allow_html=True)
        
        st.title("💻🤖 AI-Powered Python Code Reviewer")
        st.markdown(""" 
        Paste your Python code, and get detailed feedback on potential bugs, code quality improvements, and a fixed version using Google Gemini AI.
        """)
        
        # Create a box container for the code input section
        st.markdown('<div class="main-container">', unsafe_allow_html=True)

        st.header("📝📝 Enter Your Python Code")
        user_code = st.text_area(
            "Paste your Python code here",
            height=150,
            placeholder="# Paste your Python code here..."
        )
        
        if st.button("🤖Review Code"):
            if not user_code.strip():
                st.warning("Please enter some code to review.")
                return

            with st.spinner("🔍🔍 Reviewing your code..."):
                reviewer = CodeReviewer()
                issues, fixed_code = reviewer.review_code(user_code)

                # Display the results directly
                if issues:
                    st.subheader("🐞🐞 Potential Bugs")
                    for bug in issues['bugs']:
                        st.markdown(f"- {bug.strip('- ')}")
                    
                    st.subheader("💡💡 Suggested Improvements")
                    for improvement in issues['improvements']:
                        st.markdown(f"- {improvement.strip('- ')}")
                    
                    st.subheader("🛠️🛠️ Improved Code")
                    if fixed_code:
                        st.code(fixed_code, language="python")

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
