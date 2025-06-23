import streamlit as st

def display_footer():
    """
    Displays the application footer with links to Terms of Service and Privacy Policy.
    """
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 10px;">
            <p style="font-size: 0.9em; color: #888;">
                © 2025 BankStat. All rights reserved.
            </p>
            <p style="font-size: 0.8em;">
                <a href="/tos" target="_self" style="color: #007bff; text-decoration: none; margin-right: 15px;">Terms of Service</a>
                <a href="/privacy" target="_self" style="color: #007bff; text-decoration: none;">Privacy Policy</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    st.title("Footer Test Page")
    st.write("This is a test to see how the footer looks.")
    display_footer()
