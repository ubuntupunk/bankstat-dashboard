import streamlit as st

def privacy_policy_page():
    """
    Displays the Privacy Policy page.
    """
    st.set_page_config(page_title="Privacy Policy", page_icon="🔒")
    st.title("🔒 Privacy Policy")

    st.markdown("""
    This Privacy Policy describes how BankStat Dashboard ("we," "us," or "our") collects, uses, and discloses your information when you use our application.

    **Information We Collect**

    We collect information you provide directly to us when you use the BankStat Dashboard, such as:
    *   **Bank Statement Data:** When you upload bank statements, we process and store the financial transaction data contained within them. This data is used solely for the purpose of providing you with financial insights and visualizations within the application.
    *   **Account Information:** If you create an account, we collect basic information such as your username and email address.
    *   **Usage Data:** We may collect information about how you access and use the application, including your IP address, browser type, operating system, and usage patterns. This data is used for analytical purposes to improve the application's performance and user experience.

    **How We Use Your Information**

    We use the information we collect for various purposes, including to:
    *   Provide, maintain, and improve the BankStat Dashboard's features and functionality.
    *   Process and analyze your bank statement data to generate financial insights and visualizations.
    *   Communicate with you about your account, updates, and important notices.
    *   Monitor and analyze usage and trends to improve the application.
    *   Ensure the security and integrity of our services.

    **Data Sharing and Disclosure**

    We do not share, sell, rent, or trade your personal financial data with third parties for their marketing purposes. We may share information in the following circumstances:
    *   **With Your Consent:** We may share your information if you give us explicit consent to do so.
    *   **Service Providers:** We may share your information with third-party service providers who perform services on our behalf, such as hosting, data analysis, and customer support. These service providers are obligated to protect your information and use it only for the purposes for which it was disclosed.
    *   **Legal Requirements:** We may disclose your information if required to do so by law or in response to valid requests by public authorities (e.g., a court order or government agency request).
    *   **Business Transfers:** In the event of a merger, acquisition, or sale of all or a portion of our assets, your information may be transferred as part of that transaction. We will notify you via email or a prominent notice on our application of any such change in ownership or control of your personal information.
    *   **Aggregated or Anonymized Data:** We may share aggregated or anonymized data that cannot reasonably be used to identify you.

    **Data Security**

    We implement reasonable security measures to protect your information from unauthorized access, alteration, disclosure, or destruction. However, no method of transmission over the Internet or electronic storage is 100% secure, and we cannot guarantee absolute security.

    **Your Choices**

    *   **Access and Correction:** You may access and update your account information through the application settings.
    *   **Data Retention:** We retain your bank statement data and other information for as long as necessary to provide you with the services and for legitimate business purposes, such as complying with legal obligations, resolving disputes, and enforcing our agreements.
    *   **Deletion:** You may request the deletion of your account and associated data by contacting us. Please note that some information may be retained for legal or operational purposes.

    **Changes to This Privacy Policy**

    We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the "Last Updated" date. You are advised to review this Privacy Policy periodically for any changes.

    **Contact Us**

    If you have any questions about this Privacy Policy, please contact us at [Your Contact Email Here].

    ---
    *Last Updated: June 11, 2025*
    """)

if __name__ == "__main__":
    privacy_policy_page()
