import hashlib
import hmac
import secrets
import sqlite3
from pathlib import Path

import streamlit as st
import database as db

st.set_page_config(
    page_title="SocietyConnect",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.create_database()


# ---------------- ACCOUNT BACKEND ----------------
def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 300000
    ).hex()


def create_account(name, email, flat_number, password):
    name, email, flat_number = name.strip(), email.strip().lower(), flat_number.strip()
    if not name or not email or not flat_number or not password:
        return False, "Please fill in all fields."
    if "@" not in email or "." not in email.split("@")[-1]:
        return False, "Please enter a valid email address."
    if len(password) < 8:
        return False, "Password must contain at least 8 characters."
    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)
    try:
        with db.get_connection() as conn:
            conn.execute(
                """INSERT INTO users
                   (name, email, flat_number, password_hash, salt, role)
                   VALUES (?, ?, ?, ?, ?, 'resident')""",
                (name, email, flat_number, password_hash, salt),
            )
        return True, "Account created successfully. You can now log in."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."


def authenticate_user(email, password):
    with db.get_connection() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE email=? COLLATE NOCASE",
            (email.strip().lower(),),
        ).fetchone()
    if not user:
        return None
    entered_hash = hash_password(password, user["salt"])
    if not hmac.compare_digest(entered_hash, user["password_hash"]):
        return None
    return {
        "id": user["id"], "name": user["name"], "email": user["email"],
        "flat_number": user["flat_number"], "role": user["role"],
    }


def show_complaints(rows):
    if not rows:
        st.info("No complaints found.")
        return
    display_rows = []
    for item in rows:
        display_rows.append({
            "Complaint ID": item["tracking_id"],
            "Category": item["category"],
            "Location": item["location"],
            "Priority": item.get("priority", "Normal"),
            "Status": item["status"],
            "Submitted": item["created_at"],
            "Description": item["description"],
        })
    st.dataframe(display_rows, use_container_width=True, hide_index=True)


# ---------------- LOGIN / SIGNUP ----------------
if "current_user" not in st.session_state:
    st.session_state.current_user = None

