import streamlit as st

def tos_page():
    st.title("Terms of Service")
    st.write("""
    ## Terms of Service

    These terms of service ("Terms") govern your use of the BankStat Dashboard application (the "App") provided by us. By using the App, you agree to be bound by these Terms.

    ### 1. Acceptance of Terms

    By accessing or using the App, you agree to these Terms and our Privacy Policy. If you do not agree with all of these Terms, do not access or use the App.

    ### 2. Description of Service

    The App provides tools for analyzing your bank statements and gaining insights into your financial activity.

    ### 3. User Responsibilities

    You are responsible for maintaining the confidentiality of your account and password and for restricting access to your device. You agree to accept responsibility for all activities that occur under your account.

    ### 4. Disclaimer of Warranties

    The App is provided on an "as is" and "as available" basis. We make no warranties, express or implied, regarding the App.

    ### 5. Limitation of Liability

    We will not be liable for any damages of any kind arising from the use of the App.

    ### 6. Governing Law

    These Terms shall be governed by the laws of the State of [Your State], without regard to its conflict of law provisions.

    ### 7. Changes to Terms

    We reserve the right to modify these Terms at any time. Your continued use of the App after any such changes constitutes your acceptance of the new Terms.

    ### 8. Contact Information

    If you have any questions about these Terms, please contact us at [Your Contact Information].
    """)

if __name__ == "__main__":
    tos_page()
