import streamlit as st
from datetime import datetime, timedelta

# ---------------------------------------------------------
# SHARED GLOBAL STATE (Connects all 3 websites in real time)
# ---------------------------------------------------------
@st.cache_resource
def get_shared_bank_state():
    return {
        "accounts": {
            "Siddhant Shithole (ACC-101)": {
                "balance": 50000.0,
                "pin": "1234",
                "cvv": "842",
                "password": "Siddhant123",
                "biometric_token": "BIO-SIDDHANT-OK",
                "failed_attempts": 0,
                "locked_until": None,
                "last_active_time": None,
                "last_action_summary": "Idle",
                "credentials_leaked": False,
                "leak_reason": ""
            },
            "Prithviraj Chavan (ACC-102)": {
                "balance": 75000.0,
                "pin": "4321",
                "cvv": "319",
                "password": "Pr1thv1r@j123",
                "biometric_token": "BIO-PRITHVIRAJ-OK",
                "failed_attempts": 0,
                "locked_until": None,
                "last_active_time": None,
                "last_action_summary": "Idle",
                "credentials_leaked": False,
                "leak_reason": ""
            },
            "Jagriti Gattani (ACC-103)": {
                "balance": 32000.0,
                "pin": "9876",
                "cvv": "507",
                "password": "J@gr1t1_l0l",
                "biometric_token": "BIO-JAGRITI-OK",
                "failed_attempts": 0,
                "locked_until": None,
                "last_active_time": None,
                "last_action_summary": "Idle",
                "credentials_leaked": False,
                "leak_reason": ""
            }
        },
        "pending_approvals": [],
        "logs": []
    }

state = get_shared_bank_state()

# Bank SOC Admin Passcode 
SOC_ADMIN_PASSCODE = "F13ld_pr0j3ct"

# Read URL parameter (?site=victim, ?site=hacker, or ?site=bank)
current_site = st.query_params.get("site", "victim").lower()

page_titles = {
    "victim": ("SecurePay | Personal Banking", "📱", "centered"),
    "hacker": ("SecurePay | Adversary Terminal", "🕵️", "centered"),
    "bank": ("SecurePay | Bank SOC Command Center", "🛡️", "wide")
}
title_text, icon_text, layout_mode = page_titles.get(current_site, page_titles["victim"])

st.set_page_config(page_title=title_text, page_icon=icon_text, layout=layout_mode)

# Helper: Check 7-day lockout status
def check_lock_status(acc):
    if acc["locked_until"] is not None:
        if datetime.now() < acc["locked_until"]:
            return True, acc["locked_until"] - datetime.now()
        else:
            acc["locked_until"] = None
            acc["failed_attempts"] = 0
    return False, None

# Helper: Check if user is actively transacting right now (within last 25 seconds)
def is_user_currently_transacting(acc):
    if acc["last_active_time"] is None:
        return False
    return (datetime.now() - acc["last_active_time"]).total_seconds() <= 25

# Helper: Record audit log
def add_log(user, actor, method, amount, status, details):
    state["logs"].insert(0, {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Account": user,
        "Initiator": actor,
        "Auth Method": method,
        "Amount": f"₹{amount:,.2f}",
        "Status": status,
        "Details": details
    })

