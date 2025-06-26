import streamlit as st
from datetime import date, timedelta

st.set_page_config(page_title="ÁFA Elévülés Kalkulátor", layout="centered")

# Logo eltávolítva, ha szükséges: # st.image("nav_logo.png", width=150)

st.title("📆 ÁFA Ellenőrzési Elévülés Kalkulátor")
st.markdown("Ez az eszköz segít meghatározni, hogy mely ÁFA időszakok **még nem évültek el** az Art. 164. § alapján.")

closure_date = st.date_input("🗓️ Vizsgálat várható lezárásának dátuma", value=date.today())
frequency = st.selectbox("📊 ÁFA bevallás gyakorisága", ["havi", "negyedéves", "éves"])
new_procedure = st.checkbox("🔁 Volt új eljárás (pl. másodfok, új eljárás)?")
late_filing = st.checkbox("🐌 Történt késedelmes bevallás?")
litigation = st.checkbox("⚖️ Volt peres vagy más nyugvást okozó eljárás?")

def filing_deadline(year, period_month, frequency):
    if frequency == "havi":
        if period_month < 12:
            return date(year, period_month + 1, 20)
        else:
            return date(year + 1, 1, 20)
    elif frequency == "negyedéves":
        if period_month == 3:
            return date(year, 4, 20)
        elif period_month == 6:
            return date(year, 7, 20)
        elif period_month == 9:
            return date(year, 10, 20)
        elif period_month == 12:
            return date(year + 1, 1, 20)
    elif frequency == "éves":
        return date(year + 1, 2, 25)
    else:
        raise ValueError("Ismeretlen gyakoriság!")

def calculate_expiry(filing_deadline, new_proc, late_filing, litigation):
    expiry = date(filing_deadline.year, 12, 31) + timedelta(days=5*365)
    if late_filing:
        expiry += timedelta(days=183)
    if new_proc:
        expiry += timedelta(days=365)
    if litigation:
        expiry += timedelta(days=730)
    return expiry

def get_first_non_expired_period(closure_date, frequency, new_proc, late_filing, litigation):
    today = closure_date
    earliest = None

    for year in range(2000, today.year + 1):
        if frequency == "havi":
            periods = range(1, 13)
        elif frequency == "negyedéves":
            periods = [3, 6, 9, 12]
        elif frequency == "éves":
            periods = [12]
        else:
            raise ValueError("Ismeretlen gyakoriság!")

        for pm in periods:
            fd = filing_deadline(year, pm, frequency)
            expiry = calculate_expiry(fd, new_proc, late_filing, litigation)
            if expiry >= today:
                if earliest is None or (year, pm) < earliest:
                    earliest = (year, pm)

    return earliest

if st.button("📐 Számítás indítása"):
    result = get_first_non_expired_period(closure_date, frequency, new_procedure, late_filing, litigation)

    if result:
        year, month = result
        st.success(f"✅ Legkorábbi vizsgálható időszak: {year}. {month:02d} hónap")
    else:
        st.error("❌ Nem található vizsgálható időszak a megadott feltételekkel.")
