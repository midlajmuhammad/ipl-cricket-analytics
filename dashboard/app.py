from pathlib import Path
import sqlite3
import math
import json

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# IPL BOWLING EXPLORER with batting + bowling over animation
# ============================================================
st.set_page_config(page_title="IPL Bowling Explorer", page_icon="🏏", layout="wide")

st.markdown(r"""
<style>
:root{--lime:#b8ff3b;--cyan:#39e6ff;--ink:#071018;--panel:#101d29;--muted:#9bb0c1}
.stApp{background:radial-gradient(ellipse at 10% 0%,#173d36 0,transparent 32%),radial-gradient(ellipse at 100% 15%,#172c4b 0,transparent 35%),linear-gradient(145deg,#070d14,#0b1722 65%,#101b25);color:#f3f7fb}
[data-testid="stHeader"]{background:transparent}.block-container{max-width:1500px;padding-top:1.4rem;padding-bottom:3rem}
h1,h2,h3{color:#f3f7fb!important}
@keyframes aurora{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulse{0%,100%{opacity:.55;box-shadow:0 0 5px var(--lime)}50%{opacity:1;box-shadow:0 0 16px var(--lime)}}
@keyframes shimmer{0%{background-position:180% 0}100%{background-position:-180% 0}}
@keyframes ticker{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@keyframes ball{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-13px) rotate(180deg)}}
.control-hero{position:relative;overflow:hidden;padding:30px;border-radius:24px;border:1px solid #b8ff3b44;background:linear-gradient(120deg,#142d2c,#132b3b,#282043,#142d2c);background-size:300% 300%;animation:aurora 14s ease infinite;box-shadow:0 15px 45px #0005}
.control-hero:after{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(105deg,transparent 25%,#ffffff0b 50%,transparent 70%);background-size:220% 100%;animation:shimmer 8s linear infinite}
.hero-kicker{font-size:11px;letter-spacing:3px;font-weight:900;color:var(--lime)}.hero-title{font-size:clamp(28px,4vw,46px);font-weight:900;letter-spacing:-1.4px;margin:10px 0}.hero-copy{color:#bdd0dc;font-size:15px}.hero-ball{font-size:56px;display:inline-block;animation:ball 2.8s ease-in-out infinite;filter:drop-shadow(0 0 15px #b8ff3b55)}
.live-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--lime);margin-right:8px;animation:pulse 1.4s infinite}
.ticker{overflow:hidden;white-space:nowrap;padding:13px 0;margin:18px 0 24px;border-block:1px solid #b8ff3b30;color:#c7d8e2;font-size:11px;font-weight:800;letter-spacing:2px}.ticker-inner{display:inline-block;min-width:max-content;animation:ticker 32s linear infinite}.ticker:hover .ticker-inner{animation-play-state:paused}.ticker span{margin-right:45px}
div[data-testid="stMetric"]{background:linear-gradient(145deg,#142634,#0d1923);border:1px solid #37505e88;border-radius:17px;padding:17px;animation:rise .6s ease both;transition:transform .25s,border-color .25s,box-shadow .25s;position:relative;overflow:hidden}
div[data-testid="stMetric"]:after{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(110deg,transparent 30%,#ffffff0c 50%,transparent 70%);background-size:220% 100%;animation:shimmer 7s linear infinite}
div[data-testid="stMetric"]:hover{transform:translateY(-4px);border-color:var(--lime);box-shadow:0 10px 28px #b8ff3b13}div[data-testid="stMetricLabel"]{color:#a8bdca!important}div[data-testid="stMetricValue"]{color:var(--lime)!important;font-weight:900}
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:7px;background:#0a151f;padding:7px;border:1px solid #29404d;border-radius:14px}[data-testid="stTabs"] [data-baseweb="tab"]{border-radius:9px;font-weight:800;transition:background .2s}[data-testid="stTabs"] [data-baseweb="tab"]:hover{background:#203440}[data-testid="stTabs"] [aria-selected="true"]{background:#1a3432;color:var(--lime)!important}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#09141d,#101f2a);border-right:1px solid #29404d}
div[data-testid="stPlotlyChart"]{background:linear-gradient(145deg,#101e29,#0b1721);border:1px solid #31475688;border-radius:16px;padding:5px;animation:rise .65s ease both;transition:transform .2s,border-color .2s}div[data-testid="stPlotlyChart"]:hover{transform:translateY(-2px);border-color:#b8ff3b88}
.stButton>button{border:0;border-radius:10px;font-weight:800;background:linear-gradient(100deg,#b8ff3b,#39e6ff);color:#071018}.stButton>button:hover{box-shadow:0 0 20px #b8ff3b33;color:#071018}
div[data-testid="stExpander"]{border:1px solid #29404d;border-radius:13px;background:#0e1b26}
hr{border-color:#29404d}[data-testid="stCaptionContainer"]{color:#9bb0c1}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🧪 Control Room")
    accent = st.selectbox("Interface skin", ["Lime Circuit", "Ocean Pulse", "Violet Night", "Ember League"])
    motion = st.selectbox("Motion mode", ["Full motion", "Reduced motion"])
    st.markdown("---")
    st.caption("IPL Bowling Explorer • Local database mode")

skin = {
    "Lime Circuit": ("#b8ff3b", "#39e6ff"),
    "Ocean Pulse": ("#43d9ff", "#83ffe1"),
    "Violet Night": ("#c5a3ff", "#ff7be5"),
    "Ember League": ("#ffb45c", "#ff6b73"),
}[accent]
if motion == "Reduced motion":
    st.markdown("<style>*,*::before,*::after{animation:none!important;transition:none!important}</style>", unsafe_allow_html=True)
st.markdown(f"<style>:root{{--lime:{skin[0]};--cyan:{skin[1]}}}.hero-kicker{{color:{skin[0]}}}div[data-testid='stMetricValue']{{color:{skin[0]}!important}}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="control-hero"><div style="display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap;position:relative;z-index:1">
<div><div class="hero-kicker"><span class="live-dot"></span> IPL DATA • LIVE ANALYSIS MODE</div><div class="hero-title">Bowling Intelligence</div><div class="hero-copy">A control-room style for exploring wickets, economy, dot balls, season trends and animated overs.</div></div><div class="hero-ball">🏏</div></div></div>
<div class="ticker"><div class="ticker-inner"><span>◉ WICKET RADAR</span><span>◉ ECONOMY TRACKER</span><span>◉ SEASON MOMENTUM</span><span>◉ BOWLER COMPARISON</span><span>◉ OVER SIMULATOR</span><span>◉ WICKET RADAR</span><span>◉ ECONOMY TRACKER</span><span>◉ SEASON MOMENTUM</span><span>◉ BOWLER COMPARISON</span><span>◉ OVER SIMULATOR</span></div></div>
""", unsafe_allow_html=True)

