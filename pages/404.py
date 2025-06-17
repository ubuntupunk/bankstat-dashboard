import streamlit as st

def render_404_page():
    """
    Renders a custom 404 (Page Not Found) page.
    """
    st.set_page_config(
        page_title="Bankstat - Page Not Found",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    st.markdown(
        """
        <style>
            .stApp {
                background-color: #f0f2f6; /* Light grey background */
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
                text-align: center;
            }
            .stApp > header {
                display: none; /* Hide Streamlit header */
            }
            .stApp > footer {
                display: none; /* Hide Streamlit footer */
            }
            h1 {
                color: #FF4B4B; /* Red for error */
                font-size: 3rem;
                margin-bottom: 1rem;
            }
            p {
                font-size: 1.2rem;
                color: #555;
                margin-bottom: 2rem;
            }
            .stButton > button {
                background-color: #2E8B57;
                color: white;
                padding: 0.75rem 2rem;
                border-radius: 0.5rem;
                border: none;
                font-size: 1.2rem;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            .stButton > button:hover {
                background-color: #3CB371; /* Lighter green on hover */
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("404 - Page Not Found")
    st.write("Oops! The page you are looking for does not exist.")
    st.write("It might have been moved or deleted.")

    if st.button("Go to Home Page"):
        st.switch_page("streamlit_app.py")

if __name__ == "__main__":
    render_404_page()
