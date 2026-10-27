import streamlit as st

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="SocietyConnect",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- GREEN THEME ----------------

st.sidebar.markdown("# 🌿 SocietyConnect")
st.sidebar.caption("Together, we grow better.")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "🏡 Home",
        "📝 Submit Complaint",
        "🔍 Track Complaint",
        "📊 Community Pulse",
        "🔐 Admin Dashboard"
    ]
)

st.sidebar.divider()
st.sidebar.success("🌱 Building a better community")

# ---------------- HOME PAGE ----------------

if page == "🏡 Home":

    st.title("🌿 SocietyConnect")
    st.caption("YOUR SOCIETY. YOUR VOICE. OUR COMMUNITY.")

    st.success(
        "🌱 Together, We Make Our Society Better."
    )

    st.write(
        "A simple community platform to report society "
        "problems, follow complaint progress, and help "
        "the committee improve everyday life."
    )

    st.divider()

    st.subheader("🏡 Welcome to Your Community")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Small actions. Better living.")

        st.write(
            "From water supply issues to maintenance "
            "problems, SocietyConnect helps residents "
            "communicate their concerns in one place."
        )

        st.info(
            "💚 Your feedback helps build a cleaner, "
            "safer, and happier community."
        )

    with col2:
        st.markdown("### 🌿 Community Promise")

        st.write("💧 Better water management")
        st.write("🧹 Cleaner surroundings")
        st.write("🔧 Faster maintenance")
        st.write("🤝 Better communication")

    st.divider()

    st.subheader("📌 Explore Services")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 💧 Water")
        st.write("Report water supply problems.")

    with col2:
        st.markdown("### 🧹 Cleanliness")
        st.write("Report garbage and hygiene issues.")

    with col3:
        st.markdown("### 🔧 Maintenance")
        st.write("Report repairs and common-area issues.")

    st.divider()

    st.markdown("### 💡 How SocietyConnect Works")

    step1, step2, step3 = st.columns(3)

    with step1:
        st.markdown("#### 1️⃣ Report")
        st.write("Describe the problem.")

    with step2:
        st.markdown("#### 2️⃣ Track")
        st.write("Check complaint progress.")

    with step3:
        st.markdown("#### 3️⃣ Resolve")
        st.write("The committee updates the status.")

    st.info(
        "👈 Use the navigation menu to explore the website."
    )

# ---------------- SUBMIT COMPLAINT ----------------

elif page == "📝 Submit Complaint":

    st.title("📝 Report a Community Issue")

    st.write(
        "Help us improve your society by reporting "
        "a problem below."
    )

    with st.form("complaint_form", clear_on_submit=False):

        name = st.text_input(
            "Resident Name",
            placeholder="Enter your name"
        )

        flat = st.text_input(
            "Flat Number",
            placeholder="Example: A-204"
        )

        category = st.selectbox(
            "Select Complaint Category",
            [
                "Water Supply",
                "Cleanliness / Garbage",
                "Electricity",
                "Lift Problems",
                "Maintenance",
                "Security",
                "Other"
            ]
        )

        priority = st.selectbox(
            "Priority",
            [
                "Normal",
                "High",
                "Urgent"
            ]
        )

        description = st.text_area(
            "Describe the Issue",
            placeholder=(
                "Explain the problem and where it occurred..."
            )
        )

        submitted = st.form_submit_button(
            "🌿 Submit Complaint",
            use_container_width=True
        )

        if submitted:

            if (
                name.strip()
                and flat.strip()
                and description.strip()
            ):

                st.success(
                    "Form validation successful!"
                )

                st.info(
                    "The form is ready for backend integration. "
                    "A permanent complaint ID will be generated "
                    "when the backend and database are connected."
                )

            else:

                st.error(
                    "Please fill in your name, flat number, "
                    "and complaint description."
                )

# ---------------- TRACK COMPLAINT ----------------

elif page == "🔍 Track Complaint":

    st.title("🔍 Track Your Complaint")

    st.write(
        "Check the latest status of your submitted complaint."
    )

    complaint_id = st.text_input(
        "Complaint ID",
        placeholder="Example: SC001"
    )

    if st.button(
        "🔎 Check Status",
        use_container_width=True
    ):

        if complaint_id.strip():

            st.info(
                "Complaint tracking will work after the "
                "database and backend are connected."
            )

        else:

            st.warning(
                "Please enter your complaint ID."
            )

    st.divider()

    st.subheader("🌱 Complaint Journey")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("### 📨")
        st.write("Submitted")

    with col2:
        st.markdown("### 👀")
        st.write("Under Review")

    with col3:
        st.markdown("### 🔧")
        st.write("In Progress")

    with col4:
        st.markdown("### ✅")
        st.write("Resolved")

    st.caption(
        "The actual complaint status will appear "
        "after backend integration."
    )

# ---------------- COMMUNITY PULSE ----------------

elif page == "📊 Community Pulse":

    st.title("🌱 Community Pulse")

    st.write(
        "Understand recurring society problems and "
        "monitor progress towards a better community."
    )

    st.info(
        "The statistics below are placeholders. "
        "They will display actual complaint data after "
        "database integration."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Complaints", "—")

    with col2:
        st.metric("Pending Complaints", "—")

    with col3:
        st.metric("Resolved Complaints", "—")

    st.divider()

    st.subheader("🌿 Community Insights")

    st.write(
        "💧 Water: identify recurring supply problems."
    )

    st.write(
        "🧹 Cleanliness: identify repeated garbage complaints."
    )

    st.write(
        "🔧 Maintenance: identify common repair requirements."
    )

    st.write(
        "💡 Electricity: identify reported electrical issues."
    )

    st.divider()

    st.subheader("💚 Our Community Goal")

    st.success(
        "Every reported problem should receive attention "
        "and a clear status update."
    )

# ---------------- ADMIN DASHBOARD ----------------

elif page == "🔐 Admin Dashboard":

    st.title("🔐 Society Committee Dashboard")

    st.write(
        "A central place for the society committee "
        "to review and manage complaints."
    )

    st.warning(
        "This is a prototype screen, not a secured admin area. "
        "Authentication must be added before real use."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Complaints", "—")

    with col2:
        st.metric("Pending", "—")

    with col3:
        st.metric("Resolved", "—")

    st.divider()

    st.subheader("🛠️ Complaint Management")

    st.write(
        "The complaint table, status update controls, "
        "and committee actions will be added during "
        "backend integration."
    )

    st.subheader("📢 Community Notice Board")

    st.write(
        "Future notices may include water interruptions, "
        "lift maintenance, society meetings")