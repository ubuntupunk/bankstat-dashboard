import streamlit as st
from streamlit_mermaid import st_mermaid
import os

def render_tools_tab():
    """Render the Tools tab with a Financial Flow Calculator."""
    # Load CSS from tools.css
    css_path = os.path.join(os.path.dirname(__file__), "tools.css")
    try:
        with open(css_path, "r") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("tools.css file not found. Please ensure it exists in the same directory as tools_tab.py.")
        return

    # Main container
    with st.container():
        st.markdown('<div class="calculator-container">', unsafe_allow_html=True)
        
        # Header
        st.markdown("""
            <div class="header">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-calculator"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" x2="16" y1="6" y2="6"/><line x1="16" x2="16" y1="14" y2="18"/><path d="M16 10h.01"/><path d="M12 10h.01"/><path d="M8 10h.01"/><path d="M12 14h.01"/><path d="M8 14h.01"/><path d="M12 18h.01"/><path d="M8 18h.01"/></svg>
                <h1>Financial Flow Calculator</h1>
            </div>
        """, unsafe_allow_html=True)

        # Input and Results sections
        col1, col2 = st.columns([1, 1])

        # Input Section
        with col1:
            st.markdown('<div class="input-section"><h2>Input Parameters</h2></div>', unsafe_allow_html=True)
            initial_amount = st.number_input(
                "Initial Amount (R)",
                min_value=0.0,
                value=1000.0,
                step=0.01,
                format="%.2f",
                key="initial_amount",
                help="Enter the initial investment amount in Rand."
            )
            dividend_rate = st.number_input(
                "Dividend Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=5.0,
                step=0.1,
                format="%.1f",
                key="dividend_rate",
                help="Enter the annual dividend rate as a percentage."
            )
            dividend_tax_rate = st.number_input(
                "Dividend Tax Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=20.0,
                step=0.1,
                format="%.1f",
                key="dividend_tax_rate",
                help="Enter the tax rate on dividends as a percentage."
            )

        # Calculations
        dividend = (initial_amount * dividend_rate) / 100
        dividend_tax = (dividend * dividend_tax_rate) / 100
        net_dividend = dividend - dividend_tax
        total_value = initial_amount + net_dividend

        # Results Section
        with col2:
            st.markdown('<div class="results-section"><h2>Calculated Results</h2></div>', unsafe_allow_html=True)
            
            # Investment Path
            st.markdown('<div class="result-card investment-card">', unsafe_allow_html=True)
            st.markdown("""
                <div class="title">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-trending-up"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
                    <span>Investment Path</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
                <div style="color: #15803d; font-size: 0.875rem;">
                    <div>Dividend: R{dividend:.2f}</div>
                    <div>Tax: R{dividend_tax:.2f}</div>
                    <div>Net Dividend: R{net_dividend:.2f}</div>
                    <div style="font-weight: bold; font-size: 1.125rem; padding-top: 0.25rem;">Total: R{total_value:.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Consumption Path
            st.markdown('<div class="result-card consumption-card">', unsafe_allow_html=True)
            st.markdown("""
                <div class="title">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-trending-down"><polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/></svg>
                    <span>Consumption Path</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
                <div style="color: #b91c1c; font-size: 0.875rem;">
                    <div>Consumed: R{initial_amount:.2f}</div>
                    <div>Remaining: R0.00</div>
                    <div style="font-weight: bold; font-size: 1.125rem; padding-top: 0.25rem;">Loss: R{initial_amount:.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Investment Advantage
            st.markdown('<div class="result-card advantage-card">', unsafe_allow_html=True)
            st.markdown("""
                <div class="title">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-dollar-sign"><line x1="12" x2="12" y1="2" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                    <span>Investment Advantage</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
                <div style="color: #1e40af;">
                    <span style="font-size: 1.125rem; font-weight: bold;">R{net_dividend:.2f}</span> additional value vs consumption
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Mermaid Diagram
        st.markdown('<div class="calculator-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="font-size: 1.25rem; font-weight: 600; color: #374151; margin-bottom: 1rem;">Financial Flow Diagram</h2>', unsafe_allow_html=True)
        mermaid_code = f"""flowchart TD
    A["R{initial_amount:.2f} Earned"] --> B{{Decision Point}}
    
    %% Investment Branch
    B -->|Investment| C["Invested: R{initial_amount:.2f}"]
    C --> D["Dividend Generated: R{dividend:.2f}"]
    D --> E["Dividend Tax ({dividend_tax_rate}%): R{dividend_tax:.2f}"]
    E --> F["Net Dividend: R{net_dividend:.2f}"]
    F --> G["Total Value: R{total_value:.2f}"]
    
    %% Consumption Branch
    B -->|Consumption| H["Immediate Consumption: R{initial_amount:.2f}"]
    H --> I["Value Extracted: R{initial_amount:.2f}"]
    I --> J["Remaining Value: R0.00"]
    
    %% Styling
    classDef startNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef investmentPath fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef consumptionPath fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef endPositive fill:#4caf50,color:#fff,stroke:#2e7d32,stroke-width:3px
    classDef endNegative fill:#f44336,color:#fff,stroke:#c62828,stroke-width:3px
    
    class A startNode
    class C,D,E,F investmentPath
    class H,I consumptionPath
    class G endPositive
    class J endNegative
"""
        st.markdown('<div class="diagram-container">', unsafe_allow_html=True)
        st_mermaid(mermaid_code, height=500)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)