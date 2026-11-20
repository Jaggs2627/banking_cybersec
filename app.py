import streamlit as st
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="SecurePay | Personal Banking Portal",
    page_icon="🏦",
    layout="centered"
)

# ---------------------------------------------------------
# SHARED GLOBAL STATE (Connects all views in real time)
# ---------------------------------------------------------
@st.cache_resource
def get_shared_bank_state():
    return {
        "accounts": {
            "Siddhant Shithole (ACC-101)": {
                "balance": 50000.0,
                "pin": "1234",
                "cvv": "842",
                "password": "Siddant123",
                "biometric_token": "BIO-SIDDHANT-OK",
                "failed_attempts": 0,
                "locked_until": None,
                "is_active_now": False,
                "credentials_leaked": False,
                "leak_reason": ""
            },
            "Prithviraj Chavan (ACC-102)": {
                "balance": 75000.0,
                "pin": "4321",
                "cvv": "319",
                "password": "Pr1thv1r@j123",
                "biometric_token": "BIO-PRITHIVIRAJ-OK",
                "failed_attempts": 0,
                "locked_until": None,
                "is_active_now": False,
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
                "is_active_now": False,
                "credentials_leaked": False,
                "leak_reason": ""
            }
        },
        "pending_approvals": [],
        "logs": []
    }

state = get_shared_bank_state()

# Helper: Check if account is locked
def check_lock_status(acc):
    if acc["locked_until"] is not None:
        if datetime.now() < acc["locked_until"]:
            return True, acc["locked_until"] - datetime.now()
        else:
            # 7-day lockout expired
            acc["locked_until"] = None
            acc["failed_attempts"] = 0
    return False, None

# Helper: Record log entry
def add_log(user, actor, method, amount, status, details):
    state["logs"].insert(0, {
        "time": datetime.now().strftime("%H:%M:%S"),
        "user": user,
        "actor": actor,
        "method": method,
        "amount": f"₹{amount:,.2f}",
        "status": status,
        "details": details
    })

# ---------------------------------------------------------
# WEBSITE 1: VICTIM / LEGITIMATE USER BANKING APP
# ---------------------------------------------------------
st.title("📱 SecurePay Personal Banking")
st.caption("Website 1 of 3 — Legitimate Customer Payment Portal")

# Select which user is using the phone
selected_user = st.selectbox("Select Your Account", list(state["accounts"].keys()))
account = state["accounts"][selected_user]

# Mark user as currently active on the network (for Master View highlight later)
for u in state["accounts"]:
    state["accounts"][u]["is_active_now"] = (u == selected_user)

# Display Account Summary Card
col1, col2 = st.columns(2)
col1.metric("Available Balance", f"₹{account['balance']:,.2f}")
col2.metric("Failed Security Attempts", f"{account['failed_attempts']} / 5")

is_locked, remaining_time = check_lock_status(account)

if is_locked:
    days = remaining_time.days
    hours, rem = divmod(remaining_time.seconds, 3600)
    minutes, _ = divmod(rem, 60)
    st.error(
        f"🚨 **ACCOUNT LOCKED FOR 7 DAYS** due to 5 failed security attempts.\n\n"
        f"Time remaining: **{days} days, {hours} hours, {minutes} minutes**."
    )
else:
    st.divider()
    st.subheader("💸 Make a Payment")

    recipient = st.text_input("Recipient UPI / Account ID", value="merchant.store@upi")
    amount = st.number_input("Amount (₹)", min_value=100.0, max_value=100000.0, value=2500.0, step=500.0)

    auth_method = st.radio(
        "Choose Multi-Factor Authentication (MFA) Method:",
        [
            "1. PIN + Biometric Verification",
            "2. PIN + Debit Card Security Code (CVV)",
            "3. PIN + Account Password"
        ]
    )

    with st.form("victim_payment_form"):
        entered_pin = st.text_input("Enter 4-Digit ATM/UPI PIN", type="password", max_chars=4)

        biometric_verified = False
        entered_cvv = ""
        entered_password = ""

        if auth_method.startswith("1."):
            biometric_verified = st.checkbox("👆 Tap to Scan Fingerprint / Face ID (Simulated Biometric)")
        elif auth_method.startswith("2."):
            entered_cvv = st.text_input("Enter 3-Digit Security Number (Back of Debit Card)", type="password", max_chars=3)
        elif auth_method.startswith("3."):
            entered_password = st.text_input("Enter Banking Password", type="password")

        submit_payment = st.form_submit_button("Authorize & Send Money", use_container_width=True)

        if submit_payment:
            if amount > account["balance"]:
                st.warning("Insufficient balance for this transaction.")
            else:
                # Validate chosen MFA method
                auth_passed = False
                if auth_method.startswith("1."):
                    auth_passed = (entered_pin == account["pin"]) and biometric_verified
                elif auth_method.startswith("2."):
                    auth_passed = (entered_pin == account["pin"]) and (entered_cvv == account["cvv"])
                elif auth_method.startswith("3."):
                    auth_passed = (entered_pin == account["pin"]) and (entered_password == account["password"])

                if auth_passed:
                    account["failed_attempts"] = 0
                    tx_id = f"TXN-{1000 + len(state['logs']) + 1}"
                    state["pending_approvals"].append({
                        "tx_id": tx_id,
                        "user": selected_user,
                        "actor": "Legitimate User",
                        "recipient": recipient,
                        "amount": amount,
                        "method": auth_method,
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "status": "Pending Bank Permission"
                    })
                    add_log(selected_user, "Legitimate User", auth_method, amount, "PENDING APPROVAL", f"Sent to {recipient}")
                    st.success(f"✅ Authentication Passed! Transaction **{tx_id}** sent to Bank SOC for final permission.")
                else:
                    account["failed_attempts"] += 1
                    remaining_tries = 5 - account["failed_attempts"]
                    if account["failed_attempts"] >= 5:
                        account["locked_until"] = datetime.now() + timedelta(days=7)
                        add_log(selected_user, "Legitimate User", auth_method, amount, "LOCKED (7 DAYS)", "5 consecutive failed attempts")
                        st.error("🚨 5 incorrect attempts reached! Account has been locked for 7 days.")
                        st.rerun()
                    else:
                        add_log(selected_user, "Legitimate User", auth_method, amount, "FAILED AUTH", f"{remaining_tries} attempts left")
                        st.error(f"❌ Authentication Failed! Only **{remaining_tries}** attempts remaining before a 7-day lockout.")

    # ---------------------------------------------------------
    # HUMAN ERROR SIMULATION (How the Hacker Gets Credentials)
    # ---------------------------------------------------------
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

