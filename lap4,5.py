import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from vnstock import Vnstock
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

SCHEMA = "dbo"
TABLE = "FPT_Stock"
FQTN = f"{SCHEMA}.{TABLE}"  # fully-qualified table name

# ========= KẾT NỐI =========
def get_engine():
    DRIVER = "ODBC Driver 17 for SQL Server"
    conn = (
        f"DRIVER={{{DRIVER}}};"
        r"SERVER=localhost\SQLEXPRESS;"
        "DATABASE=FPT_StockDB;"
        "Trusted_Connection=yes;"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )
    return create_engine(
        f"mssql+pyodbc:///?odbc_connect={quote_plus(conn)}",
        fast_executemany=True
    )

# Tạo bảng nếu chưa có (đúng schema dbo)
def ensure_table(engine):
    sql = f"""
    IF OBJECT_ID('{FQTN}','U') IS NULL
    BEGIN
        CREATE TABLE {FQTN}(
            [date]   DATE   NOT NULL,
            [open]   FLOAT  NULL,
            [high]   FLOAT  NULL,
            [low]    FLOAT  NULL,
            [close]  FLOAT  NULL,
            [volume] BIGINT NULL,
            CONSTRAINT PK_FPT_Stock PRIMARY KEY CLUSTERED([date])
        );
    END
    """
    with engine.begin() as con:
        con.execute(text(sql))

# ========= LẤY DỮ LIỆU =========
def get_stock_data_range(symbol, start, end):
    f = Vnstock().stock(symbol=symbol, source="VCI")
    df = f.quote.history(start=start, end=end)  # DataFrame daily
    if df is None or df.empty:
        return pd.DataFrame()
    date_col = "time" if "time" in df.columns else "date"
    df = (df.rename(columns={date_col: "date"})
            .assign(date=lambda x: pd.to_datetime(x["date"]))
            .sort_values("date")
            .reset_index(drop=True))
    keep = [c for c in ["date", "open", "high", "low", "close", "volume"] if c in df.columns]
    return df[keep]

# ========= DB HELPERS =========
def get_max_date_in_db(engine):
    try:
        with engine.connect() as conn:
            max_d = conn.execute(text(f"SELECT MAX([date]) FROM {FQTN}")).scalar()
        return pd.to_datetime(max_d) if max_d else None
    except Exception:
        return None

def replace_overlap_and_append(engine, df_new, cutoff_date=None):
    if df_new.empty:
        return 0
    ensure_table(engine)
    with engine.begin() as conn:
        if cutoff_date is not None:
            conn.execute(text(f"DELETE FROM {FQTN} WHERE [date] >= :d"), {"d": cutoff_date})
    # Ghi vào đúng schema dbo
    df_new.to_sql(TABLE, con=engine, schema=SCHEMA, if_exists="append", index=False)
    return len(df_new)

def create_or_replace_view(engine):
    sql = f"""
    IF OBJECT_ID('{SCHEMA}.vFPT_Analysis','V') IS NOT NULL
        DROP VIEW {SCHEMA}.vFPT_Analysis;
    CREATE VIEW {SCHEMA}.vFPT_Analysis AS
    SELECT
        [date],[open],[high],[low],[close],[volume],
        LAG([close]) OVER (ORDER BY [date]) AS PrevClose,
        ROUND([close] - LAG([close]) OVER (ORDER BY [date]), 2) AS PriceChange,
        ROUND( ([close] - LAG([close]) OVER (ORDER BY [date]))
              / NULLIF(LAG([close]) OVER (ORDER BY [date]), 0) * 100, 2) AS PercentChange
    FROM {FQTN};
    """
    with engine.begin() as con:
        for stmt in [s.strip() for s in sql.split(";") if s.strip()]:
            con.execute(text(stmt))