# ---------- Find a database and a usable source table ----------
ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
DB_CANDIDATES = [
    ROOT / "ipl.db", ROOT / "data" / "raw" / "ipl.db",
    ROOT / "data" / "processed" / "ipl.db", ROOT / "notebooks" / "ipl.db",
    HERE / "ipl.db", HERE / "data" / "raw" / "ipl.db",
    Path.cwd() / "ipl.db", Path.cwd() / "data" / "raw" / "ipl.db",
]


def build_sqlite_from_csvs(target_path: Path) -> bool:
    table_dir = ROOT / "data" / "raw" / "tables"
    if not table_dir.exists():
        return False
    csv_files = sorted(table_dir.glob("*.csv"))
    if not csv_files:
        return False

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(target_path)) as con:
        for csv_path in csv_files:
            try:
                df = pd.read_csv(csv_path)
                table_name = csv_path.stem.strip().lower()
                df.to_sql(table_name, con, if_exists="replace", index=False)
            except Exception:
                continue
    return target_path.exists() and target_path.stat().st_size > 0


def find_source():
    seen = set()
    for path in DB_CANDIDATES:
        if str(path.resolve()) in seen or (path.exists() and path.stat().st_size == 0):
            continue
        seen.add(str(path.resolve()))
        try:
            with sqlite3.connect(str(path)) as con:
                objects = con.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view') ORDER BY name").fetchall()
                for (table,) in objects:
                    quoted = table.replace('"', '""')
                    cols = [r[1].lower().strip() for r in con.execute(f'PRAGMA table_info("{quoted}")')]
                    if any(c in cols for c in ("bowler", "bowler_name")):
                        return path, table, cols
        except sqlite3.Error:
            pass

    fallback_db = ROOT / "data" / "raw" / "ipl.db"
    if build_sqlite_from_csvs(fallback_db):
        try:
            with sqlite3.connect(str(fallback_db)) as con:
                objects = con.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view') ORDER BY name").fetchall()
                for (table,) in objects:
                    quoted = table.replace('"', '""')
                    cols = [r[1].lower().strip() for r in con.execute(f'PRAGMA table_info("{quoted}")')]
                    if any(c in cols for c in ("bowler", "bowler_name")):
                        return fallback_db, table, cols
        except sqlite3.Error:
            pass
    return None, None, []

DB_PATH, TABLE, TABLE_COLUMNS = find_source()
if DB_PATH is None:
    st.error("I couldn't find a SQLite table with a bowler column.")
    st.info("Place ipl.db in the project root, or in data/raw/ipl.db.")
    st.write("Checked database paths:")
    for p in dict.fromkeys(DB_CANDIDATES):
        st.code(str(p))
    st.stop()

