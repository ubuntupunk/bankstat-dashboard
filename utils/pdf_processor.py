import streamlit as st
import requests
import os
import re
from datetime import datetime
import tempfile
from config import Config

class StreamlitBankProcessor:
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.upstage_api_key

    @st.cache_data
    def process_pdf(_self, uploaded_file):
        """Process uploaded PDF file using Upstage API"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            # Call Upstage API
            st.write("📄 Starting PDF processing...")
            st.write(f"📂 Temporary file created at: {tmp_file_path}")
            url = 'https://api.upstage.ai/v1/document-ai/document-parse'
            headers = {"Authorization": f"Bearer {_self.api_key}"}
            st.write("🔗 API endpoint: {url}")
            st.write("🔑 Using API key (truncated): {_self.api_key[:4]}...{_self.api_key[-4:]}")

            with open(tmp_file_path, "rb") as file:
                files = {"document": file}
                response = requests.post(url, headers=headers, files=files)

            # Clean up temp file
            try:
                os.unlink(tmp_file_path)
            except:
                pass  # Handle case where file might not exist

            if response.status_code == 200:
                st.write("✅ API request successful")
                st.write(f"⏱️ Response time: {response.elapsed.total_seconds():.2f}s")
                data = response.json()
                st.write("📊 Extracted data keys: {list(data.keys())}")

                # Parse filename for date range
                filename = uploaded_file.name
                start_date, end_date = _self.parse_pdf_name(filename)

                data["filename"] = filename
                data["period"] = {
                    "start": start_date.strftime('%Y-%m-%d') if start_date else None,
                    "end": end_date.strftime('%Y-%m-%d') if end_date else None
                }

                return data
            else:
                st.error(f"API request failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return None

    def parse_pdf_name(self, pdf_name):
        """Parse date range from PDF filename"""
        pattern = r'(\d{2}\s\w{3}\s\d{4})\s-\s(\d{2}\s\w{3}\s\d{4})\.pdf'
        match = re.match(pattern, pdf_name)
        if match:
            start_date = datetime.strptime(match.group(1), '%d %b %Y')
            end_date = datetime.strptime(match.group(2), '%d %b %Y')
            return start_date, end_date
        return None, None