# ---------------------------------------------------------
# WEBSITES 1 & 2: VICTIM APP & HACKER TERMINAL
# ---------------------------------------------------------
def render_payment_portal(actor_role):
    is_hacker = (actor_role == "Hacker")

    top_col1, top_col2 = st.columns([4, 1])
    with top_col1:
        if is_hacker:
            st.title("🕵️ Adversary Attack Terminal")
            st.caption("Website 2 of 3 — External Attacker Spoofing Customer Payment Gateway")
        else:
            st.title("📱 SecurePay Personal Banking")
            st.caption("Website 1 of 3 — Legitimate Customer Payment Portal")
    with top_col2:
        st.write("")
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    label_text = "🎯 Select Target Victim Account" if is_hacker else "Select Your Account"
    selected_user = st.selectbox(label_text, list(state["accounts"].keys()))
    account = state["accounts"][selected_user]

    # Hacker-only Phishing Intercept Feed
    if is_hacker:
        st.divider()
        st.subheader("📡 Intercepted Phishing & Recon Feed")
        if account["credentials_leaked"]:
            st.error(
                f"🔓 **HUMAN ERROR EXPLOITED!** Captured stolen credentials for **{selected_user}**:\n\n"
                f"- **4-Digit PIN:** `{account['pin']}`\n"
                f"- **Card CVV:** `{account['cvv']}`\n"
                f"- **Password:** `{account['password']}`\n"
                f"- **Biometric Status:** Hardware-bound (Cannot be phished remotely!)"
            )
        else:
            st.info(
                "🔒 **Target is cautious — No leaked credentials intercepted.**\n\n"
                "You have no stolen PIN/Password. Guessing credentials will trigger the bank's 5-attempt 7-day lockout."
            )

    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("Account Balance", f"₹{account['balance']:,.2f}")
    col2.metric("Failed Security Attempts", f"{account['failed_attempts']} / 5")

    is_locked, remaining_time = check_lock_status(account)

    if is_locked:
        days = remaining_time.days
        hours, rem = divmod(remaining_time.seconds, 3600)
        minutes, _ = divmod(rem, 60)
        st.error(
            f"🚨 **ACCOUNT LOCKED FOR 7 DAYS** due to 5 failed security attempts or SOC security block.\n\n"
            f"Time remaining: **{days} days, {hours} hours, {minutes} minutes**."
        )
    else:
        st.subheader("💸 Initiate Fund Transfer")
        default_recipient = "offshore.mule99@upi" if is_hacker else "merchant.store@upi"
        default_amount = 20000.0 if is_hacker else 2500.0

        recipient = st.text_input("Recipient UPI / Account ID", value=default_recipient)
        amount = st.number_input("Amount (₹)", min_value=100.0, max_value=100000.0, value=default_amount, step=500.0)

        auth_method = st.radio(
            "Choose Multi-Factor Authentication (MFA) Method:",
            [
                "1. PIN + Biometric Verification",
                "2. PIN + Debit Card Security Code (CVV)",
                "3. PIN + Account Password"
            ]
        )

        with st.form(f"{actor_role}_payment_form"):
            entered_pin = st.text_input("Enter 4-Digit ATM/UPI PIN", type="password", max_chars=4)

            biometric_verified = False
            entered_cvv = ""
            entered_password = ""

            if auth_method.startswith("1."):
                if is_hacker:
                    biometric_verified = st.checkbox("🧬 Attempt Biometric Spoof (Fails without victim's physical device)")
                else:
                    biometric_verified = st.checkbox("👆 Tap to Scan Fingerprint / Face ID (Simulated Biometric)")
            elif auth_method.startswith("2."):
                entered_cvv = st.text_input("Enter 3-Digit Security Number (Back of Debit Card)", type="password", max_chars=3)
            elif auth_method.startswith("3."):
                entered_password = st.text_input("Enter Banking Password", type="password")

            btn_label = "⚡ Execute Unauthorized Transfer" if is_hacker else "Authorize & Send Money"
            submit_payment = st.form_submit_button(btn_label, use_container_width=True)

            if submit_payment:
                # Mark user as actively transacting right now (triggers highlight on Bank SOC)
                account["last_active_time"] = datetime.now()

                if amount > account["balance"]:
                    st.warning("Insufficient balance for this transaction.")
                else:
                    auth_passed = False
                    if auth_method.startswith("1."):
                        auth_passed = (not is_hacker) and (entered_pin == account["pin"]) and biometric_verified
                    elif auth_method.startswith("2."):
                        auth_passed = (entered_pin == account["pin"]) and (entered_cvv == account["cvv"])
                    elif auth_method.startswith("3."):
                        auth_passed = (entered_pin == account["pin"]) and (entered_password == account["password"])

                    if auth_passed:
                        account["failed_attempts"] = 0
                        tx_id = f"TXN-{1000 + len(state['logs']) + 1}"
                        account["last_action_summary"] = f"Paying ₹{amount:,.0f} ({auth_method[:6]})"
                        state["pending_approvals"].append({
                            "tx_id": tx_id,
                            "user": selected_user,
                            "actor": actor_role,
                            "recipient": recipient,
                            "amount": amount,
                            "method": auth_method,
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "status": "Pending"
                        })
                        add_log(selected_user, actor_role, auth_method, amount, "PENDING SOC PERMISSION", f"To {recipient}")
                        st.success(f"✅ Authentication Passed! Request **{tx_id}** sent to Bank SOC for final permission.")
                    else:
                        account["failed_attempts"] += 1
                        remaining_tries = 5 - account["failed_attempts"]
                        account["last_action_summary"] = f"Failed Auth ({account['failed_attempts']}/5)"
                        if account["failed_attempts"] >= 5:
                            account["locked_until"] = datetime.now() + timedelta(days=7)
                            add_log(selected_user, actor_role, auth_method, amount, "LOCKED (7 DAYS)", "5 consecutive failed attempts")
                            st.error("🚨 5 incorrect attempts reached! Account has been locked for 7 days.")
                            st.rerun()
                        else:
                            fail_note = "Biometric hardware mismatch" if (is_hacker and auth_method.startswith("1.")) else f"{remaining_tries} attempts left"
                            add_log(selected_user, actor_role, auth_method, amount, "FAILED AUTH", fail_note)
                            st.error(f"❌ Authentication Failed! Only **{remaining_tries}** attempts remaining before a 7-day lockout.")

    # Victim-only Human Error Simulator
    if not is_hacker:
        st.divider()
        with st.expander("⚠️ Human Vulnerability Simulator (Phishing / Social Engineering)"):
            st.write(
                "In real-world banking security, systems rarely fail on their own—**human error** exposes credentials. "
                "Click below to simulate the victim accidentally entering their details on a fake KYC/reward link."
            )
            col_a, col_b = st.columns(2)
            if col_a.button("🎣 Fall for Fake KYC Phishing Link"):
                account["credentials_leaked"] = True
                account["leak_reason"] = "Victim submitted PIN, CVV & Password on a fake bank KYC SMS link."
                add_log(selected_user, "Victim (Human Error)", "Phishing Link", 0, "CREDENTIALS LEAKED", account["leak_reason"])
                st.warning("Credentials leaked! The Hacker terminal can now see this victim's stolen details.")

            if col_b.button("🛡️ Secure Credentials (Reset Leak)"):
                account["credentials_leaked"] = False
                account["leak_reason"] = ""
                st.info("Credentials secured again.")