@st.cache_data(show_spinner="Loading IPL delivery data...")
def read_table(db_path, table_name):
    safe = table_name.replace('"', '""')
    with sqlite3.connect(db_path) as con:
        return pd.read_sql_query(f'SELECT * FROM "{safe}"', con)

raw = read_table(str(DB_PATH), TABLE)
if raw.empty:
    st.error(f"Table '{TABLE}' exists but contains no rows.")
    st.stop()

# ---------- Column detection and normalization ----------
colmap = {str(c).lower().strip(): c for c in raw.columns}
def pick(*names):
    for n in names:
        if n in colmap:
            return colmap[n]
    return None

bowler_col = pick("bowler", "bowler_name")
runs_col = pick("total_runs", "total_run", "runs_conceded", "batter_runs", "runs")
if bowler_col is None or runs_col is None:
    st.error("This table doesn't have the columns needed for bowling analysis.")
    st.write("Detected table:", TABLE)
    st.write("Available columns:", list(raw.columns))
    st.stop()

def num(col, default=0):
    if col is None:
        return pd.Series(default, index=raw.index, dtype="float64")
    return pd.to_numeric(raw[col], errors="coerce").fillna(default)

def text_col(col, default="Unknown"):
    if col is None:
        return pd.Series(default, index=raw.index, dtype="string")
    return raw[col].astype("string").fillna(default).str.strip().replace("", default)

wide_col = pick("is_wide_ball", "is_wide", "wide")
noball_col = pick("is_no_ball", "is_noball", "no_ball")
legal_col = pick("is_legal", "legal_ball", "is_legal_ball")
wicket_col = pick("is_wicket", "wicket")
kind_col = pick("wicket_kind", "dismissal_kind", "kind")
season_col = pick("season_id", "season_year", "season")
phase_col = pick("phase", "innings_phase")
over_col = pick("over_number", "over", "over_id")
match_col = pick("match_id", "match_number")
team_col = pick("batting_team", "opponent")
venue_col = pick("venue", "venue_clean", "ground", "stadium")
style_col = pick("bowler_type", "bowling_style", "style")

wide = num(wide_col).clip(0, 1)
noball = num(noball_col).clip(0, 1)
legal = num(legal_col).clip(0, 1) if legal_col else (1 - wide - noball).clip(0, 1)
kind = text_col(kind_col)
wicket_flag = num(wicket_col).clip(0, 1)
not_credited = {"run out", "retired hurt", "retired out", "obstructing the field", "retired not out"}
phase_alias = {"power play": "Powerplay", "powerplay": "Powerplay", "middle overs": "Middle", "middle": "Middle", "death overs": "Death", "death": "Death"}
if phase_col:
    phase = text_col(phase_col).map(lambda x: phase_alias.get(str(x).lower(), str(x)))
else:
    over_values = num(over_col, -1)
    phase = pd.cut(over_values, bins=[-1, 5, 14, float("inf")], labels=["Powerplay", "Middle", "Death"]).astype("string").fillna("Unknown")

season = text_col(season_col) if season_col else pd.Series("Unknown", index=raw.index, dtype="string")
df = pd.DataFrame({
    "bowler": text_col(bowler_col), "runs": num(runs_col).clip(lower=0),
    "legal": legal, "wickets": ((wicket_flag == 1) & ~kind.str.lower().isin(not_credited)).astype(int),
    "dot": ((legal == 1) & (num(runs_col) == 0)).astype(int),
    "season": season, "phase": phase.astype("string").fillna("Unknown"),
    "style": text_col(style_col), "opponent": text_col(team_col), "venue": text_col(venue_col),
    "match": text_col(match_col) if match_col else pd.Series("Unknown", index=raw.index, dtype="string"),
    "kind": kind,
})
df = df[df["bowler"].notna() & ~df["bowler"].isin(["", "Unknown", "<NA>"])].copy()
if df.empty:
    st.error("No valid bowler rows were found after cleaning the source data.")
    st.stop()

# ---------- Global filters ----------
st.sidebar.markdown("### 🔎 Data filters")
seasons = sorted(df["season"].astype(str).unique().tolist())
styles = sorted(x for x in df["style"].astype(str).unique() if x.lower() != "unknown")
phases = ["Powerplay", "Middle", "Death"]
selected_seasons = st.sidebar.multiselect("Season", seasons, default=seasons)
selected_styles = st.sidebar.multiselect("Bowling style", styles, default=styles)
selected_phases = st.sidebar.multiselect("Innings phase", phases, default=phases)
minimum_balls = st.sidebar.select_slider("Minimum legal balls per bowler", options=[0, 12, 30, 60, 120, 300], value=30)

filtered = df[df["season"].astype(str).isin(selected_seasons)]
if selected_styles:
    filtered = filtered[filtered["style"].astype(str).isin(selected_styles) | (filtered["style"] == "Unknown")]