if st.session_state.current_user is None:
    st.title("🌿 SocietyConnect")
    st.caption("Your Society. Your Voice. Our Community.")
    login_tab, signup_tab = st.tabs(["🔐 Login", "📝 Create Account"])

    with login_tab:
        with st.form("login_form"):
            login_email = st.text_input("Email Address")
            login_password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login", use_container_width=True)
        if login_button:
            user = authenticate_user(login_email, login_password)
            if user:
                st.session_state.current_user = user
                st.rerun()
            else:
                st.error("Incorrect email or password.")

    with signup_tab:
        with st.form("signup_form"):
            new_name = st.text_input("Full Name")
            new_email = st.text_input("Email Address", key="signup_email")
            new_flat = st.text_input("Flat Number", placeholder="Example: A-204")
            new_password = st.text_input("Create Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            signup_button = st.form_submit_button("Create Account", use_container_width=True)
        if signup_button:
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                ok, message = create_account(new_name, new_email, new_flat, new_password)
                (st.success if ok else st.error)(message)
    st.stop()


# ---------------- NAVIGATION ----------------
current_user = st.session_state.current_user
is_admin = current_user["role"] == "admin"

st.sidebar.markdown("# 🌿 SocietyConnect")
st.sidebar.caption("Together, we grow better.")
st.sidebar.success(f"Logged in as: {current_user['name']}")
st.sidebar.caption(f"Role: {current_user['role'].title()}")

if st.sidebar.button("Logout"):
    st.session_state.current_user = None
    st.rerun()

pages = ["🏡 Home", "📝 Submit Complaint", "🔍 Track Complaint", "📊 Community Pulse"]
if is_admin:
    pages.append("🔐 Admin Dashboard")
st.sidebar.divider()
page = st.sidebar.radio("NAVIGATION", pages)
st.sidebar.divider()
st.sidebar.success("🌱 Building a better community")


# ---------------- HOME ----------------
if page == "🏡 Home":
    st.title("🌿 SocietyConnect")
    st.caption("YOUR SOCIETY. YOUR VOICE. OUR COMMUNITY.")
    st.success("🌱 Together, We Make Our Society Better.")
    st.write(
        "A community platform to report society problems, track complaint progress, "
        "and help the committee improve everyday life."
    )
    st.divider()
    st.subheader(f"🏡 Welcome, {current_user['name']}!")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("### Small actions. Better living.")
        st.write("Report water supply, cleanliness, maintenance, security, and other issues.")
        st.info("💚 Your feedback helps build a cleaner, safer, happier society.")
    with c2:
        st.markdown("### 🌿 Community Promise")
        st.write("💧 Better water management")
        st.write("🧹 Cleaner surroundings")
        st.write("🔧 Faster maintenance")
        st.write("🤝 Better communication")
    st.divider()
    st.subheader("💡 How SocietyConnect Works")
    a, b, c = st.columns(3)
    a.markdown("#### 1️⃣ Report"); a.write("Submit a complaint and receive a tracking ID.")
    b.markdown("#### 2️⃣ Track"); b.write("Check the latest status of your complaint.")
    c.markdown("#### 3️⃣ Resolve"); c.write("The committee updates progress.")

# ---------------- SUBMIT COMPLAINT ----------------
elif page == "📝 Submit Complaint":
    st.title("📝 Report a Community Issue")
    st.write("Your account details are filled in automatically.")
    with st.form("complaint_form", clear_on_submit=True):
        st.text_input("Resident Name", value=current_user["name"], disabled=True)
        st.text_input("Flat Number", value=current_user["flat_number"], disabled=True)
        category = st.selectbox("Complaint Category", [
            "Water Supply", "Cleanliness / Garbage", "Electricity", "Lift Problems",
            "Maintenance", "Security", "Parking", "Noise", "Other"
        ])
        location = st.text_input("Problem Location", placeholder="Example: Building A, lift lobby")
        priority = st.selectbox("Priority", ["Normal", "High", "Urgent"])
        description = st.text_area("Describe the Issue", placeholder="Explain the problem clearly...")
        submitted = st.form_submit_button("🌿 Submit Complaint", use_container_width=True)
        if submitted:
            if not location.strip() or not description.strip():
                st.error("Please enter the problem location and description.")
            else:
                try:
                    cid = db.add_complaint(
                    current_user["name"],
                    current_user["flat_number"],
                    category,
                    location,
                    description,
                    priority,
                    current_user["id"]
                    )
                    st.success("Complaint submitted successfully!")
                    st.info(f"Your complaint tracking ID is SC{cid:05d}.")
                except Exception as exc:
                    st.error(f"Could not save complaint: {exc}")



            # try:
            #     cid = db.add_complaint(
            #         current_user["name"], current_user["flat_number"], category,
            #         location, description, priority, current_user["id"]
            #     )
            #     st.success("Complaint submitted successfully!")
            #     st.info(f"Your complaint tracking ID is **SC{cid:05d}**. Save this ID to track progress.")
            # except (sqlite3.Error, ValueError) as exc:
            #     st.error(f"Could not save the complaint. Please try again. Details: {exc}")
            
            # try:
            #     new_id = add_complaint(
            #         current_user["id"],
            #         resident_name,
            #         flat_number,
            #         category,
            #         location,
            #         priority,
            #         description
            #     )
            #     st.success("Complaint submitted successfully!")
            #     st.info(f"Your tracking ID is SC{new_id:05d}")

            # except Exception as exc:
            #     st.error(f"Complaint submission failed: {exc}")


# ---------------- TRACK COMPLAINT ----------------
elif page == "🔍 Track Complaint":
    st.title("🔍 Track Your Complaint")
    st.write("Enter the tracking ID given when you submitted the complaint.")
    with st.form("track_form"):
        complaint_id = st.text_input("Complaint ID", placeholder="Example: SC00001")
        track_button = st.form_submit_button("🔎 Check Status", use_container_width=True)
    if track_button:
        if not complaint_id.strip():
            st.warning("Please enter your complaint ID.")
        else:
            item = db.get_complaint(
                complaint_id, user_id=current_user["id"], is_admin=is_admin
            )
            if item:
                st.subheader(f"Complaint {item['tracking_id']}")
                status = item["status"]
                if status == "Resolved":
                    st.success(f"Status: {status} ✅")
                elif status == "In Progress":
                    st.warning(f"Status: {status} 🔧")
                else:
                    st.info(f"Status: {status} 📨")
                st.write(f"**Category:** {item['category']}")
                st.write(f"**Location:** {item['location']}")
                st.write(f"**Priority:** {item.get('priority', 'Normal')}")
                st.write(f"**Description:** {item['description']}")
                st.write(f"**Submitted:** {item['created_at']}")
            else:
                st.error("Complaint not found in your account. Check the ID or contact the committee.")
    st.divider()
    st.subheader("🌱 Complaint Journey")
    c1, c2, c3 = st.columns(3)
    c1.markdown("### 📨 Submitted")
    c2.markdown("### 🔧 In Progress")
    c3.markdown("### ✅ Resolved")

# ---------------- COMMUNITY PULSE ----------------
elif page == "📊 Community Pulse":
    st.title("🌱 Community Pulse")
    st.write("Live statistics from the SocietyConnect database.")
    stats = db.get_complaint_stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Complaints", stats["total"])
    c2.metric("Submitted", stats["submitted"])
    c3.metric("In Progress", stats["in_progress"])
    c4.metric("Resolved", stats["resolved"])
    st.divider()
    st.subheader("📌 Complaints by Category")
    if stats["by_category"]:
        st.bar_chart({r["category"]: r["count"] for r in stats["by_category"]})
    else:
        st.info("No complaint data available yet.")
    st.divider()
    st.success("Every reported problem should receive attention and a clear status update.")

# ---------------- ADMIN DASHBOARD ----------------
elif page == "🔐 Admin Dashboard":
    if not is_admin:
        st.error("Admin access required.")
        st.stop()
    st.title("🔐 Society Committee Dashboard")
    stats = db.get_complaint_stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", stats["total"])
    c2.metric("Submitted", stats["submitted"])
    c3.metric("In Progress", stats["in_progress"])
    c4.metric("Resolved", stats["resolved"])
    st.divider()
    st.subheader("🛠️ Complaint Management")
    rows = db.get_all_complaints(is_admin=True)
    if not rows:
        st.info("No complaints have been submitted yet.")
    else:
        show_complaints(rows)
        st.divider()
        options = {f"{r['tracking_id']} — {r['category']} — {r['resident_name']}": r["id"] for r in rows}
        selected_label = st.selectbox("Select complaint to update", list(options.keys()))
        selected_id = options[selected_label]
        current_item = next(r for r in rows if r["id"] == selected_id)
        new_status = st.selectbox(
            "New status", db.STATUSES,
            index=db.STATUSES.index(current_item["status"]) if current_item["status"] in db.STATUSES else 0
        )
        if st.button("Update Complaint Status", use_container_width=True):
            if db.update_status(selected_id, new_status):
                st.success(f"{current_item['tracking_id']} updated to {new_status}.")
                st.rerun()
            else:
                st.error("Status could not be updated.")
    st.divider()
    st.subheader("📢 Community Notice Board")
    st.write("Committee notices can be added to this section in a future version.")
