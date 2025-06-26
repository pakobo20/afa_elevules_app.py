import streamlit as st
from datetime import date, timedelta, datetime

st.set_page_config(page_title="ÁFA Elévülés Kalkulátor", layout="centered")

st.title("📆 ÁFA Ellenőrzési Elévülés Kalkulátor")
st.markdown("Segít meghatározni, hogy egy adott időszak **elévült-e**, figyelembe véve az ellenőrzés joghatásait (önellenőrzés kizárva).")

closure_date = st.date_input("🗓️ Vizsgálat várható lezárásának dátuma")
frequency = st.selectbox("📊 ÁFA bevallás gyakorisága", ["havi", "negyedéves", "éves"])
new_procedure = st.checkbox("🔁 Volt új eljárás (másodfok, bírósági stb.)?")
late_filing = st.checkbox("🐌 Történt késedelmes bevallás?")
litigation = st.checkbox("⚖️ Volt peres vagy más nyugvást okozó eljárás?")

# Funkció a bevallás határidejének meghatározására
def get_filing_deadline(year, period_month, frequency):
    if frequency == "havi":
        return date(year, period_month, 20)
    elif frequency == "negyedéves":
        # negyedév zárása utáni 20. nap
        quarter_end_month = period_month
        return date(year, quarter_end_month, 20)
    elif frequency == "éves":
        # éves bevallás követő év február 25.
        return date(year + 1, 2, 25)
    else:
        raise ValueError("Ismeretlen gyakoriság")

# Funkció az elévülési dátum meghatározására
def calculate_expiry(filing_deadline, new_procedure, late_filing, litigation):
    expiry = date(filing_deadline.year, 12, 31) + timedelta(days=5*365)

    if new_procedure:
        expiry += timedelta(days=365)
    if late_filing:
        expiry += timedelta(days=183)
    if litigation:
        expiry += timedelta(days=730)

    return expiry

# Megkeressük a legkorábbi NEM évült időszakot
def get_first_non_expired_period(closure_date, frequency, new_procedure, late_filing, litigation):
    today = closure_date
    if frequency == "havi":
        for year in reversed(range(2000, today.year + 1)):
            for month in reversed(range(1, 13)):
                try:
                    filing_deadline = get_filing_deadline(year, month, frequency)
                    expiry_date = calculate_expiry(filing_deadline, new_procedure, late_filing, litigation)
                    if expiry_date >= today:
                        earliest_year = year
                        earliest_month = month
                    else:
                        return earliest_year, earliest_month
                except:
                    continue
    elif frequency == "negyedéves":
        for year in reversed(range(2000, today.year + 1)):
            for month in reversed([3, 6, 9, 12]):
                try:
                    filing_deadline = get_filing_deadline(year, month, frequency)
                    expiry_date = calculate_expiry(filing_deadline, new_procedure, late_filing, litigation)
                    if expiry_date >= today:
                        earliest_year = year
                        earliest_month = month - 2  # kezdő hónap
                    else:
                        return earliest_year, earliest_month
                except:
                    continue
    elif frequency == "éves":
        for year in reversed(range(2000, today.year + 1)):
            try:
                filing_deadline = get_filing_deadline(year, None, frequency)
                expiry_date = calculate_expiry(filing_deadline, new_procedure, late_filing, litigation)
                if expiry_date >= today:
                    earliest_year = year
                else:
                    return earliest_year, 1  # egész év
            except:
                continue
    return earliest_year, earliest_month if frequency != "éves" else 1

if st.button("📐 Számítás indítása"):
    year, month = get_first_non_expired_period(
        closure_date, frequency, new_procedure, late_filing, litigation
    )
    st.success(f"✅ Vizsgálható legkorábbi időszak: {year}. {month:02d}")
