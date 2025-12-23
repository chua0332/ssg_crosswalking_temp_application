import streamlit as st
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===========================================
# CONFIG
# ===========================================
API_URL = "https://ssg-crosswalking-api.onrender.com/match-skill"

# ===========================================
# API CALL (cached)
# ===========================================
@st.cache_data(show_spinner=False)
def call_api(title: str, description: str):
    params = {"title": title, "description": description}
    try:
        r = requests.get(API_URL, params=params, timeout=15)
        r.raise_for_status()
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, None


# ===========================================
# PAGE SETUP
# ===========================================
st.set_page_config(
    page_title="Skill Matching crosswalking UI",
    page_icon="🔍",
    layout="wide"
)

st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to", ["Single Query", "Batch Mode"])

st.sidebar.markdown("---")
st.sidebar.markdown("**API Endpoint**")
st.sidebar.code(API_URL)
st.sidebar.markdown("---")
st.sidebar.info("Built with Streamlit + FastAPI ⚡")


# ===========================================
# 1️⃣ SINGLE QUERY PAGE
# ===========================================
if page == "Single Query":

    st.title("🔍 Skill Matching - crosswalking")
    st.write("Enter a skill title and description to query the crosswalking endpoint.")

    col1, col2 = st.columns([1, 2])
    with col1:
        title = st.text_input("Skill Title")
    with col2:
        description = st.text_area("Skill Description")

    if st.button("Find Matching Skill", type="primary"):
        if not title or not description:
            st.warning("Both fields are required.")
        else:
            with st.spinner("Calling API..."):
                result, status = call_api(title, description)

            if status is not None:
                st.success(f"API returned HTTP {status}")
                st.subheader("Result")
                st.json(result)

                with st.expander("🔧 Raw API Response Debug"):
                    st.write(result)
            else:
                st.error("API call failed.")
                st.error(result)


# ===========================================
# 2️⃣ BATCH MODE 
# ===========================================
else:
    st.title("📄 Batch Skill Crosswalking")
    st.write("Upload a CSV file with `skill_title` and `skill_description` columns.")

    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Failed to read CSV file: {e}")
            st.stop()

        required_cols = {"skill_title", "skill_description"}
        if not required_cols.issubset(df.columns):
            st.error(f"CSV must contain columns: {required_cols}")
            st.stop()

        st.success(f"Loaded {len(df)} rows.")
        st.write(df.head())

        if st.button("Start Batch Crosswalking", type="primary"):
            st.info("Processing... this may take some time depending on number of rows.")

            results = []

            # Parallel executor with safe number of workers
            max_workers = 5

            progress_bar = st.progress(0)
            status_text = st.empty()

            tasks = []
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Create one task per row
                for i, row in df.iterrows():
                    tasks.append(executor.submit(
                        call_api,
                        str(row["skill_title"]),
                        str(row["skill_description"])
                    ))

                completed = 0

                # Process tasks as they complete
                for future in as_completed(tasks):
                    result, status = future.result()

                    if status is None:
                        # API failure
                        output_row = {
                            "input_skill_title": None,
                            "input_skill_description": None,
                            "output_skill_id": None,
                            "output_skill_title": None,
                            "output_skill_description": None,
                            "score": None,
                            "isDuplicate": None,
                            "error": result.get("error", "Unknown error during API call")
                        }
                    else:
                        # Successful output from your API format
                        output_row = {
                            "input_skill_title": result.get("input_skill_title"),
                            "input_skill_description": result.get("input_skill_description"),
                            "output_skill_id": result.get("output_skill_id"),
                            "output_skill_title": result.get("output_skill_title"),
                            "output_skill_description": result.get("output_skill_description"),
                            "score": result.get("score"),
                            "isDuplicate": result.get("isDuplicate"),
                            "error": None
                        }

                    results.append(output_row)

                    completed += 1
                    progress_bar.progress(completed / len(df))
                    status_text.text(f"Processed {completed}/{len(df)} rows")

            # 🎉 Done
            st.success("Batch processing complete!")

            result_df = pd.DataFrame(results)
            st.dataframe(result_df, use_container_width=True)