if selected_phases:
    filtered = filtered[filtered["phase"].isin(selected_phases) | ~filtered["phase"].isin(phases)]

if filtered.empty:
    st.warning("No rows match your filters. Select more seasons, styles or phases.")
    st.stop()

# ---------- Aggregations and chart styling ----------
def aggregate(data):
    out = data.groupby("bowler", as_index=False).agg(
        runs=("runs", "sum"), balls=("legal", "sum"), wickets=("wickets", "sum"), dots=("dot", "sum"),
        matches=("match", "nunique"),
    )
    out["economy"] = 6 * out["runs"] / out["balls"].where(out["balls"] > 0)
    out["dot_pct"] = 100 * out["dots"] / out["balls"].where(out["balls"] > 0)
    out["overs"] = out["balls"] / 6
    return out

stats = aggregate(filtered)
valid = stats[(stats["balls"] >= minimum_balls) & stats["economy"].notna()].copy()
COLORS = [skin[0], skin[1], "#ffb45c", "#c5a3ff", "#ff6b86", "#7cffb4"]

def style_fig(fig, height=420):
    fig.update_layout(
        height=height, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Arial, sans-serif", color="#dce8ef", size=12),
        title_font=dict(size=18, color=skin[0]), margin=dict(l=20, r=20, t=65, b=30),
        hoverlabel=dict(bgcolor="#142735", bordercolor=skin[0], font_color="#fff"),
        transition=dict(duration=650, easing="cubic-in-out"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(160,190,210,.10)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(160,190,210,.10)")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})

# ============================================================
# OVER SIMULATOR (bowling + batting animation, canvas based)
# ============================================================
SIM_HTML = r"""
<style>
body{margin:0;font-family:Inter,Arial,sans-serif;color:#e8f1f7;background:transparent}
#bar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:8px}
.chip{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:900;
 background:#13242f;border:1px solid #37505e;color:#9bb0c1;transition:all .3s}
.chip.on{transform:scale(1.18);border-color:__A__;color:__A__;box-shadow:0 0 12px __A__55}
.chip.w{background:#ff4d5e;color:#fff;border-color:#ff4d5e}.chip.f{background:__B__;color:#071018}.chip.s{background:__A__;color:#071018}
#score{margin-left:auto;font-weight:800;letter-spacing:1px}
button,select{background:#13242f;color:#e8f1f7;border:1px solid #37505e;border-radius:8px;padding:6px 12px;font-weight:700;cursor:pointer}
button:hover{border-color:__A__}
canvas{width:100%;border-radius:16px;border:1px solid #31475688;background:#0b1721}
</style>
<div id="bar"><b style="letter-spacing:2px;color:__A__">__NAME__</b><div id="chips" style="display:flex;gap:6px"></div>
<span id="score"></span>
<button id="re">↻ Replay</button><button id="pa">⏸ Pause</button>
<select id="sp"><option value="0.6">0.6x</option><option value="1" selected>1x</option><option value="1.8">1.8x</option></select></div>
<canvas id="c" width="720" height="540"></canvas>
<script>
const OUT=__OUT__, A="__A__", B="__B__";
const cv=document.getElementById('c'),g=cv.getContext('2d');
const cx=360,cy=270,rx=330,ry=245,bx=360,by=372;
const FIELD=[[360,120],[250,170],[470,170],[160,270],[560,270],[250,400],[470,400],[360,470]];
let i,t0,runs,wk,plan,paused=false,pausedAt=0,done,speed=1;
const chips=document.getElementById('chips');
function lbl(o){return o.r<0?'W':(o.r===0?'•':String(o.r))}
function reset(){i=0;runs=0;wk=0;done=false;t0=performance.now();plan=mk(OUT[0]);
 chips.innerHTML='';OUT.forEach(()=>{const d=document.createElement('div');d.className='chip';chips.appendChild(d)});
 mark();upd();}
function mk(r){const o={r:r,w:r<0};const a=(Math.random()*280-140)*Math.PI/180,dx=Math.sin(a),dy=-Math.cos(a);
 let d=0;for(;;){d+=4;const x=bx+dx*d,y=by+dy*d;if(((x-cx)/rx)**2+((y-cy)/ry)**2>=1)break;}
 const dist=o.w?0:(r===0?10:(r===4||r===6)?d:Math.min(d-12,[0,90,150,200,0,210][r]));
 return {o,dx,dy,dist,d};}
function mark(){[...chips.children].forEach((c,k)=>c.classList.toggle('on',k===i&&!done))}
function upd(){document.getElementById('score').textContent=runs+'/'+wk+' · ball '+Math.min(i+1,OUT.length)+'/'+OUT.length}
function settle(){const o=plan.o,c=chips.children[i];c.textContent=lbl(o);
 c.classList.add(o.w?'w':o.r===6?'s':o.r===4?'f':'x');if(o.w)wk++;else runs+=o.r;}
function field(){g.clearRect(0,0,720,540);
 const gr=g.createRadialGradient(cx,cy,40,cx,cy,rx);gr.addColorStop(0,'#1c5a3b');gr.addColorStop(1,'#0f3a28');
 g.fillStyle=gr;g.beginPath();g.ellipse(cx,cy,rx,ry,0,0,7);g.fill();
 g.strokeStyle=A;g.lineWidth=3;g.setLineDash([10,8]);g.beginPath();g.ellipse(cx,cy,rx,ry,0,0,7);g.stroke();g.setLineDash([]);
 g.strokeStyle='#ffffff22';g.lineWidth=1;g.beginPath();g.ellipse(cx,cy,rx*.55,ry*.55,0,0,7);g.stroke();
 g.fillStyle='#b99a63aa';g.fillRect(cx-16,170,32,205);
 g.strokeStyle='#fff8';g.lineWidth=1.5;g.beginPath();g.moveTo(cx-24,190);g.lineTo(cx+24,190);g.moveTo(cx-24,360);g.lineTo(cx+24,360);g.stroke();
 g.fillStyle='#ffffff55';FIELD.forEach(f=>{g.beginPath();g.arc(f[0],f[1],6,0,7);g.fill()});}
function stumps(x,y,scatter){g.strokeStyle='#f5e6b8';g.lineWidth=3;
 for(let k=-1;k<=1;k++){g.save();g.translate(x+k*7+k*scatter*26,y-scatter*(10+Math.abs(k)*6));g.rotate(k*scatter*1.6);
  g.beginPath();g.moveTo(0,-9);g.lineTo(0,9);g.stroke();g.restore();}}
function frame(now){
 if(paused){requestAnimationFrame(frame);return;}
 let el=(now-t0)*speed;
 if(!done&&el>2700){settle();i++;if(i>=OUT.length){done=true;mark();upd();}else{plan=mk(OUT[i]);t0=now;el=0;mark();upd();}}
 field();
 if(done){stumps(cx,190,0);stumps(cx,360,0);g.fillStyle='#fff';g.font='900 34px Arial';g.textAlign='center';
  g.fillText('Over complete: '+runs+'/'+wk,cx,cy+8);requestAnimationFrame(frame);return;}
 const o=plan.o;
 const by2=110+45*Math.min(1,el/700);
 g.fillStyle=B;g.beginPath();g.arc(cx-20,by2,11,0,7);g.fill();
 let sc=(o.w&&el>800)?Math.min(1,(el-800)/400):0;
 stumps(cx,190,0);stumps(cx,360,sc);
 g.fillStyle=A;g.beginPath();g.arc(bx-24,by+8,12,0,7);g.fill();
 const hit=Math.max(0,el-800);let ang=-0.9;
 if(el>650){const s=Math.min(1,(el-650)/260);ang=-0.9+(o.r===0||o.w?1.1:2.4)*s;}
 g.save();g.translate(bx-18,by+4);g.rotate(ang);g.strokeStyle='#e8c98a';g.lineWidth=7;g.lineCap='round';
 g.beginPath();g.moveTo(0,0);g.lineTo(0,-34);g.stroke();g.restore();
 let x,y,h=0,trail=null;
 if(el<800){const u=el/800,b=.72;y=150+(by-12-150)*u;x=cx;h=u<b?1-u/b:.35*Math.sin(Math.PI*(u-b)/(1-b));}
 else{const v=Math.min(1,hit/1700),e=1-(1-v)**2;
  if(o.w){x=cx+Math.sin(v*6)*3;y=by-10+e*14;}
  else{x=bx+plan.dx*plan.dist*e;y=by+plan.dy*plan.dist*e;if(o.r===6)h=Math.sin(Math.PI*Math.min(1,v*1.1))*2.4;trail=[bx,by,x,y];}}
 if(trail){g.strokeStyle=(o.r===6?B:A)+'88';g.lineWidth=3;g.setLineDash([2,7]);g.beginPath();g.moveTo(trail[0],trail[1]);g.lineTo(trail[2],trail[3]);g.stroke();g.setLineDash([]);}
 g.fillStyle='#0006';g.beginPath();g.ellipse(x,y+2,5+h*2,3,0,0,7);g.fill();
 g.fillStyle='#ff4d5e';g.shadowColor='#ff4d5e';g.shadowBlur=10;g.beginPath();g.arc(x,y-h*20,5+h*3,0,7);g.fill();g.shadowBlur=0;
 if(hit>150){const al=Math.min(1,(hit-150)/200);g.globalAlpha=al;g.textAlign='center';g.font='900 38px Arial';
  g.fillStyle=o.w?'#ff4d5e':(o.r>=4?A:'#dce8ef');
  g.fillText(o.w?'WICKET!':o.r===6?'SIX!':o.r===4?'FOUR!':o.r===0?'DOT BALL':o.r+(o.r>1?' RUNS':' RUN'),cx,70);g.globalAlpha=1;}
 requestAnimationFrame(frame);}
document.getElementById('re').onclick=()=>{paused=false;document.getElementById('pa').textContent='⏸ Pause';reset();};
document.getElementById('pa').onclick=e=>{if(!paused){paused=true;pausedAt=performance.now();e.target.textContent='▶ Resume';}
 else{t0+=performance.now()-pausedAt;paused=false;e.target.textContent='⏸ Pause';}};
document.getElementById('sp').onchange=e=>{speed=parseFloat(e.target.value)};
reset();requestAnimationFrame(frame);
</script>
"""

def sample_over(rows, rng):
    legal_rows = rows[rows["legal"] == 1]
    if legal_rows.empty:
        return [0] * 6
    pool = np.where(legal_rows["wickets"] == 1, -1, legal_rows["runs"].clip(0, 6).round()).astype(int)
    return [int(x) for x in rng.choice(pool, 6)]

def render_over_simulator(data):
    st.subheader("🎬 Over simulator: bowling + batting animation")
    st.caption("Six balls are sampled from the selected bowler's real delivery outcomes under your current filters, "
               "then animated: run-up, bounce, bat swing and ball flight. Shot direction is random (no direction data).")
    counts = data.groupby("bowler")["legal"].sum()
    names = counts[counts >= 6].sort_values(ascending=False).index.tolist()
    if not names:
        st.info("No bowler has enough legal balls under the current filters.")
        return
    c1, c2 = st.columns([3, 1])
    bowler = c1.selectbox("Bowler to animate", names, key="sim_bowler")
    if "sim_seed" not in st.session_state:
        st.session_state.sim_seed = 1
    if c2.button("🎲 Bowl a new over", use_container_width=True):
        st.session_state.sim_seed += 1
    rng = np.random.default_rng(st.session_state.sim_seed)
    outcomes = sample_over(data[data["bowler"] == bowler], rng)
    html = (SIM_HTML.replace("__OUT__", json.dumps(outcomes))
            .replace("__A__", skin[0]).replace("__B__", skin[1])
            .replace("__NAME__", str(bowler).upper().replace('"', "").replace("<", "")))
    components.html(html, height=680)

# ---------- Summary strip ----------
unique_bowlers = filtered["bowler"].nunique()
total_wickets = int(filtered["wickets"].sum())
total_balls = int(filtered["legal"].sum())
total_runs = float(filtered["runs"].sum())
unique_matches = filtered.loc[filtered["match"] != "Unknown", "match"].nunique()

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Bowlers", f"{unique_bowlers:,}")
m2.metric("Credited wickets", f"{total_wickets:,}")
m3.metric("Legal balls", f"{total_balls:,}")
m4.metric("Runs conceded", f"{total_runs:,.0f}")
m5.metric("Matches", f"{unique_matches:,}" if unique_matches else "N/A")
st.caption(f"Source: {DB_PATH.name} → {TABLE} · {len(filtered):,} delivery rows selected")

# ---------- Main pages ----------
tab_overview, tab_bowler, tab_visuals, tab_sim, tab_data = st.tabs(
    ["📊 Match Center", "🎯 Bowler Lab", "🌌 Visual Experiments", "🎬 Over Simulator", "🗃️ Data Inspector"])

with tab_overview:
    left, right = st.columns(2)
    with left:
        st.subheader("📈 Economy trend by season")
        by_season = filtered.groupby("season", as_index=False).agg(runs=("runs", "sum"), balls=("legal", "sum"), wickets=("wickets", "sum"))
        by_season["economy"] = 6 * by_season["runs"] / by_season["balls"].where(by_season["balls"] > 0)
        by_season = by_season.dropna(subset=["economy"]).sort_values("season")
        if not by_season.empty:
            fig = px.area(by_season, x="season", y="economy", markers=True, title="Season economy trend", hover_data=["balls", "wickets"])
            fig.update_traces(line_color=skin[0], fillcolor="rgba(184,255,59,.12)", marker=dict(size=8, color=skin[1]))
            style_fig(fig)
        else:
            st.info("No season values available for this selection.")
    with right:
        st.subheader("🎯 Wickets by innings phase")
        by_phase = filtered.groupby("phase", as_index=False).agg(wickets=("wickets", "sum"), deliveries=("legal", "sum"))
        by_phase = by_phase[by_phase["phase"].isin(phases)]
        if not by_phase.empty:
            fig = px.bar(by_phase, x="phase", y="wickets", color="phase", text="wickets", title="Wicket impact by phase", category_orders={"phase": phases}, color_discrete_sequence=COLORS)
            fig.update_traces(textposition="outside", marker_line_width=0)
            fig.update_layout(showlegend=False)
            style_fig(fig)
        else:
            st.info("Phase data isn't available for the selected filters.")
    st.divider()
    st.subheader("🏆 Leading wicket takers")
    leaders = valid.nlargest(15, "wickets").sort_values("wickets")
    if not leaders.empty:
        fig = px.bar(leaders, x="wickets", y="bowler", orientation="h", color="wickets", hover_data=["economy", "balls", "dot_pct"], title="Top wicket takers", color_continuous_scale=[skin[1], skin[0], "#ffb45c"])
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        style_fig(fig, 520)
    else:
        st.info("No bowlers meet the current minimum-ball threshold.")

with tab_bowler:
    st.subheader("🎯 Individual bowler breakdown")
    names = sorted(filtered["bowler"].unique().tolist())
    chosen_bowler = st.selectbox("Select a bowler", names)
    player_rows = filtered[filtered["bowler"] == chosen_bowler]
    player_stats = aggregate(player_rows).iloc[0]
    a, b, c, d = st.columns(4)
    a.metric("Wickets", f"{int(player_stats['wickets']):,}")
    b.metric("Economy", f"{player_stats['economy']:.2f}" if pd.notna(player_stats["economy"]) else "N/A")
    c.metric("Dot balls", f"{int(player_stats['dots']):,}")
    d.metric("Dot-ball %", f"{player_stats['dot_pct']:.1f}%" if pd.notna(player_stats["dot_pct"]) else "N/A")
    l, r = st.columns(2)
    with l:
        player_phase = player_rows.groupby("phase", as_index=False).agg(wickets=("wickets", "sum"), runs=("runs", "sum"), balls=("legal", "sum"))
        player_phase["economy"] = 6 * player_phase["runs"] / player_phase["balls"].where(player_phase["balls"] > 0)
        fig = px.bar(player_phase, x="phase", y="wickets", color="phase", title=f"{chosen_bowler}: wickets by phase", color_discrete_sequence=COLORS)
        fig.update_layout(showlegend=False)
        style_fig(fig)
    with r:
        player_season = player_rows.groupby("season", as_index=False).agg(wickets=("wickets", "sum"), runs=("runs", "sum"), balls=("legal", "sum"))
        player_season["economy"] = 6 * player_season["runs"] / player_season["balls"].where(player_season["balls"] > 0)
        player_season = player_season.dropna(subset=["economy"]).sort_values("season")
        fig = px.line(player_season, x="season", y="economy", markers=True, title=f"{chosen_bowler}: season economy", hover_data=["wickets", "balls"])
        fig.update_traces(line_color=skin[0], marker_color=skin[1], line_width=3)
        style_fig(fig)
    st.subheader("Bowler performance details")
    st.dataframe(player_season if not player_season.empty else player_rows.head(30), use_container_width=True, hide_index=True)

with tab_visuals:
    st.subheader("🌌 Visual experiments")
    chart_type = st.selectbox("Choose a chart", ["Impact bubble map", "Economy violin", "Radar profile", "Wicket treemap", "Animated season chart", "Bowler leaderboard race"])
    if chart_type == "Impact bubble map":
        plotdata = valid.copy()
        if not plotdata.empty:
            fig = px.scatter(plotdata, x="economy", y="wickets", size="balls", color="dot_pct", hover_name="bowler", hover_data=["runs", "matches"], size_max=42, color_continuous_scale=[skin[1], skin[0], "#ffb45c"], title="Bowler impact: economy × wickets")
            style_fig(fig, 520)
        else:
            st.info("Not enough data for the selected threshold.")
    elif chart_type == "Economy violin":
        violin = filtered.copy()
        violin["delivery_economy"] = 6 * violin["runs"] / violin["legal"].where(violin["legal"] > 0)
        violin = violin.replace([math.inf, -math.inf], pd.NA).dropna(subset=["delivery_economy"])
        if not violin.empty:
            cap = violin["delivery_economy"].quantile(.98)
            violin = violin[violin["delivery_economy"] <= cap]
            violin["style_label"] = violin["style"].where(violin["style"] != "Unknown", "Style not recorded")
            fig = px.violin(violin, x="style_label", y="delivery_economy", color="style_label", box=True, points=False, title="Economy distribution by recorded bowling style", color_discrete_sequence=COLORS)
            fig.update_layout(showlegend=False, xaxis_title="Bowling style", yaxis_title="Runs per six legal balls")
            style_fig(fig, 520)
        else:
            st.info("There aren't enough legal-ball records for this chart.")
    elif chart_type == "Radar profile":
        if not valid.empty:
            radar_name = st.selectbox("Bowler for radar", sorted(valid["bowler"].tolist()))
            row = valid[valid["bowler"] == radar_name].iloc[0]
            max_w = max(float(valid["wickets"].max()), 1)
            max_d = max(float(valid["dot_pct"].max()) if valid["dot_pct"].notna().any() else 1, 1)
            max_e = max(float(valid["economy"].max()), 1)
            vals = [100 * row["wickets"] / max_w, 100 * (row["dot_pct"] if pd.notna(row["dot_pct"]) else 0) / max_d, max(0, 100 * (1 - row["economy"] / max_e))]
            labels = ["Wicket impact", "Dot-ball rate", "Economy efficiency"]
            fig = go.Figure(go.Scatterpolar(r=vals + [vals[0]], theta=labels + [labels[0]], fill="toself", line=dict(color=skin[0], width=3), fillcolor="rgba(184,255,59,.17)", marker=dict(size=8, color=skin[1])))
            fig.update_layout(title=f"{radar_name}: relative performance profile", polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, range=[0, 100], gridcolor="#334653"), angularaxis=dict(gridcolor="#334653")), showlegend=False)
            style_fig(fig, 500)
        else:
            st.info("No bowlers match the current filters.")
    elif chart_type == "Wicket treemap":
        tree = valid[valid["wickets"] > 0].nlargest(35, "wickets")
        if not tree.empty:
            fig = px.treemap(tree, path=[px.Constant("IPL Bowlers"), "bowler"], values="wickets", color="economy", color_continuous_scale=[skin[0], skin[1], "#ffb45c"], hover_data=["balls", "dot_pct"], title="Wicket contribution map")
            style_fig(fig, 540)
        else:
            st.info("No credited wickets available for the current selection.")
    elif chart_type == "Animated season chart":
        race = filtered.groupby(["season", "bowler"], as_index=False).agg(wickets=("wickets", "sum"), runs=("runs", "sum"), balls=("legal", "sum"))
        race["economy"] = 6 * race["runs"] / race["balls"].where(race["balls"] > 0)
        race = race.dropna(subset=["economy"])
        if race["season"].nunique() > 1:
            top_names = race.groupby("bowler")["wickets"].sum().nlargest(12).index
            race = race[race["bowler"].isin(top_names)].copy()
            race["frame"] = race["season"].astype(str)
            fig = px.scatter(race, x="wickets", y="economy", animation_frame="frame", animation_group="bowler", color="bowler", size="balls", hover_name="bowler", range_x=[0, max(2, float(race["wickets"].max()) * 1.15)], range_y=[0, max(8, float(race["economy"].quantile(.98)) * 1.15)], title="Animated bowler performance by season", color_discrete_sequence=COLORS, size_max=28)
            fig.update_layout(transition=dict(duration=700, easing="cubic-in-out"))
            style_fig(fig, 560)
        else:
            st.info("Select data containing at least two seasons to use the animated chart.")
    else:
        race = filtered.groupby(["season", "bowler"], as_index=False).agg(wickets=("wickets", "sum"), balls=("legal", "sum"), runs=("runs", "sum"))
        if race["season"].nunique() > 1:
            top_names = race.groupby("bowler")["wickets"].sum().nlargest(10).index
            race = race[race["bowler"].isin(top_names)].copy()
            race["frame"] = race["season"].astype(str)
            fig = px.bar(race, x="wickets", y="bowler", color="wickets", animation_frame="frame", animation_group="bowler", orientation="h", range_x=[0, max(2, float(race["wickets"].max()) * 1.2)], title="Wicket leaderboard by season", color_continuous_scale=[skin[1], skin[0], "#ffb45c"])
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False, transition=dict(duration=650))
            style_fig(fig, 560)
        else:
            st.info("The leaderboard race needs at least two seasons.")

with tab_sim:
    render_over_simulator(filtered)
885
with tab_data:
    st.subheader("🗃️ Data inspector")
    with st.expander("Database and table details", expanded=True):
        st.write({"database": str(DB_PATH), "table": TABLE, "source_rows": len(raw), "filtered_rows": len(filtered)})
        st.write("Columns detected:", list(raw.columns))
    st.dataframe(filtered.head(500), use_container_width=True, hide_index=True)
    st.download_button("Download filtered data as CSV", filtered.to_csv(index=False).encode("utf-8"), file_name="ipl_bowling_filtered.csv", mime="text/csv")

st.divider()
st.markdown(f"<div style='padding:17px;border:1px solid #29404d;border-radius:14px;text-align:center;background:#0b1721'><b style='letter-spacing:2px;color:{skin[0]}'>IPL BOWLING EXPLORER</b><div style='color:#9bb0c1;font-size:12px;margin-top:7px'>Streamlit · Pandas · SQLite · Plotly · Interactive motion UI</div></div>", unsafe_allow_html=True)
st.caption("Economy = runs conceded × 6 / legal balls. Dot-ball rate counts legal deliveries with zero runs. Wicket attribution excludes common non-bowler dismissals where dismissal type is available.")