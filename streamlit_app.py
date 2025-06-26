import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="ÁFA Elévülés Kalkulátor", layout="centered")

st.image("nav_logo.png", width=150)
st.title("📆 ÁFA Ellenőrzési Elévülés Kalkulátor")
st.markdown("Segít meghatározni, hogy egy adott időszak **elévült-e**, figyelembe véve az ellenőrzés joghatásait.")

closure_date = st.date_input("🗓️ Vizsgálat várható lezárásának dátuma")
frequency = st.selectbox("📊 ÁFA bevallás gyakorisága", ["havi", "negyedéves", "éves"])

new_procedure = st.checkbox("🔁 Volt új eljárás (másodfok, bírósági stb.)?")
late_filing = st.checkbox("🐌 Történt késedelmes bevallás?")
self_revision = st.checkbox("✏️ Volt önellenőrzés?")
self_revision_favor = False
if self_revision:
    self_revision_favor = st.checkbox("📉 Az önellenőrzés az adózó **javára** szólt?")
litigation = st.checkbox("⚖️ Volt peres vagy más nyugvást okozó eljárás?")

def get_latest_non_expired_period(closure_date, frequency, new_procedure, late_filing, self_revision, self_revision_favor, litigation):
    base_year = closure_date.year
    expiry_date = datetime(base_year - 4, 12, 31)

    if new_procedure:
        expiry_date += timedelta(days=365)
    if late_filing:
        expiry_date += timedelta(days=183)
    if self_revision and self_revision_favor:
        expiry_date = closure_date + timedelta(days=5*365)
    if litigation:
        expiry_date += timedelta(days=730)

    if closure_date > expiry_date:
        last_expired_year = expiry_date.year
    else:
        last_expired_year = expiry_date.year - 1

    if frequency == "havi":
        last_month = 12
        last_year = last_expired_year
    elif frequency == "negyedéves":
        last_month = 10
        last_year = last_expired_year
    elif frequency == "éves":
        last_month = 12
        last_year = last_expired_year - 1
    else:
        raise ValueError("Ismeretlen gyakoriság!")

    return last_year, last_month

if st.button("📐 Számítás indítása"):
    year, month = get_latest_non_expired_period(
        closure_date, frequency, new_procedure, late_filing, self_revision, self_revision_favor, litigation
    )
    st.success(f"✅ Utolsó teljesen **elévült időszak**: {year}. {month:02d}")
    next_month = (month % 12) + 1
    next_year = year + 1 if next_month == 1 else year
    st.info(f"📌 Vizsgálható időszak: {next_year}. {next_month:02d} hónaptól kezdődően.")
