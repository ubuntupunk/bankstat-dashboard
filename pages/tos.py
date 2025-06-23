import streamlit as st

def tos_page():
    st.title("Terms of Service")
    st.write("""
    ## Terms of Service

    These terms of service ("Terms") govern your use of the BankStat application (the "App") provided by us. By using the App, you agree to be bound by these Terms.

    ### 1. Acceptance of Terms

    By accessing or using the App, you agree to these Terms and our Privacy Policy. If you do not agree with all of these Terms, do not access or use the App.

    ### 2. Description of Service

    The App provides tools for analyzing your bank statements and gaining insights into your financial activity.

    ### 3. Third-Party Services

    The App utilizes a third-party service for processing uploaded PDF bank statements into machine-readable formats, such as CSV. This service is committed to high security standards, is a member of [AICPA/CIMA](https://www.aicpa-cima.com) and holds an information security management certificate issued by BSI.

    The BankStat AI adviser within the App utilizes a Meta Language model, which is streamed from a third-party hosting service. This AI agent has been specifically tailored to provide general financial information, and steps have been taken to restrict its discussion topics to remain within this scope.

    ### 4. User Responsibilities

    You are responsible for maintaining the confidentiality of your account and password and for restricting access to your device. You agree to accept responsibility for all activities that occur under your account.

    ### 5. Disclaimer of Warranties

    The App is provided on an "as is" and "as available" basis. We make no warranties, express or implied, regarding the App. We adhere to professional standards, including those set forth by organizations like the AICPA (American Institute of Certified Public Accountants) which can be found at [https://www.aicpa-cima.com](https://www.aicpa-cima.com).

    ### 6. Limitation of Liability

    We will not be liable for any damages of any kind arising from the use of the App.

    ### 7. Governing Law

    These Terms shall be governed by the laws of the Republic of South Africa, without regard to its conflict of law provisions.

    ### 8. Changes to Terms

    We reserve the right to modify these Terms at any time. Your continued use of the App after any such changes constitutes your acceptance of the new Terms.

    ### 9. Contact Information

    If you have any questions about these Terms, please contact us at [Your Contact Information].
    """)

if __name__ == "__main__":
    tos_page()
