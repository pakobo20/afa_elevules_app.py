import streamlit as st
from datetime import date, timedelta

st.set_page_config(page_title="ÁFA Elévülés Kalkulátor", layout="centered")

st.title("📆 ÁFA Ellenőrzési Elévülés Kalkulátor")
st.markdown("Ez az eszköz pontosan számolja az első **nem elévült** ÁFA időszakot.")

closure_date = st.date_input("🗓️ Vizsgálat várható lezárásának dátuma", value=date.today())
frequency = st.selectbox("📊 ÁFA bevallás gyakorisága", ["havi", "negyedéves", "éves"])
new_procedure = st.checkbox("🔁 Volt új eljárás?")
late_filing = st.checkbox("🐌 Késedelmes bevallás?")
litigation = st.checkbox("⚖️ Volt peres eljárás?")

def filing_deadline(year, pm, freq):
    if freq == "havi":
        nxt_month = pm + 1
        nxt_year = year
        if nxt_month == 13:
            nxt_month = 1
            nxt_year += 1
        return date(nxt_year, nxt_month, 20)
    if freq == "negyedéves":
        if pm not in [3,6,9,12]:
            raise ValueError("Negyedéves hónap csak 3,6,9,12 lehet")
        nxt_month = pm + 1
        nxt_year = year
        if nxt_month == 13:
            nxt_month = 1
            nxt_year += 1
        return date(nxt_year, nxt_month, 20)
    if freq == "éves":
        return date(year + 1, 2, 25)
    raise ValueError("Ismeretlen gyakoriság")

def expiry_date(filing_dl, new_proc, late_filing, litigation):
    base = date(filing_dl.year, 12, 31) + timedelta(days=5*365)
    if late_filing:
        base += timedelta(days=183)
    if new_proc:
        base += timedelta(days=365)
    if litigation:
        base += timedelta(days=730)
    return base

def find_first_non_expired(closure_date, freq, new_proc, late_filing, litigation):
    today = closure_date
    earliest = None

    start_year = today.year - 7  # elegendő korábbi évre hátra
    for year in range(start_year, today.year + 1):
        periods = (
            range(1,13) if freq=="havi" else
            [3,6,9,12] if freq=="negyedéves" else
            [12]
        )
        for pm in periods:
            dl = filing_deadline(year, pm, freq)
            exp = expiry_date(dl, new_proc, late_filing, litigation)
            if exp >= today:
                if earliest is None or (year, pm) < earliest:
                    earliest = (year, pm)

    return earliest

if st.button("📐 Számítás indítása"):
    result = find_first_non_expired(closure_date, frequency, new_procedure, late_filing, litigation)
    if result:
        year, pm = result
        if frequency == "negyedéves":
            start_month = pm - 2
        elif frequency == "éves":
            start_month = 1
        else:
            start_month = pm

        st.success(f"✅ Legkorábbi vizsgálható időszak: {year}. {start_month:02d} hónap")
    else:
        st.error("❌ Nincs vizsgálható időszak a megadott feltételekkel.")
