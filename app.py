import io
import json
import os
import re
import hashlib
from datetime import datetime, timezone

import pandas as pd
import streamlit as st
from PIL import Image, ImageChops, ImageStat

from database import init_db, insert_report, fetch_reports, update_report_status, report_stats
from ai_engine import analyze_report
from hotspot import build_hotspot_table, calculate_priority
from verification import compare_images


st.set_page_config(
    page_title="Garbage360 AI",
    page_icon="🚮",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# ---------- Helpers ----------

def get_secret(name: str):
    try:
        value = st.secrets.get(name)
        if value:
            return value
    except Exception:
        pass
    return os.getenv(name)


def image_hash(uploaded_file) -> str | None:
    if uploaded_file is None:
        return None
    raw = uploaded_file.getvalue()
    return hashlib.sha256(raw).hexdigest()


def reset_form():
    for key in ["description", "location", "latitude", "longitude"]:
        st.session_state[key] = ""


# ---------- Styling ----------

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1250px;}
.hero {
    padding: 2rem 2rem 1.8rem 2rem;
    border-radius: 24px;
    background: linear-gradient(135deg, #10251a, #1f4a2d);
    color: white;
    margin-bottom: 1.2rem;
}
.hero h1 {font-size: 3.4rem; margin: 0; letter-spacing: -0.05em;}
.hero h1 span {color: #8fe3a5;}
.hero p {font-size: 1.05rem; color: #d7e9dc; margin-bottom: 0;}
.kicker {font-size: .72rem; font-weight: 800; letter-spacing: .16em; color: #2d7541;}
.card {
    border: 1px solid #e1e9e2;
    border-radius: 16px;
    padding: 1rem 1.1rem;
    background: white;
}
.metric-label {color:#68756c; font-size:.8rem;}
.metric-value {font-size:2rem; font-weight:800;}
.small-muted {color:#748077; font-size:.82rem;}
.priority-p1 {color:#a92727; font-weight:900;}
.priority-p2 {color:#8a5a00; font-weight:900;}
.priority-p3 {color:#2d5a9b; font-weight:900;}
.priority-p4 {color:#56645a; font-weight:900;}
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------

with st.sidebar:
    st.markdown("## 🚮 Garbage360 AI")
    st.caption("AI-first waste intelligence prototype")
    page = st.radio(
        "Go to",
        ["Citizen Report", "Admin Dashboard", "Hotspot Intelligence", "Resolution Verification", "About"],
    )
    st.divider()
    st.markdown("### Demo mode")
    st.caption("You can run the complete project without an API key. Add a Gemini key later for real multimodal image analysis.")
    if st.button("Load demo reports", use_container_width=True):
        demo = [
            {
                "description": "Huge mixed garbage pile beside a blocked drain. Plastic bottles, bags and food waste are scattered on the road.",
                "location": "Nagpur Central",
                "latitude": 21.1458,
                "longitude": 79.0882,
            },
            {
                "description": "Plastic bottles and bags accumulating near a busy market road.",
                "location": "Nagpur Market",
                "latitude": 21.1490,
                "longitude": 79.0940,
            },
            {
                "description": "Small paper waste near a public dustbin.",
                "location": "Nagpur Central",
                "latitude": 21.1465,
                "longitude": 79.0870,
            },
            {
                "description": "Food waste and leaves collecting around a drain.",
                "location": "Nagpur East",
                "latitude": 21.1500,
                "longitude": 79.1050,
            },
        ]
        existing = fetch_reports()
        for item in demo:
            result = analyze_report(item["description"], item["location"], existing)
            insert_report({
                **item,
                **result,
                "image_hash": None,
                "image_name": None,
            })
        st.success("Demo reports loaded.")
        st.rerun()

# ---------- Hero ----------

st.markdown("""
<div class="hero">
  <div class="kicker" style="color:#9bd9a9;">AI-FIRST WASTE MANAGEMENT</div>
  <h1>Garbage<span>360</span> AI</h1>
  <p>Report. Understand. Prioritize. Clean. Verify.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Citizen Report ----------

if page == "Citizen Report":
    st.markdown('<div class="kicker">CITIZEN REPORTING</div>', unsafe_allow_html=True)
    st.title("Tell us what you found")
    st.write("Upload a photo, describe the problem and give a location. The system turns the complaint into an actionable waste report.")

    col1, col2 = st.columns([1.1, 0.9], gap="large")

    with col1:
        image_file = st.file_uploader(
            "Garbage photo",
            type=["jpg", "jpeg", "png", "webp"],
            help="For the final hackathon version this image can be analyzed by a real vision model.",
        )

        if image_file:
            st.image(image_file, caption="Selected image", use_container_width=True)

        description = st.text_area(
            "What is happening?",
            key="description",
            height=130,
            placeholder="Example: Large mixed garbage pile beside a blocked drain. Plastic bottles and food waste are scattered across the road.",
        )

        location = st.text_input(
            "Location",
            key="location",
            placeholder="Example: Nagpur Central",
        )

        c1, c2 = st.columns(2)
        with c1:
            latitude = st.text_input("Latitude (optional)", key="latitude", placeholder="21.1458")
        with c2:
            longitude = st.text_input("Longitude (optional)", key="longitude", placeholder="79.0882")

        submitted = st.button("🚮 Submit & Analyze with AI", type="primary", use_container_width=True)

    with col2:
        st.markdown("### What happens after submission?")
        flow = [
            ("📸", "Report", "Image + text + location"),
            ("🧠", "Understand", "Waste type + severity"),
            ("📍", "Prioritize", "Risk + hotspot signals"),
            ("🚛", "Act", "Assign cleanup"),
            ("✅", "Verify", "Close the issue"),
        ]
        for icon, title, desc in flow:
            st.markdown(
                f"""<div class="card" style="margin-bottom:.6rem;">
                <b>{icon} &nbsp;{title}</b><br><span class="small-muted">{desc}</span>
                </div>""",
                unsafe_allow_html=True,
            )

    if submitted:
        if not description.strip() or not location.strip():
            st.error("Please enter both the description and location.")
        else:
            try:
                lat = float(latitude) if latitude.strip() else None
                lon = float(longitude) if longitude.strip() else None
            except ValueError:
                st.error("Latitude and longitude must be numbers.")
                lat = lon = None

            if (latitude.strip() and lat is None) or (longitude.strip() and lon is None):
                st.stop()

            existing = fetch_reports()
            img_bytes = image_file.getvalue() if image_file else None
            mime_type = image_file.type if image_file else None
            api_key = get_secret("GEMINI_API_KEY")

            with st.spinner("Analyzing the report..."):
                result = analyze_report(
                    description=description,
                    location=location,
                    existing_reports=existing,
                    image_bytes=img_bytes,
                    mime_type=mime_type,
                    api_key=api_key,
                )

            report_id = insert_report({
                "description": description.strip(),
                "location": location.strip(),
                "latitude": lat,
                "longitude": lon,
                "image_hash": image_hash(image_file),
                "image_name": image_file.name if image_file else None,
                **result,
            })

            st.success(f"Report #{report_id} submitted successfully.")

            a, b, c, d = st.columns(4)
            a.metric("Waste type", result["category"])
            b.metric("Severity", result["severity"])
            c.metric("Priority", result["priority"])
            d.metric("Drain risk", result["drain_risk"])

            st.info(f"**Recommended action:** {result['recommended_action']}")
            st.caption(f"Analysis mode: {result['analysis_mode']} | Confidence: {result['confidence']:.0%}")

# ---------- Admin Dashboard ----------

elif page == "Admin Dashboard":
    st.markdown('<div class="kicker">MUNICIPAL DASHBOARD</div>', unsafe_allow_html=True)
    st.title("Waste intelligence dashboard")

    reports = fetch_reports()
    stats = report_stats(reports)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total reports", stats["total"])
    m2.metric("Open reports", stats["open"])
    m3.metric("P1 critical", stats["critical"])
    m4.metric("Resolved", stats["resolved"])

    st.divider()

    if not reports:
        st.info("No reports yet. Go to Citizen Report or load demo reports from the sidebar.")
    else:
        df = pd.DataFrame(reports)
        st.subheader("Reports")

        display_cols = [
            "id", "created_at", "location", "category", "severity",
            "priority", "drain_risk", "status"
        ]
        st.dataframe(
            df[display_cols],
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Manage a report")
        selected_id = st.selectbox("Select report ID", df["id"].tolist())
        selected = df[df["id"] == selected_id].iloc[0]

        st.write(f"**Description:** {selected['description']}")
        st.write(f"**Recommended action:** {selected['recommended_action']}")

        new_status = st.selectbox(
            "Update status",
            ["Reported", "Verified", "Assigned", "In Progress", "Resolved"],
            index=["Reported", "Verified", "Assigned", "In Progress", "Resolved"].index(selected["status"]),
        )

        if st.button("Update status", type="primary"):
            update_report_status(int(selected_id), new_status)
            st.success("Status updated.")
            st.rerun()

        st.download_button(
            "Download reports as CSV",
            df.to_csv(index=False).encode("utf-8"),
            "garbage360_reports.csv",
            "text/csv",
        )

# ---------- Hotspot Intelligence ----------

elif page == "Hotspot Intelligence":
    st.markdown('<div class="kicker">LOCATION INTELLIGENCE</div>', unsafe_allow_html=True)
    st.title("Garbage hotspot intelligence")
    st.write("Repeated reports from the same area are grouped into a simple hotspot signal. Add real GPS coordinates to make the map more useful.")

    reports = fetch_reports()

    if not reports:
        st.info("Load demo reports from the sidebar first.")
    else:
        hotspot_df = build_hotspot_table(reports)

        st.subheader("Hotspot summary")
        st.dataframe(hotspot_df, use_container_width=True, hide_index=True)

        map_df = pd.DataFrame(reports)
        map_df = map_df.dropna(subset=["latitude", "longitude"])
        if not map_df.empty:
            st.subheader("Report map")
            st.map(map_df[["latitude", "longitude"]], zoom=11)
        else:
            st.warning("No GPS coordinates available for mapping.")

        st.subheader("Priority logic")
        st.write(
            "The prototype combines severity, drain risk and repeated reports. "
            "For the final hackathon build, this should become a validated ML/risk model."
        )

# ---------- Verification ----------

elif page == "Resolution Verification":
    st.markdown('<div class="kicker">CLEANUP VERIFICATION</div>', unsafe_allow_html=True)
    st.title("Before → after cleanup verification")
    st.write("Upload the original and cleanup photos. The prototype calculates a simple visual-change score. This is a demo feature; a production version should use a trained vision model.")

    before = st.file_uploader("Before cleanup", type=["jpg", "jpeg", "png", "webp"], key="before")
    after = st.file_uploader("After cleanup", type=["jpg", "jpeg", "png", "webp"], key="after")

    if before and after:
        left, right = st.columns(2)
        with left:
            st.image(before, caption="Before", use_container_width=True)
        with right:
            st.image(after, caption="After", use_container_width=True)

        if st.button("🔎 Verify cleanup", type="primary"):
            result = compare_images(
                Image.open(io.BytesIO(before.getvalue())).convert("RGB"),
                Image.open(io.BytesIO(after.getvalue())).convert("RGB"),
            )
            st.metric("Visual change score", f"{result['change_score']:.0%}")
            if result["verified"]:
                st.success("The images show enough visual change to pass the demo verification.")
            else:
                st.warning("The images are still visually similar. Manual verification is recommended.")

# ---------- About ----------

else:
    st.markdown('<div class="kicker">ABOUT THE PROJECT</div>', unsafe_allow_html=True)
    st.title("Why Garbage360 AI?")
    st.write(
        "The project evolves a citizen-first civic reporting concept into a focused "
        "AI-first waste management platform."
    )

    st.subheader("Core idea")
    st.markdown("""
    **Detect → Understand → Prioritize → Assign → Clean → Verify**

    Instead of treating every complaint equally, Garbage360 AI attempts to answer:

    > **Which garbage problem needs attention first, and why?**
    """)

    st.subheader("Hackathon tracks we can connect to")
    tracks = pd.DataFrame({
        "Track": [
            "Civic Education",
            "Street Action",
            "Waste Collection & Segregation",
            "Drain Monitoring",
            "Recycling & Circular Economy",
            "Hardware & IoT",
        ],
        "Garbage360 feature": [
            "AI segregation guidance",
            "Citizen garbage reporting",
            "Waste classification + priority",
            "Drain-risk detection",
            "Recyclable material identification",
            "Future smart-bin/sensor integration",
        ],
    })
    st.dataframe(tracks, use_container_width=True, hide_index=True)

    st.subheader("Current vs final version")
    st.info(
        "The included project is a complete, runnable MVP. The next major upgrade is "
        "to connect the AI engine to a real waste-image model and then add stronger "
        "duplicate detection, hotspot clustering and route optimization."
    )