# ========= HIỂN THỊ =========
def display_latest_from_db(engine):
    q = f"SELECT TOP 2 * FROM {FQTN} ORDER BY [date] DESC"
    df = pd.read_sql(q, con=engine)
    if df.empty:
        print("❌ Chưa có dữ liệu trong DB."); return
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else None

    current = latest["close"]
    if prev is not None:
        price_change = current - prev["close"]
        percent_change = price_change / prev["close"] * 100
    else:
        price_change = 0; percent_change = 0.0

    print("🚀 PHÂN TÍCH CỔ PHIẾU FPT (ngày gần nhất)")
    print("=" * 56)
    print(f"📅 Ngày:        {latest['date'].strftime('%d/%m/%Y')}")
    print(f"📊 Đóng cửa:    {current:,.0f} VND")
    print(f"📈 Thay đổi:    {price_change:+,.0f} VND ({percent_change:+.2f}%)")
    print(f"🔼 Cao nhất:    {latest['high']:,.0f} | 🔽 Thấp nhất: {latest['low']:,.0f}")
    print(f"📦 Khối lượng:  {latest['volume']:,.0f}")
    print("=" * 56)

def visualize_stock_data(df):
    if df is None or df.empty:
        print("❌ Không có dữ liệu để vẽ."); return

    recent = df.tail(180)  # ~6 tháng
    # Close
    plt.figure(figsize=(10,5))
    plt.plot(recent["date"], recent["close"], label="Close")
    plt.title("FPT – Giá đóng cửa (6 tháng gần nhất)")
    plt.xlabel("Ngày"); plt.ylabel("VND"); plt.legend(); plt.tight_layout()
    plt.show()

    # Volume
    plt.figure(figsize=(10,4))
    plt.bar(recent["date"], recent["volume"])
    plt.title("FPT – Khối lượng giao dịch (6 tháng gần nhất)")
    plt.xlabel("Ngày"); plt.ylabel("Cổ phiếu"); plt.tight_layout()
    plt.show()

    # Open vs Close
    plt.figure(figsize=(10,5))
    plt.plot(recent["date"], recent["open"], linestyle="--", label="Open")
    plt.plot(recent["date"], recent["close"], label="Close")
    plt.title("FPT – So sánh Open/Close (6 tháng gần nhất)")
    plt.xlabel("Ngày"); plt.ylabel("VND"); plt.legend(); plt.tight_layout()
    plt.show()

# ========= MAIN =========
if __name__ == "__main__":
    symbol = "FPT"
    eng = get_engine()
    ensure_table(eng)

    today = datetime.today().strftime("%Y-%m-%d")
    last_date = get_max_date_in_db(eng)

    if last_date is None:
        start = (datetime.today() - timedelta(days=1825)).strftime("%Y-%m-%d")
        print(f"⏳ Khởi tạo: tải {symbol} từ {start} đến {today}")
        df_full = get_stock_data_range(symbol, start, today)
        if df_full.empty:
            print("❌ Không có dữ liệu từ API.")
        else:
            # replace lần đầu và luôn vào dbo
            df_full.to_sql(TABLE, con=eng, schema=SCHEMA, if_exists="replace", index=False)
            print(f"✅ Khởi tạo bảng với {len(df_full):,} dòng.")
            recent_for_plot = df_full
    else:
        overlap_days = 5
        start = (last_date - timedelta(days=overlap_days)).strftime("%Y-%m-%d")
        print(f"🔄 Cập nhật: tải từ {start} đến {today} (xoá chồng lấn từ {start})")
        df_inc = get_stock_data_range(symbol, start, today)
        if df_inc.empty:
            print("ℹ️ Không có dữ liệu mới.")
            recent_for_plot = pd.read_sql(
                f"SELECT TOP 180 * FROM {FQTN} ORDER BY [date] DESC", con=eng
            ).sort_values("date")
        else:
            n = replace_overlap_and_append(eng, df_inc, cutoff_date=start)
            print(f"✅ Cập nhật {n:,} dòng (đã ghi đè phần chồng lấn).")
            recent_for_plot = df_inc

    create_or_replace_view(eng)
    display_latest_from_db(eng)
    visualize_stock_data(recent_for_plot)

