import streamlit as st
import pandas as pd
import plotly.express as px

def render_energy_calculator():
    """Renders the Energy Calculator section."""

    # Default appliance settings for South African households
    appliance_defaults = {
    'Lighting': {'usage_type': 'Timed', 'power': 10.0, 'hours_per_day': 5.0, 'quantity': 10},
    'Washing Machine': {'usage_type': 'Per Use', 'energy_per_use': 1.0, 'uses_per_month': 8},
    'Stove': {'usage_type': 'Timed', 'power': 3000.0, 'hours_per_day': 1.0, 'quantity': 1},
    'Microwave': {'usage_type': 'Timed', 'power': 1000.0, 'hours_per_day': 0.5, 'quantity': 1},
    'Phone Charger': {'usage_type': 'Timed', 'power': 5.0, 'hours_per_day': 2.0, 'quantity': 1},
    'Geyser': {'usage_type': 'Always-On', 'daily_energy': 15.0},
    'Fridge': {'usage_type': 'Always-On', 'daily_energy': 3.0},
    'Custom': {'usage_type': 'Timed', 'power': 0.0, 'hours_per_day': 0.0, 'quantity': 1}
}

    def render_energy_calculator():
        """Renders the Energy Calculator section."""
        # App title and description
        st.markdown("""
        <div class="header">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-bolt"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.29 7 12 12 20.71 7"></polyline><line x1="12" y1="22" x2="12" y2="12"></line></svg>
        <h1>Energy Calculator</h1>
        </div>
    """, unsafe_allow_html=True)
        st.markdown("""
        This calculator helps you understand how your monthly electricity bill is divided among household appliances. 
        Add appliances, adjust their settings, and see the cost breakdown. Tailored for South African households with prepaid metering.
        """)

    # Global settings
    with st.container():
        st.markdown('<div class="input-section"><h2>Global Settings</h2></div>', unsafe_allow_html=True)
        fixed_fee = st.number_input(
            "Fixed monthly fee (R)", 
            min_value=0.0, 
            value=0.0, 
            help="Enter any fixed connection fee (R0 for prepaid users)."
        )
        price_per_kwh = st.number_input(
            "Price per kWh (R)", 
            min_value=0.0, 
            value=2.50, 
            help="Enter your electricity rate per kWh (e.g., R2.50)."
        )

    # Appliances section
    with st.container():
        st.markdown('<div class="input-section"><h2>Appliances</h2></div>', unsafe_allow_html=True)
        
        # Initialize session state for appliances
        if 'appliances' not in st.session_state:
            st.session_state.appliances = []
        
        # Add new appliance
        appliance_type = st.selectbox("Select appliance type to add", list(appliance_defaults.keys()))
        if appliance_type == "Custom":
            usage_type = st.selectbox("Usage Type", ["Timed", "Per Use", "Always-On"], key="custom_usage")
            if usage_type == "Timed":
                new_appliance = {'usage_type': 'Timed', 'power': 0.0, 'hours_per_day': 0.0, 'quantity': 1}
            elif usage_type == "Per Use":
                new_appliance = {'usage_type': 'Per Use', 'energy_per_use': 0.0, 'uses_per_month': 0}
            elif usage_type == "Always-On":
                new_appliance = {'usage_type': 'Always-On', 'daily_energy': 0.0}
            new_name = f"Custom {len([app for app in st.session_state.appliances if app['type'] == 'Custom']) + 1}"
            new_appliance['name'] = new_name
            new_appliance['type'] = 'Custom'
        else:
            new_appliance = appliance_defaults[appliance_type].copy()
            type_count = sum(1 for app in st.session_state.appliances if app['type'] == appliance_type)
            new_name = f"{appliance_type} {type_count + 1}"
            new_appliance['name'] = new_name
            new_appliance['type'] = appliance_type
        
        if st.button("Add Appliance"):
            st.session_state.appliances.append(new_appliance)
        
        # Display and edit appliances
        for i, appliance in enumerate(st.session_state.appliances):
            with st.expander(f"{appliance['name']}"):
                appliance['name'] = st.text_input("Appliance Name", value=appliance['name'], key=f"name_{i}")
                
                if appliance['usage_type'] == 'Timed':
                    appliance['power'] = st.number_input(
                        "Power (watts)", 
                        min_value=0.0, 
                        value=float(appliance['power']), 
                        key=f"power_{i}", 
                        help="Power rating in watts."
                    )
                    appliance['hours_per_day'] = st.number_input(
                        "Hours per day", 
                        min_value=0.0, 
                        value=float(appliance['hours_per_day']), 
                        key=f"hours_{i}", 
                        help="Daily usage hours."
                    )
                    appliance['quantity'] = st.number_input(
                        "Quantity", 
                        min_value=1, 
                        value=int(appliance['quantity']), 
                        key=f"qty_{i}", 
                        help="Number of units."
                    )
                elif appliance['usage_type'] == 'Per Use':
                    appliance['energy_per_use'] = st.number_input(
                        "Energy per use (kWh)", 
                        min_value=0.0, 
                        value=float(appliance['energy_per_use']), 
                        key=f"energy_per_use_{i}", 
                        help="Energy per cycle in kWh."
                    )
                    appliance['uses_per_month'] = st.number_input(
                        "Uses per month", 
                        min_value=0, 
                        value=int(appliance['uses_per_month']), 
                        key=f"uses_{i}", 
                        help="Number of uses per month."
                    )
                elif appliance['usage_type'] == 'Always-On':
                    appliance['daily_energy'] = st.number_input(
                        "Daily energy (kWh)", 
                        min_value=0.0, 
                        value=float(appliance['daily_energy']), 
                        key=f"daily_energy_{i}", 
                        help="Daily energy consumption in kWh."
                    )
                
                if st.button("Remove", key=f"remove_{i}"):
                    if 'to_remove' not in st.session_state:
                        st.session_state.to_remove = []
                    st.session_state.to_remove.append(i)
        
        # Remove marked appliances
        if 'to_remove' in st.session_state:
            for i in sorted(st.session_state.to_remove, reverse=True):
                del st.session_state.appliances[i]
            del st.session_state.to_remove

    # Summary and visualization
    with st.container():
        st.markdown('<div class="results-section"><h2>Summary</h2></div>', unsafe_allow_html=True)
        total_energy = 0
        total_cost = 0
        appliance_costs = []

        for appliance in st.session_state.appliances:
            if appliance['usage_type'] == 'Timed':
                energy = (appliance['power'] / 1000) * appliance['hours_per_day'] * 30 * appliance['quantity']
            elif appliance['usage_type'] == 'Per Use':
                energy = appliance['energy_per_use'] * appliance['uses_per_month']
            elif appliance['usage_type'] == 'Always-On':
                energy = appliance['daily_energy'] * 30
            
            cost = energy * price_per_kwh
            appliance_costs.append({'name': appliance['name'], 'energy': round(energy, 2), 'cost': round(cost, 2)})
            total_energy += energy
            total_cost += cost
        
        total_cost += fixed_fee

        if appliance_costs:
            df = pd.DataFrame(appliance_costs)
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.table(df)
            st.markdown(f"""
                <div style="color: #15803d; font-size: 0.875rem;">
                    <div><b>Total monthly energy consumption:</b> {total_energy:.2f} kWh</div>
                    <div><b>Total monthly cost:</b> R{total_cost:.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Pie chart for cost distribution
            fig = px.pie(df, values='cost', names='name', title='Cost Distribution by Appliance')
            st.plotly_chart(fig)
        else:
            st.write("Add appliances to see your bill breakdown.")

    return render_energy_calculator
