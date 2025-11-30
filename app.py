import streamlit as st
import requests

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
    page_title="Skill Matching UI",
    page_icon="🔍",
    layout="wide"
)

st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to", ["Single Query", "Batch Mode (Coming Soon)"])

st.sidebar.markdown("---")
st.sidebar.markdown("**API Endpoint**")
st.sidebar.code(API_URL)
st.sidebar.markdown("---")
st.sidebar.info("Built with Streamlit + FastAPI ⚡")


# ===========================================
# 1️⃣ SINGLE QUERY PAGE
# ===========================================
if page == "Single Query":

    st.title("🔍 Skill Matcher")
    st.write("Enter a skill title and description to query the FastAPI endpoint.")

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
# 2️⃣ BATCH MODE PLACEHOLDER
# ===========================================
else:
    st.title("📄 Batch Mode")
    st.write("This feature is coming soon! 🚧")

    st.info(
        "Batch mode will allow you to upload a CSV file with multiple skills and "
        "automatically query the FastAPI endpoint for each row.\n\n"
        "For now, this page is a placeholder."
    )

    st.image(
        "https://cdn-icons-png.flaticon.com/512/565/565654.png",
        width=150,
        caption="Batch mode loading soon!"
    )
