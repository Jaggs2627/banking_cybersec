import streamlit as st
from datetime import datetime, timedelta

# ---------------------------------------------------------
# SHARED GLOBAL STATE (Connects all sites in real time)
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
                "is_active_now": False,
                "active_actor": None,
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
                "is_active_now": False,
                "active_actor": None,
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
                "active_actor": None,
                "credentials_leaked": False,
                "leak_reason": ""
            }
        },
        "pending_approvals": [],
        "logs": []
    }

state = get_shared_bank_state()

# Read URL parameter (?site=victim or ?site=hacker)
current_site = st.query_params.get("site", "victim").lower()

st.set_page_config(
    page_title="SecurePay | Hacker Terminal" if current_site == "hacker" else "SecurePay | Personal Banking",
    page_icon="🕵️" if current_site == "hacker" else "🏦",
    layout="centered"
)

# Helper: Check if account is locked
def check_lock_status(acc):
    if acc["locked_until"] is not None:
        if datetime.now() < acc["locked_until"]:
            return True, acc["locked_until"] - datetime.now()
        else:
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

# Shared Payment Gateway UI used by both Victim and Hacker
def render_payment_portal(actor_role):
    is_hacker = (actor_role == "Hacker")

    if is_hacker:
        st.title("🕵️ Adversary Attack Terminal")
        st.caption("Website 2 of 3 — External Attacker Spoofing Customer Payment Gateway")
        selected_user = st.selectbox("🎯 Select Target Victim Account", list(state["accounts"].keys()))
    else:
        st.title("📱 SecurePay Personal Banking")
        st.caption("Website 1 of 3 — Legitimate Customer Payment Portal")
        selected_user = st.selectbox("Select Your Account", list(state["accounts"].keys()))

    account = state["accounts"][selected_user]

    # Highlight currently active user on the network
    for u in state["accounts"]:
        state["accounts"][u]["is_active_now"] = (u == selected_user)
        if u == selected_user:
            state["accounts"][u]["active_actor"] = actor_role

    # Hacker-only Phishing Intercept Box
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
                "You have no stolen PIN/Password. Attempting brute-force guesses will trigger the bank's 5-attempt 7-day lockout."
            )

    # Account Status Metrics
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
            f"🚨 **ACCOUNT LOCKED FOR 7 DAYS** due to 5 failed security attempts.\n\n"
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
                    biometric_verified = st.checkbox("🧬 Attempt Biometric Spoof (Fails without victim's physical finger/device)")
                else:
                    biometric_verified = st.checkbox("👆 Tap to Scan Fingerprint / Face ID (Simulated Biometric)")
            elif auth_method.startswith("2."):
                entered_cvv = st.text_input("Enter 3-Digit Security Number (Back of Debit Card)", type="password", max_chars=3)
            elif auth_method.startswith("3."):
                entered_password = st.text_input("Enter Banking Password", type="password")

            btn_label = "⚡ Execute Unauthorized Transfer" if is_hacker else "Authorize & Send Money"
            submit_payment = st.form_submit_button(btn_label, use_container_width=True)

            if submit_payment:
                if amount > account["balance"]:
                    st.warning("Insufficient balance for this transaction.")
                else:
                    auth_passed = False
                    if auth_method.startswith("1."):
                        # Hacker cannot spoof hardware biometric remotely
                        auth_passed = (not is_hacker) and (entered_pin == account["pin"]) and biometric_verified
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
                            "actor": actor_role,
                            "recipient": recipient,
                            "amount": amount,
                            "method": auth_method,
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "status": "Pending Bank Permission"
                        })
                        add_log(selected_user, actor_role, auth_method, amount, "PENDING APPROVAL", f"Transfer to {recipient}")
                        st.success(f"✅ MFA Bypassed/Passed! Request **{tx_id}** queued at Bank SOC for final permission.")
                    else:
                        account["failed_attempts"] += 1
                        remaining_tries = 5 - account["failed_attempts"]
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

# Route to Website 1 or Website 2
if current_site == "hacker":
    render_payment_portal("Hacker")
else:
    render_payment_portal("Legitimate User")
