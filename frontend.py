import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/find-similar"
UPLOAD_URL = "http://127.0.0.1:8000/upload-fir"

st.set_page_config(
    page_title="Kerala Police FIR System",
    layout="wide"
)


# ---------------- STYLE ----------------

st.markdown("""
<style>

.main-header {
    font-size:42px;
    font-weight:bold;
    color:#0B3D91;
}

.sub-header {
    font-size:18px;
    color:#555;
}

.result-card {
    background:white;
    padding:18px;
    border-radius:10px;
    border-left:6px solid #0B3D91;
    margin-bottom:12px;
    box-shadow:0px 2px 8px rgba(0,0,0,0.08);
}

.similarity {
    color:#D4AF37;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------

st.markdown(
    "<div class='main-header'> Kerala Police FIR Analysis System</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='sub-header'>AI-powered FIR Similarity & Investigation Tool</div>",
    unsafe_allow_html=True
)

st.divider()


# ---------------- SIDEBAR ----------------

st.sidebar.title("Police Tools")

mode = st.sidebar.radio(
    "Select Action",
    ["Search by Narrative", "Upload FIR PDF"]
)

top_k = st.sidebar.slider(
    "Similar FIRs",
    1,
    10,
    5
)


# ---------------- MAIN LAYOUT ----------------

col1, col2 = st.columns([1,1])


# LEFT PANEL (INPUT)
with col1:

    if mode == "Search by Narrative":

        st.subheader("Enter FIR Narrative")

        narrative = st.text_area(
            "Paste FIR Narrative",
            height=300
        )

        if st.button("Find Similar FIRs"):

            if narrative.strip() == "":
                st.warning("Enter FIR narrative first.")

            else:

                response = requests.post(
                    API_URL,
                    json={
                        "narrative": narrative,
                        "top_k": top_k
                    }
                )

                if response.status_code == 200:

                    st.session_state["results"] = response.json()["similar_firs"]

                else:
                    st.error("API Error")


    if mode == "Upload FIR PDF":

        st.subheader("Upload FIR Document")

        uploaded_file = st.file_uploader(
            "Upload FIR PDF",
            type=["pdf"]
        )

        if uploaded_file:

            response = requests.post(
                UPLOAD_URL,
                files={"file": uploaded_file.getvalue()}
            )

            if response.status_code == 200:

                data = response.json()

                st.write("### Extracted Narrative")
                st.write(data["narrative"])

                st.session_state["results"] = data["similar_firs"]

            else:
                st.error("Upload failed")


# RIGHT PANEL (RESULTS)

with col2:

    st.subheader("Similar FIR Cases")

    if "results" in st.session_state:

        for r in st.session_state["results"]:

            st.markdown(f"""
            <div class="result-card">

            <b>FIR File:</b> {r['file']} <br>
            <span class="similarity">
            Similarity Score: {round(r['score'],3)}
            </span>

            </div>
            """, unsafe_allow_html=True)

            with st.expander("View FIR Details"):

                if "acts" in r:
                    st.write("**Acts / Sections**")
                    st.write(r["acts"])

                if "accused" in r:
                    st.write("**Accused**")
                    st.write(r["accused"])

                if "narrative" in r:
                    st.write("**Narrative**")
                    st.write(r["narrative"])

    else:

        st.info("Results will appear here.")