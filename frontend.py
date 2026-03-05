import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/find-similar"

st.title("🚔 FIR Similarity Engine")

st.write("Paste FIR Narrative Below")

narrative = st.text_area("FIR Narrative", height=250)

top_k = st.slider("Number of similar cases", 1, 10, 5)

if st.button("Find Similar FIRs"):
    if narrative.strip() == "":
        st.warning("Please enter FIR narrative.")
    else:
        response = requests.post(
            API_URL,
            json={
                "narrative": narrative,
                "top_k": top_k
            }   
        )

        if response.status_code == 200:
            results = response.json()["similar_firs"]

            st.subheader("🔎 Similar FIRs Found")

            for r in results:
                st.write(f"**File:** {r['file']}")
                st.write(f"Score: {round(r['score'], 4)}")
                st.write("---")
        else:
            st.error("API Error")
st.subheader("Or Upload FIR PDF")

uploaded_file = st.file_uploader("Upload FIR PDF", type=["pdf"])

if uploaded_file:
    response = requests.post(
        "http://127.0.0.1:8000/upload-fir",
        files={"file": uploaded_file.getvalue()}
    )

    if response.status_code == 200:
        data = response.json()

        st.subheader("Extracted Narrative")
        st.write(data["narrative"])

        st.subheader("Similar FIRs")

        for r in data["similar_firs"]:
            st.write(f"File: {r['file']} | Score: {round(r['score'], 4)}")