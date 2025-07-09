import streamlit as st
import requests

API_BASE = "http://localhost:8000/api/v1"

def download_file(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        st.download_button(
            label=f"Download {filename.split('.')[-1].upper()}",
            data=response.content,
            file_name=filename,
            mime="application/pdf" if filename.endswith(".pdf") else "text/csv"
        )
    else:
        st.error(f"Failed to download {filename}: {response.status_code}")

def show():
    st.title("Visualize Pathways")
    st.write("Interactive graphs and pathway visualizations will appear here.")

    # Example scenario data (replace with user input in the future)
    scenario_data = {
        "years": [2025, 2030, 2040, 2050],
        "vehicle_types": ["car", "bus"],
        "miles_traveled": {
            "car":   [1_000_000, 1_100_000, 1_200_000, 1_300_000],
            "bus":   [100_000, 110_000, 120_000, 130_000]
        },
        "fuel_mix": {
            "car": [
                {"petrol": 0.7, "diesel": 0.2, "electric": 0.1, "hydrogen": 0.0},
                {"petrol": 0.5, "diesel": 0.2, "electric": 0.25, "hydrogen": 0.05},
                {"petrol": 0.2, "diesel": 0.1, "electric": 0.6, "hydrogen": 0.1},
                {"petrol": 0.0, "diesel": 0.0, "electric": 0.8, "hydrogen": 0.2}
            ],
            "bus": [
                {"diesel": 0.8, "electric": 0.1, "hydrogen": 0.1},
                {"diesel": 0.6, "electric": 0.2, "hydrogen": 0.2},
                {"diesel": 0.3, "electric": 0.4, "hydrogen": 0.3},
                {"diesel": 0.0, "electric": 0.5, "hydrogen": 0.5}
            ]
        },
        "emission_factors": {  # gCO2e per mile
            "petrol": 250,
            "diesel": 220,
            "electric": 50,
            "hydrogen": 20
        },
        "cost_per_mile": {  # £ per mile
            "petrol": 0.12,
            "diesel": 0.10,
            "electric": 0.08,
            "hydrogen": 0.15
        }
    }

    scenario_id = st.number_input("Scenario ID to export", min_value=1, step=1)
    if st.button("Download CSV"):
        download_file(f"{API_BASE}/scenarios/{scenario_id}/export/csv", f"scenario_{scenario_id}_results.csv")
    if st.button("Download PDF"):
        download_file(f"{API_BASE}/scenarios/{scenario_id}/export/pdf", f"scenario_{scenario_id}_results.pdf")

    if st.button("Run Optimization"):
        with st.spinner("Optimizing..."):
            try:
                response = requests.post(f"{API_BASE}/optimize/", json=scenario_data)
                if response.status_code == 200:
                    result = response.json()
                    if result["success"]:
                        st.success("Optimization complete!")
                        st.write("Objective value (minimized emissions):", result["objective_value"])
                        st.write("Optimized fuel mix:")
                        st.json(result["optimized_mix"])
                    else:
                        st.error(
                            "No feasible pathway found with current constraints. "
                            "Try relaxing year-on-year change limits, or adjust scenario targets."
                        )
                        st.info(f"Solver message: {result['message']}")
                else:
                    st.error(f"API call failed: {response.status_code}")
            except Exception as e:
                st.error(f"Error calling API: {e}") 