# ---------------------------------------------------------
# WEBSITE 3: SECURED BANK SOC & MASTER COMMAND CENTER
# ---------------------------------------------------------
def render_bank_soc():
    if "soc_authenticated" not in st.session_state:
        st.session_state.soc_authenticated = False

    # Security Gate so Hacker cannot access Bank Command Center
    if not st.session_state.soc_authenticated:
        st.title("🛡️ SecurePay Bank SOC — Restricted Access")
        st.warning("Authorized Security Operations Center (SOC) Personnel Only. Unauthorized access attempts are blocked.")
        with st.form("soc_login_form"):
            passcode = st.text_input("Enter Bank SOC Admin Passcode", type="password")
            if st.form_submit_button("Authenticate SOC Session"):
                if passcode == SOC_ADMIN_PASSCODE:
                    st.session_state.soc_authenticated = True
                    st.rerun()
                else:
                    add_log("SYSTEM-SOC", "Unknown Intruder", "Admin Portal", 0, "INTRUSION BLOCKED", "Invalid SOC Passcode")
                    st.error("🚫 Access Denied: Invalid SOC Admin Passcode.")
        return

    # Header Bar
    h_col1, h_col2, h_col3 = st.columns([5, 1, 1])
    with h_col1:
        st.title("🛡️ Bank SOC & Master Command Center")
        st.caption("Website 3 of 3 — Real-Time Transaction Permission, Fraud Detection & Live User Monitor")
    with h_col2:
        st.write("")
        if st.button("🔄 Refresh Live Feed", use_container_width=True):
            st.rerun()
    with h_col3:
        st.write("")
        if st.button("♻️ Reset Demo", use_container_width=True):
            for acc in state["accounts"].values():
                acc["failed_attempts"] = 0
                acc["locked_until"] = None
                acc["last_active_time"] = None
                acc["last_action_summary"] = "Idle"
                acc["credentials_leaked"] = False
            state["pending_approvals"].clear()
            state["logs"].clear()
            st.rerun()

    st.divider()

    # MASTER LAYOUT: 75% Bank SOC (Left) | 25% Tiny Live User Terminals (Right)
    bank_area, user_terminals_area = st.columns([3, 1], gap="large")

    # -----------------------------------------------------
    # LEFT (LARGE AREA): BANK MONITORING & PERMISSION ENGINE
    # -----------------------------------------------------
    with bank_area:
        # Top KPIs
        pending_list = [tx for tx in state["pending_approvals"] if tx["status"] == "Pending"]
        locked_count = sum(1 for acc in state["accounts"].values() if check_lock_status(acc)[0])
        leaked_count = sum(1 for acc in state["accounts"].values() if acc["credentials_leaked"])

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Pending Permissions", len(pending_list))
        m2.metric("Locked Accounts (7d)", locked_count)
        m3.metric("Phishing Exposure Alerts", leaked_count)
        m4.metric("Total Audited Events", len(state["logs"]))

        st.subheader("🚦 Live Transaction Permission Queue")
        if not pending_list:
            st.info("No transactions currently waiting for bank authorization.")
        else:
            for tx in pending_list:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    with c1:
                        st.markdown(
                            f"**{tx['tx_id']}** | Account: **{tx['user']}**  \n"
                            f"Amount: **₹{tx['amount']:,.2f}** $\\rightarrow$ Recipient: `{tx['recipient']}`  \n"
                            f"MFA Used: `{tx['method']}` | Time: `{tx['time']}`"
                        )
                    with c2:
                        if st.button("✅ Allow", key=f"allow_{tx['tx_id']}", use_container_width=True):
                            acc = state["accounts"][tx["user"]]
                            if acc["balance"] >= tx["amount"]:
                                acc["balance"] -= tx["amount"]
                                tx["status"] = "Approved"
                                acc["last_action_summary"] = f"Approved ₹{tx['amount']:,.0f}"
                                add_log(tx["user"], "Bank SOC", tx["method"], tx["amount"], "APPROVED & SETTLED", f"To {tx['recipient']}")
                                st.rerun()
                    with c3:
                        if st.button("🚫 Block (7d Lock)", key=f"block_{tx['tx_id']}", use_container_width=True):
                            acc = state["accounts"][tx["user"]]
                            tx["status"] = "Blocked"
                            acc["locked_until"] = datetime.now() + timedelta(days=7)
                            acc["last_action_summary"] = "Blocked by Bank (7d)"
                            add_log(tx["user"], "Bank SOC", tx["method"], tx["amount"], "BLOCKED & LOCKED (7D)", "Flagged malicious by SOC")
                            st.rerun()

        st.subheader("🔒 7-Day Account Lockout & Security Status")
        for uname, acc in state["accounts"].items():
            is_locked, rem = check_lock_status(acc)
            if is_locked:
                days = rem.days
                hours, r = divmod(rem.seconds, 3600)
                mins, _ = divmod(r, 60)
                lcol1, lcol2 = st.columns([4, 1])
                lcol1.error(f"**{uname}** — LOCKED ({days}d {hours}h {mins}m remaining) | Failed Attempts: {acc['failed_attempts']}/5")
                if lcol2.button("Unlock", key=f"unlock_{uname}", use_container_width=True):
                    acc["locked_until"] = None
                    acc["failed_attempts"] = 0
                    acc["last_action_summary"] = "Unlocked by SOC"
                    add_log(uname, "Bank SOC", "Admin Override", 0, "ACCOUNT UNLOCKED", "Manual SOC clearance")
                    st.rerun()

        st.subheader("📜 Live Security & Transaction Audit Feed")
        if state["logs"]:
            st.dataframe(state["logs"], use_container_width=True, hide_index=True)
        else:
            st.caption("Waiting for live transactions from Website 1 (Victim) or Website 2 (Hacker)...")

    # -----------------------------------------------------
    # RIGHT (TINY AREAS): LIVE HIGHLIGHTED PERSONAL USERS
    # -----------------------------------------------------
    with user_terminals_area:
        st.subheader("📱 Live User Terminals")
        st.caption("Active transacting users highlight automatically")

        for uname, acc in state["accounts"].items():
            active_now = is_user_currently_transacting(acc)
            is_locked, _ = check_lock_status(acc)

            if active_now:
                # Highlighted card for users currently doing a payment
                st.markdown(
                    f"""
                    <div style="border: 3px solid #00E676; background-color: rgba(0, 230, 118, 0.14);
                                border-radius: 10px; padding: 12px; margin-bottom: 12px;">
                        <span style="background-color: #00E676; color: #000; font-weight: bold;
                                     padding: 2px 8px; border-radius: 5px; font-size: 11px;">
                            ● ACTIVE PAYMENT NOW
                        </span>
                        <h4 style="margin: 6px 0 2px 0;">{uname}</h4>
                        <p style="margin: 0; font-size: 13px;"><b>Balance:</b> ₹{acc['balance']:,.2f}</p>
                        <p style="margin: 2px 0 0 0; font-size: 12px;"><b>Activity:</b> {acc['last_action_summary']}</p>
                        <p style="margin: 2px 0 0 0; font-size: 12px;"><b>Failed Tries:</b> {acc['failed_attempts']}/5</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                # Dimmed compact card for idle users
                status_badge = "🚨 LOCKED (7D)" if is_locked else "IDLE"
                border_col = "#FF5252" if is_locked else "#444444"
                st.markdown(
                    f"""
                    <div style="border: 1px solid {border_col}; opacity: 0.72;
                                border-radius: 10px; padding: 10px; margin-bottom: 12px;">
                        <span style="font-size: 11px; color: #AAAAAA; font-weight: bold;">
                            ○ {status_badge}
                        </span>
                        <h5 style="margin: 4px 0 2px 0;">{uname}</h5>
                        <p style="margin: 0; font-size: 12px;">Balance: ₹{acc['balance']:,.2f}</p>
                        <p style="margin: 2px 0 0 0; font-size: 11px; color: #AAAAAA;">Last: {acc['last_action_summary']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# Route to the selected website
if current_site == "hacker":
    render_payment_portal("Hacker")
elif current_site == "bank":
    render_bank_soc()
else:
    render_payment_portal("Legitimate User")
