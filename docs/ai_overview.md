# AI Financial Advisor Tab Overview

## Purpose
The `ai_advisor_tab.py` module integrates an AI-powered financial advisor into a Streamlit application, providing users with general financial advice on topics such as household budgets, saving money, and retirement investing. It leverages the Cerebras Cloud SDK to interact with a large language model (LLM), currently set to "llama3.1-8b," to generate responses based on user queries.

## Functionality
- **User Interface**: A Streamlit tab with a text input field for users to submit financial questions (e.g., "How can I save for retirement?") and a display area for AI-generated responses.
- **AI Integration**: Uses the Cerebras Cloud SDK to send user queries to an LLM, wrapped in a carefully engineered prompt to ensure accurate and ethical financial advice.
- **Error Handling**: Manages API initialization failures, rate limits, and response errors to maintain app stability.
- **Security**: Loads the Cerebras API key from an environment variable using `python-dotenv` to prevent key exposure.
- **Disclaimer**: Informs users that AI advice is general and not a substitute for professional financial guidance.

## Technical Details

### Dependencies
- **Python Libraries**:
  - `streamlit`: For building the interactive UI.
  - `cerebras-cloud-sdk`: For interacting with Cerebras Cloud AI models.
  - `python-dotenv`: For loading environment variables (e.g., API key).
- **Installation**:
  ```bash
  pip install streamlit cerebras-cloud-sdk python-dotenv
  ```

### File Structure
- **ai_advisor_tab.py**: Main module containing the `render_ai_advisor_tab` function, which sets up the Streamlit UI and handles AI interactions.
- **.env** (not included in repo): Stores the `CEREBRAS_API_KEY` environment variable.
  ```plaintext
  CEREBRAS_API_KEY=your-api-key-here
  ```

### Key Components
- **Cerebras Client Initialization**:
  ```python
  client = Cerebras(api_key=api_key)
  ```
  Initializes the Cerebras client using the API key from the environment.
- **Prompt Engineering**:
  The prompt ensures accurate and ethical responses:
  ```plaintext
  You are a financial advisor with expertise in household budgets, saving money, and investing for retirement.
  Provide accurate, clear, and actionable advice for the query: '{user_query}'.
  Base your response on general financial principles.
  Do not provide advice that involves illegal or unethical practices.
  If the query is unclear, ask for clarification or provide general guidance.
  ```
- **Streamlit UI**:
  - Title and description styled with HTML/CSS.
  - Text input for user queries.
  - Loading spinner during API calls.
  - Response display with error handling.
- **Error Handling**:
  Catches exceptions for API initialization, request failures, and invalid responses, displaying user-friendly error messages.

### Model Selection
- **Current Model**: "llama3.1-8b" (general-purpose LLM).
- **Recommendation**: Check the [Cerebras Model Zoo](https://cerebras.ai/) or contact [Cerebras support](https://cerebras.ai/developers/) for finance-specific models. If unavailable, enhance prompt engineering for better accuracy.
- **Configuration**:
  ```python
  response = client.chat.completions.create(
      messages=[{"role": "user", "content": prompt}],
      model="llama3.1-8b",
      max_tokens=500
  )
  ```

## Setup Instructions
1. **Obtain Cerebras API Key**:
   - Sign up at [Cerebras Cloud](https://cloud.cerebras.ai/) to get an API key.
   - Store it in a `.env` file or environment variable:
     ```plaintext
     CEREBRAS_API_KEY=your-api-key-here
     ```
2. **Install Dependencies**:
   ```bash
   pip install streamlit cerebras-cloud-sdk python-dotenv
   ```
3. **Integrate into Streamlit App**:
   - Import and call `render_ai_advisor_tab` in your main app, similar to `tools_tab.py`:
     ```python
     from tabs.ai_advisor import render_ai_advisor_tab
     render_ai_advisor_tab()
     ```
   - Ensure `.env` is in the project root and loaded with `load_dotenv()`.
4. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## Security Considerations
- **API Key**: Store in `.env` and exclude from version control (add `.env` to `.gitignore`).
- **Rate Limits**: Check [Cerebras documentation](https://inference-docs.cerebras.ai/) for limits and implement retry logic if needed.
- **Data Privacy**: Avoid sending sensitive user data (e.g., account numbers) to the API.
- **Disclaimer**: Clearly state that AI advice is not professional financial guidance to mitigate liability.

## Development Notes
- **Prompt Tuning**: Adjust the prompt based on response quality. Test with varied queries (e.g., budgeting, investing) to ensure relevance.
- **Performance**: Reuse the Cerebras client instance to avoid reinitialization. Consider enabling streaming (`stream=True`) for real-time responses.
- **Testing**: Validate responses for accuracy and ethics. Monitor for hallucinations or off-topic advice.
- **Enhancements**:
  - Add query history or predefined question templates.
  - Support multi-turn conversations for follow-up questions.
  - Explore fine-tuning a model on financial datasets via Cerebras Cloud.

## Limitations
- **Model Accuracy**: General-purpose models like "llama3.1-8b" may lack financial specificity, requiring robust prompt engineering.
- **API Dependence**: Relies on Cerebras Cloud availability and rate limits.
- **Scope**: Advice is general and may not account for user-specific circumstances (e.g., income, location).

## Resources
- [Cerebras Cloud SDK Documentation](https://sdk.cerebras.net/)
- [Cerebras Inference Guide](https://inference-docs.cerebras.ai/)
- [Cerebras Financial Services](https://www.cerebras.ai/industry-financial-services)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Python-dotenv Documentation](https://pypi.org/project/python-dotenv/)

## Contact
For issues or model recommendations, reach out to [Cerebras support](https://cerebras.ai/developers/) or consult the [Cerebras GitHub](https://github.com/Cerebras/cerebras-cloud-sdk-python).