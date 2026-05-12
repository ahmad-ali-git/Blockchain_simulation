"""
51% Attack Simulation — Streamlit GUI
"""
import math
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from simulation import Simulation

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="51% Attack Simulation",
    page_icon="⛓️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═════════════════════════════════════════════════════════════════════════════
# INTRO ANIMATION (unchanged)
# ═════════════════════════════════════════════════════════════════════════════
INTRO_HTML = """
<style>
#intro-overlay {
    position: fixed; top: 0; left: 0;
    width: 100vw; height: 100vh;
    background: #050911;
    z-index: 99999;
    display: flex; align-items: center; justify-content: center;
    overflow: hidden;
    font-family: 'Segoe UI', sans-serif;
    animation: overlayExit .9s 5.8s ease-out forwards;
}
@keyframes overlayExit { to { opacity: 0; pointer-events: none; } }
.ig {
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(0,212,255,.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,.045) 1px, transparent 1px);
    background-size: 55px 55px;
    animation: iFade .8s .1s ease-out both;
}
.iglow {
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%,-50%);
    width: 680px; height: 680px;
    background: radial-gradient(ellipse, rgba(0,212,255,.09) 0%, transparent 68%);
    pointer-events: none;
    animation: iFade 1.2s .3s ease-out both;
}
.inode {
    position: absolute; border-radius: 50%;
    border: 1.5px solid rgba(0,212,255,.45);
    background: rgba(0,212,255,.06);
    box-shadow: 0 0 12px rgba(0,212,255,.25);
    animation: nodePulse var(--dur,4s) var(--del,0s) ease-in-out infinite alternate;
}
.inode.red {
    border-color: rgba(255,71,87,.5); background: rgba(255,71,87,.06);
    box-shadow: 0 0 12px rgba(255,71,87,.25); animation-name: nodePulseRed;
}
@keyframes nodePulse {
    0%   { opacity:.25; transform:translate(0,0) scale(1); }
    100% { opacity:.75; transform:translate(var(--tx,6px),var(--ty,-8px)) scale(1.12); }
}
@keyframes nodePulseRed {
    0%   { opacity:.2;  transform:translate(0,0) scale(1); }
    100% { opacity:.65; transform:translate(var(--tx,-6px),var(--ty,8px)) scale(1.1); }
}
.inet { position:absolute; inset:0; width:100%; height:100%; pointer-events:none; }
.inet line {
    stroke: rgba(0,212,255,.15); stroke-width:.8;
    animation: lineFlash var(--d,3s) var(--dl,0s) ease-in-out infinite alternate;
}
.inet line.red-line { stroke: rgba(255,71,87,.18); animation-name: lineFlashRed; }
@keyframes lineFlash    { 0%{opacity:.1} 100%{opacity:.55} }
@keyframes lineFlashRed { 0%{opacity:.1} 100%{opacity:.45} }
.hdrift {
    position: absolute; left: -420px;
    font-family: 'Consolas','Courier New',monospace;
    font-size: 11px; white-space: nowrap;
    color: rgba(0,212,255,.14);
    animation: drift var(--spd,18s) var(--del,0s) linear infinite;
    pointer-events: none;
}
.hdrift.red-text { color: rgba(255,71,87,.12); }
@keyframes drift {
    from { transform: translateX(0); }
    to   { transform: translateX(calc(100vw + 500px)); }
}
.icenter { position: relative; z-index: 2; text-align: center; pointer-events: none; }
.ieyebrow {
    font-size: 11px; letter-spacing: 5px; text-transform: uppercase;
    color: rgba(0,212,255,.8); margin-bottom: 18px;
    animation: iFade .6s 1.4s ease-out both;
}
.ititle {
    font-size: 62px; font-weight: 900; line-height: 1.0;
    color: #fff; letter-spacing: 6px; text-transform: uppercase; margin: 0;
    text-shadow: 0 0 45px rgba(0,212,255,.6), 0 0 90px rgba(0,212,255,.2);
    animation: iSlideUp .7s 1.8s ease-out both, iTitleGlow 2.5s 3.5s infinite;
}
.isub {
    font-size: 14.5px; color: rgba(255,255,255,.55);
    margin-top: 18px; line-height: 1.75;
    animation: iFade .6s 2.4s ease-out both;
}
.idiv {
    width: 0; height: 1px; margin: 20px auto;
    background: linear-gradient(90deg,transparent,#00d4ff,transparent);
    animation: iDivGrow .5s 2.8s ease-out both;
}
.iauthor {
    font-size: 11px; letter-spacing: 3px; text-transform: uppercase;
    color: rgba(255,255,255,.3);
    animation: iFade .5s 3.1s ease-out both;
}
#intro-skip {
    position: absolute; bottom: 26px; right: 34px;
    background: transparent; border: 1px solid rgba(255,255,255,.18);
    color: rgba(255,255,255,.4); padding: 7px 22px; border-radius: 20px;
    font-size: 11px; letter-spacing: 2px; cursor: pointer;
    transition: border-color .2s, color .2s;
    font-family: 'Segoe UI', sans-serif; z-index: 3; pointer-events: all;
}
#intro-skip:hover { border-color: #00d4ff; color: #00d4ff; }
@keyframes iFade    { from{opacity:0} to{opacity:1} }
@keyframes iSlideUp { from{opacity:0;transform:translateY(24px)} to{opacity:1;transform:translateY(0)} }
@keyframes iDivGrow { from{width:0;opacity:0} to{width:300px;opacity:1} }
@keyframes iTitleGlow {
    0%,100% { text-shadow:0 0 45px rgba(0,212,255,.6),0 0 90px rgba(0,212,255,.2); }
    50%     { text-shadow:0 0 65px rgba(0,212,255,.95),0 0 120px rgba(0,212,255,.45); }
}
</style>
<div id="intro-overlay">
  <div class="ig"></div><div class="iglow"></div>
  <svg class="inet" viewBox="0 0 100 100" preserveAspectRatio="none">
    <line x1="6" y1="16" x2="26" y2="8"  style="--d:3.2s;--dl:0.2s"/>
    <line x1="26" y1="8"  x2="52" y2="5"  style="--d:2.8s;--dl:0.8s"/>
    <line x1="52" y1="5"  x2="76" y2="10" style="--d:3.5s;--dl:0.4s"/>
    <line x1="76" y1="10" x2="93" y2="22" style="--d:2.6s;--dl:1.0s"/>
    <line x1="93" y1="22" x2="96" y2="52" style="--d:3.8s;--dl:0.1s"/>
    <line x1="96" y1="52" x2="87" y2="79" style="--d:2.9s;--dl:0.6s"/>
    <line x1="87" y1="79" x2="64" y2="93" style="--d:3.1s;--dl:0.3s"/>
    <line x1="64" y1="93" x2="34" y2="91" style="--d:2.7s;--dl:0.9s"/>
    <line x1="34" y1="91" x2="9"  y2="72" style="--d:3.4s;--dl:0.5s"/>
    <line x1="9"  y1="72" x2="4"  y2="46" style="--d:3.0s;--dl:0.7s"/>
    <line x1="4"  y1="46" x2="6"  y2="16" style="--d:2.5s;--dl:1.1s"/>
    <line x1="26" y1="8"  x2="9"  y2="72" class="red-line" style="--d:4.1s;--dl:0.3s"/>
    <line x1="76" y1="10" x2="87" y2="79" class="red-line" style="--d:3.7s;--dl:0.8s"/>
    <line x1="52" y1="5"  x2="96" y2="52" style="--d:4.5s;--dl:0.2s"/>
    <line x1="34" y1="91" x2="4"  y2="46" class="red-line" style="--d:3.9s;--dl:1.2s"/>
  </svg>
  <div class="inode" style="left:4%;top:14%;width:16px;height:16px;--dur:4.2s;--del:0.0s;--tx:7px;--ty:-9px"></div>
  <div class="inode" style="left:23%;top:6%;width:10px;height:10px;--dur:3.5s;--del:0.5s;--tx:-5px;--ty:6px"></div>
  <div class="inode" style="left:50%;top:3%;width:13px;height:13px;--dur:5.0s;--del:0.2s;--tx:4px;--ty:-7px"></div>
  <div class="inode" style="left:74%;top:8%;width:9px;height:9px;--dur:3.8s;--del:0.9s;--tx:6px;--ty:5px"></div>
  <div class="inode" style="left:91%;top:20%;width:15px;height:15px;--dur:4.6s;--del:0.3s;--tx:-8px;--ty:-6px"></div>
  <div class="inode" style="left:94%;top:50%;width:11px;height:11px;--dur:3.2s;--del:0.7s;--tx:-5px;--ty:8px"></div>
  <div class="inode" style="left:85%;top:77%;width:14px;height:14px;--dur:4.9s;--del:0.1s;--tx:6px;--ty:-5px"></div>
  <div class="inode" style="left:62%;top:91%;width:10px;height:10px;--dur:3.6s;--del:0.6s;--tx:-6px;--ty:4px"></div>
  <div class="inode" style="left:32%;top:89%;width:12px;height:12px;--dur:4.3s;--del:0.4s;--tx:5px;--ty:-8px"></div>
  <div class="inode" style="left:7%;top:70%;width:16px;height:16px;--dur:3.9s;--del:0.8s;--tx:-4px;--ty:7px"></div>
  <div class="inode" style="left:2%;top:44%;width:9px;height:9px;--dur:4.7s;--del:0.2s;--tx:8px;--ty:-5px"></div>
  <div class="inode red" style="left:18%;top:52%;width:8px;height:8px;--dur:3.3s;--del:0.6s;--tx:-6px;--ty:6px"></div>
  <div class="inode red" style="left:78%;top:37%;width:9px;height:9px;--dur:4.0s;--del:0.4s;--tx:5px;--ty:-7px"></div>
  <div class="inode red" style="left:58%;top:60%;width:7px;height:7px;--dur:2.9s;--del:1.0s;--tx:-4px;--ty:5px"></div>
  <div class="hdrift" style="top:8%;--spd:22s;--del:0s">BLOCK #1847 | SHA256: 0000a3f7b2c91e... | nonce: 284910</div>
  <div class="hdrift" style="top:19%;--spd:17s;--del:4s">merkle_root: 4a8b2c1d9f3e7a... | txs: 3 | miner: Honest_2</div>
  <div class="hdrift red-text" style="top:30%;--spd:25s;--del:8s">PRIVATE CHAIN: P1 → P2 → P3 [DOUBLE SPEND DETECTED] ⚠</div>
  <div class="hdrift" style="top:70%;--spd:19s;--del:2s">UTXO: Alice=990 Bob=510 Charlie=300 | prev_hash: 00002f8e...</div>
  <div class="hdrift red-text" style="top:80%;--spd:23s;--del:6s">LPC DEFENSE ACTIVE | consecutive_blocks=5 | REJECTED</div>
  <div class="hdrift" style="top:90%;--spd:20s;--del:1s">GENESIS → #1 → #2 → #3 | difficulty: 0000... | valid ✓</div>
  <div class="icenter">
    <div class="ieyebrow">CS619 · Final Year Project · Virtual University of Pakistan</div>
    <h1 class="ititle">51% ATTACK<br>SIMULATION</h1>
    <p class="isub">A Simulation-Based Framework for Mitigating<br>a 51% Attack on Blockchain Networks</p>
    <div class="idiv"></div>
    <p class="iauthor">Ahmad Ali &nbsp;·&nbsp; BC220425973 &nbsp;·&nbsp; F25PROJECT5043F</p>
  </div>
  <button id="intro-skip">SKIP →</button>
</div>
"""

INTRO_JS = """
<script>
(function () {
    var TRIES = 0;
    function init() {
        try {
            var pdoc = window.parent.document;
            var pss  = window.parent.sessionStorage;
            var ov   = pdoc.getElementById('intro-overlay');
            if (!ov) { if (TRIES++ < 25) setTimeout(init, 80); return; }
            try {
                if (pss.getItem('_51iv2')) {
                    ov.style.cssText += ';opacity:0!important;pointer-events:none!important;';
                    return;
                }
            } catch(e) {}
            function hide(fast) {
                ov.style.transition = 'opacity ' + (fast ? '.22s' : '.7s') + ' ease-out';
                ov.style.opacity = '0'; ov.style.pointerEvents = 'none';
                setTimeout(function () {
                    ov.style.display = 'none';
                    try { pss.setItem('_51iv2', '1'); } catch(e) {}
                }, fast ? 230 : 720);
            }
            setTimeout(function () { hide(false); }, 5500);
            var btn = pdoc.getElementById('intro-skip');
            if (btn) btn.addEventListener('click', function(e) { e.stopPropagation(); hide(true); });
            setTimeout(function () {
                ov.style.cursor = 'pointer';
                ov.addEventListener('click', function(e) { if (e.target.id !== 'intro-skip') hide(true); });
            }, 1500);
        } catch(e) { if (TRIES++ < 25) setTimeout(init, 80); }
    }
    setTimeout(init, 50);
}());
</script>
"""

st.markdown(INTRO_HTML, unsafe_allow_html=True)
components.html(INTRO_JS, height=0)


# ═════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="collapsedControl"] { display: none; }
.stApp { background: #060b14 !important; }
.block-container { padding: 0 2.8rem 0 !important; max-width: 100% !important; }

/* ── background animation layer ── */
#bg-layer {
    position: fixed; inset: 0; z-index: 1;
    pointer-events: none; overflow: hidden;
}
.bgl-grid {
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(0,212,255,.018) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,.018) 1px, transparent 1px);
    background-size: 64px 64px;
}
.bgl-glow {
    position: absolute; top: 30%; left: 50%;
    transform: translate(-50%, -50%);
    width: 900px; height: 500px;
    background: radial-gradient(ellipse, rgba(0,212,255,.035) 0%, transparent 65%);
}
.bgl-glow-r {
    position: absolute; top: 70%; left: 65%;
    transform: translate(-50%, -50%);
    width: 600px; height: 400px;
    background: radial-gradient(ellipse, rgba(255,71,87,.022) 0%, transparent 65%);
}
.bgn {
    position: absolute; border-radius: 50%;
    background: rgba(0,212,255,.055);
    border: 1px solid rgba(0,212,255,.1);
    animation: bgnFloat var(--d,10s) var(--dl,0s) ease-in-out infinite alternate;
}
.bgn.r { background: rgba(255,71,87,.04); border-color: rgba(255,71,87,.08); }
@keyframes bgnFloat {
    from { transform: translate(0,0); opacity: .4; }
    to   { transform: translate(var(--tx,20px),var(--ty,-15px)); opacity: .9; }
}

/* ── hero header ── */
.hero-wrap {
    background: linear-gradient(180deg, #0a1628 0%, #070e1c 100%);
    border-bottom: 1px solid rgba(0,212,255,.12);
    padding: 0 2.8rem;
    margin: 0 -2.8rem;
    position: relative; z-index: 10;
    overflow: hidden;
}
.hero-inner {
    display: flex; align-items: center;
    justify-content: space-between;
    height: 72px; gap: 24px;
}
.hero-title {
    font-size: 22px; font-weight: 900; letter-spacing: 3px;
    text-transform: uppercase; color: #fff; margin: 0; white-space: nowrap;
    text-shadow: 0 0 30px rgba(0,212,255,.5);
}
.hero-sub {
    font-size: 10px; letter-spacing: 3px; text-transform: uppercase;
    color: rgba(0,212,255,.55); margin-top: 2px;
}
.hero-chain {
    flex: 1; overflow: hidden; height: 26px;
    margin: 0 24px; opacity: .45;
}
.hero-chain-inner {
    display: flex; align-items: center; gap: 0;
    white-space: nowrap;
    animation: chainScroll 28s linear infinite;
}
.hcb {
    display: inline-flex; align-items: center; justify-content: center;
    width: 32px; height: 20px; border-radius: 3px;
    background: rgba(0,212,255,.08); border: 1px solid rgba(0,212,255,.2);
    font-family: 'Consolas', monospace; font-size: 8.5px;
    color: rgba(0,212,255,.7); margin: 0 1px;
    flex-shrink: 0;
}
.hcb.atk {
    background: rgba(255,71,87,.08); border-color: rgba(255,71,87,.2);
    color: rgba(255,71,87,.7);
}
.hc-arrow {
    color: rgba(0,212,255,.3); font-size: 10px;
    margin: 0 1px; flex-shrink: 0;
}
@keyframes chainScroll {
    from { transform: translateX(0); }
    to   { transform: translateX(-50%); }
}
.hero-badge {
    background: rgba(0,212,255,.08); border: 1px solid rgba(0,212,255,.25);
    color: rgba(0,212,255,.8); font-size: 10px; letter-spacing: 2px;
    padding: 5px 14px; border-radius: 20px; white-space: nowrap; flex-shrink: 0;
}

/* ── top spacing after hero ── */


/* ── section label ── */
.sec-lbl {
    font-size: 9.5px; font-weight: 800; letter-spacing: 4px;
    text-transform: uppercase; color: rgba(0,212,255,.45);
    margin: 0 0 16px;
    display: flex; align-items: center; gap: 12px;
}
.sec-lbl::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(0,212,255,.15), transparent);
}

/* ── config cards ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #0b1424 !important;
    border: 1px solid #182035 !important;
    border-radius: 18px !important;
    padding: 8px 4px !important;
}
.card-lbl {
    font-size: 9.5px; font-weight: 800; letter-spacing: 3px;
    text-transform: uppercase; margin-bottom: 18px;
}
.card-lbl-blue { color: rgba(0,212,255,.65); }
.card-lbl-red  { color: rgba(255,71,87,.65); }
.card-lbl-gray { color: rgba(255,255,255,.35); }

/* ── number input — stepper style ── */
[data-testid="stNumberInput"] label {
    font-size: 9px !important;
    letter-spacing: 2.5px !important;
    text-transform: uppercase !important;
    color: rgba(255,255,255,.38) !important;
    font-weight: 700 !important;
}
[data-testid="stNumberInput"] > div {
    background: #08111e !important;
    border: 1px solid #1d2e48 !important;
    border-radius: 10px !important;
    overflow: hidden;
}
[data-testid="stNumberInput"] input {
    color: #e8f4fd !important;
    font-size: 26px !important;
    font-weight: 800 !important;
    text-align: center !important;
    background: transparent !important;
    border: none !important;
    font-family: 'Consolas', monospace !important;
    padding: 10px 4px !important;
}
[data-testid="stNumberInput"] button {
    background: #111f33 !important;
    color: rgba(0,212,255,.8) !important;
    border: none !important;
    border-radius: 0 !important;
    font-size: 18px !important;
    font-weight: 800 !important;
    min-width: 40px !important;
    transition: background .15s !important;
}
[data-testid="stNumberInput"] button:hover {
    background: rgba(0,212,255,.18) !important;
    color: #00d4ff !important;
}
[data-testid="stNumberInput"] button:first-of-type {
    border-right: 1px solid #1d2e48 !important;
}
[data-testid="stNumberInput"] button:last-of-type {
    border-left: 1px solid #1d2e48 !important;
}

/* ── slider — refined ── */
[data-testid="stSlider"] label {
    font-size: 9px !important;
    letter-spacing: 2.5px !important;
    text-transform: uppercase !important;
    color: rgba(255,255,255,.38) !important;
    font-weight: 700 !important;
}
[data-testid="stSlider"] [data-testid="stTickBarMin"],
[data-testid="stSlider"] [data-testid="stTickBarMax"] {
    color: rgba(255,255,255,.2) !important;
    font-size: 10px !important;
}
[data-testid="stSlider"] > div > div > div > div {
    background: rgba(0,212,255,.25) !important;
}
[data-testid="stSlider"] > div > div > div > div > div {
    background: #00d4ff !important;
    border: 2px solid #060b14 !important;
    box-shadow: 0 0 10px rgba(0,212,255,.6), 0 0 20px rgba(0,212,255,.2) !important;
    width: 18px !important; height: 18px !important;
}

/* ── select slider (difficulty) ── */
.diff-wrap { margin: 4px 0 0; }

/* ── radio (run mode) ── */
[data-testid="stRadio"] label {
    font-size: 9px !important; letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: rgba(255,255,255,.35) !important; font-weight: 700 !important;
}
[data-testid="stRadio"] > div {
    gap: 6px !important;
}
[data-testid="stRadio"] > div > label {
    background: #08111e !important;
    border: 1px solid #1d2e48 !important;
    border-radius: 8px !important;
    padding: 7px 14px !important;
    color: rgba(255,255,255,.5) !important;
    font-size: 11px !important;
    cursor: pointer !important;
    transition: all .15s !important;
    white-space: nowrap !important;
}
[data-testid="stRadio"] > div > label:has(input:checked) {
    background: rgba(0,212,255,.1) !important;
    border-color: rgba(0,212,255,.4) !important;
    color: #00d4ff !important;
}

/* hide radio circle dots */
[data-testid="stRadio"] > div > label > div:first-child {
    display: none !important;
}

/* ── node dot grid ── */
.ndot-grid {
    display: flex; flex-wrap: wrap; gap: 10px;
    margin-top: 14px; padding: 12px;
    background: #060b14; border-radius: 10px;
    border: 1px solid #182035;
    min-height: 54px;
}
.ndot-pool {
    display: flex; flex-wrap: wrap; gap: 4px;
    padding: 6px 7px;
    background: rgba(0,212,255,.04);
    border: 1px solid rgba(0,212,255,.1);
    border-radius: 7px;
}
.ndot {
    width: 9px; height: 9px; border-radius: 50%;
    background: #00d4ff;
    box-shadow: 0 0 6px rgba(0,212,255,.6);
    opacity: .75;
}
.ndot-lbl {
    width: 100%; font-size: 9px; text-align: center;
    color: rgba(255,255,255,.2); margin-top: 3px;
    letter-spacing: 1px; font-family: 'Consolas', monospace;
}
.ndot-atk-pool {
    display: flex; flex-wrap: wrap; gap: 4px;
    padding: 8px; max-height: 90px; overflow: hidden;
}
.ndot-atk {
    width: 9px; height: 9px; border-radius: 50%;
    background: #ff4757;
    box-shadow: 0 0 6px rgba(255,71,87,.6);
    opacity: .75;
}
.ndot-more {
    font-size: 9px; color: rgba(0,212,255,.45);
    letter-spacing: 1px; align-self: center;
    font-family: 'Consolas', monospace;
}

/* ── attacker big % ── */
.atk-pct-wrap {
    text-align: center; padding: 20px 0 12px;
    position: relative;
}
.atk-pct-ring {
    width: 130px; height: 130px; margin: 0 auto;
    border-radius: 50%; display: flex;
    align-items: center; justify-content: center;
    flex-direction: column; position: relative;
}
.atk-pct-val {
    font-size: 38px; font-weight: 900;
    letter-spacing: -1px; line-height: 1;
}
.atk-pct-sub {
    font-size: 9px; letter-spacing: 3px; font-weight: 700;
    text-transform: uppercase; margin-top: 2px;
    opacity: .7;
}
.atk-pct-nodes {
    font-size: 11px; color: rgba(255,255,255,.3);
    margin-top: 10px; letter-spacing: 1px;
}

/* ── network ring SVG area ── */
.net-wrap {
    background: #0b1424;
    border: 1px solid #182035;
    border-radius: 18px;
    padding: 24px 32px;
    margin: 20px 0;
    display: flex; align-items: center; gap: 32px;
}
.net-svg-col { flex-shrink: 0; }
.net-stats-col { flex: 1; }
.net-stat-row {
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid #182035;
}
.net-stat-row:last-child { border-bottom: none; }
.nsr-label {
    font-size: 9.5px; letter-spacing: 2.5px;
    text-transform: uppercase; font-weight: 700;
}
.nsr-val {
    font-size: 18px; font-weight: 800;
    font-family: 'Consolas', monospace;
}
.nsr-bar {
    height: 4px; border-radius: 2px; margin-top: 4px;
}

/* ── run button ── */
.run-btn-wrap {
    display: flex; justify-content: center;
    margin: 24px 0 0;
}
div[data-testid="stButton"] > button {
    font-weight: 800 !important; font-size: 13px !important;
    letter-spacing: 3px !important; border: none !important;
    border-radius: 50px !important;
    padding: 14px 48px !important;
    text-transform: uppercase !important;
    transition: all .2s !important;
    white-space: nowrap !important;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 36px rgba(0,0,0,.5) !important;
}
div[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
}

/* ── progress bar ── */
[data-testid="stProgressBar"] > div { background: #182035 !important; }
[data-testid="stProgressBar"] > div > div { background: #00d4ff !important; }

/* ── event log ── */
.elog { height: 280px; overflow-y: auto; border-radius: 10px; padding: 4px; }
.elog::-webkit-scrollbar { width: 3px; }
.elog::-webkit-scrollbar-track { background: #0b1424; }
.elog::-webkit-scrollbar-thumb { background: #1d2e48; border-radius: 3px; }
.ev {
    padding: 6px 10px; margin-bottom: 3px; border-radius: 5px;
    font-family: 'Consolas', monospace; font-size: 11.5px; line-height: 1.45;
}
.ev-mine    { background:#0d1f10; border-left:3px solid #2ed573; color:#7cf5a0; }
.ev-attack  { background:#1f0d0d; border-left:3px solid #ff4757; color:#ff8591; }
.ev-defense { background:#0d1526; border-left:3px solid #00d4ff; color:#6ecff6; }
.ev-result  { background:#131f0d; border-left:3px solid #a8e063; color:#c6f47c; }
.ev-info    { background:#10192a; border-left:3px solid #2d3748; color:#6b7d99; }

/* ── metric cards ── */
.mcard {
    background: #0b1424; border-radius: 14px;
    padding: 20px 16px 16px; border: 1px solid #182035;
    text-align: center; height: 100%;
}
.mcard-val { font-size: 24px; font-weight: 800; margin: 7px 0 4px; }
.mcard-label {
    font-size: 9px; letter-spacing: 2.5px;
    color: rgba(255,255,255,.3); text-transform: uppercase; font-weight: 700;
}
.mcard-sub { font-size: 10.5px; color: rgba(255,255,255,.25); margin-top: 4px; }
.val-danger  { color: #ff4757; }
.val-safe    { color: #2ed573; }
.val-neutral { color: #00d4ff; }
.val-warn    { color: #ffa502; }

/* override st.container border for simulation blocks */
.sim-container [data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px !important;
    padding: 4px !important;
}

/* caption */
.stCaption { color: rgba(255,255,255,.28) !important; }
</style>
""", unsafe_allow_html=True)


# ── Persistent background animation ──────────────────────────────────────────
st.markdown("""
<div id="bg-layer">
  <div class="bgl-grid"></div>
  <div class="bgl-glow"></div>
  <div class="bgl-glow-r"></div>
  <div class="bgn" style="left:5%;top:18%;width:18px;height:18px;--d:14s;--dl:0s;--tx:20px;--ty:-12px;"></div>
  <div class="bgn" style="left:12%;top:55%;width:10px;height:10px;--d:11s;--dl:2s;--tx:-14px;--ty:10px;"></div>
  <div class="bgn" style="left:88%;top:22%;width:14px;height:14px;--d:16s;--dl:1s;--tx:-18px;--ty:-8px;"></div>
  <div class="bgn" style="left:92%;top:68%;width:8px;height:8px;--d:12s;--dl:3s;--tx:12px;--ty:14px;"></div>
  <div class="bgn" style="left:45%;top:8%;width:12px;height:12px;--d:18s;--dl:0.5s;--tx:10px;--ty:-16px;"></div>
  <div class="bgn" style="left:68%;top:82%;width:16px;height:16px;--d:13s;--dl:4s;--tx:-10px;--ty:10px;"></div>
  <div class="bgn r" style="left:25%;top:75%;width:9px;height:9px;--d:15s;--dl:1.5s;--tx:16px;--ty:-6px;"></div>
  <div class="bgn r" style="left:75%;top:40%;width:11px;height:11px;--d:10s;--dl:3.5s;--tx:-12px;--ty:8px;"></div>
</div>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("baseline_result", None), ("protected_result", None), ("last_run_mode", None)]:
    if k not in st.session_state:
        st.session_state[k] = v


# ═════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════════════
def node_dot_grid_html(num_miners, nodes_each):
    MAX_N = 6   # max dots shown per miner
    MAX_M = 7   # max miners shown
    html = '<div class="ndot-grid">'
    show_miners = min(num_miners, MAX_M)
    show_nodes  = min(nodes_each, MAX_N)
    for m in range(show_miners):
        html += f'<div class="ndot-pool">'
        for _ in range(show_nodes):
            html += '<span class="ndot"></span>'
        if nodes_each > MAX_N:
            html += f'<span class="ndot-more">+{nodes_each - MAX_N}</span>'
        html += f'<div class="ndot-lbl">M{m+1}</div></div>'
    if num_miners > MAX_M:
        html += f'<div style="font-size:9px;color:rgba(0,212,255,.35);align-self:center;letter-spacing:1px;">+{num_miners - MAX_M} more</div>'
    html += '</div>'
    return html


def attacker_dot_grid_html(attacker_nodes):
    MAX_DOTS = 30
    show = min(attacker_nodes, MAX_DOTS)
    html = '<div class="ndot-atk-pool">'
    for _ in range(show):
        html += '<span class="ndot-atk"></span>'
    if attacker_nodes > MAX_DOTS:
        html += f'<span class="ndot-more">+{attacker_nodes - MAX_DOTS}</span>'
    html += '</div>'
    return html


def network_topology_svg(honest_total, attacker_nodes):
    total = honest_total + attacker_nodes
    W, H = 220, 220
    cx, cy, r = W / 2, H / 2, 82

    MAX_DOTS = 40
    scale = min(1.0, MAX_DOTS / max(total, 1))
    h_show = max(1, round(honest_total * scale))
    a_show = max(1, round(attacker_nodes * scale))
    t_show = h_show + a_show

    circles = ""
    for i in range(t_show):
        angle = (i / t_show) * 2 * math.pi - math.pi / 2
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        is_atk = (i >= h_show)
        color = "#ff4757" if is_atk else "#00d4ff"
        glow  = "rgba(255,71,87,.5)" if is_atk else "rgba(0,212,255,.5)"
        node_r = 5 if is_atk else 4.5
        circles += (
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{node_r}" fill="{color}" opacity="0.85">'
            f'<animate attributeName="opacity" values="0.85;0.5;0.85" dur="{2 + (i % 4)}s" repeatCount="indefinite"/>'
            f'</circle>'
        )

    ap = attacker_nodes / total * 100
    threat_color = "#ff4757" if ap > 50 else ("#ffa502" if ap > 40 else "#2ed573")

    return f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:{W}px;height:{H}px;">
        <circle cx="{cx}" cy="{cy}" r="{r+16}" fill="none" stroke="rgba(0,212,255,.06)" stroke-width="1.5"/>
        <circle cx="{cx}" cy="{cy}" r="{r+8}"  fill="none" stroke="rgba(0,212,255,.04)" stroke-width="1"/>
        {circles}
        <text x="{cx}" y="{cy - 10}" text-anchor="middle"
              fill="{threat_color}" font-size="26" font-weight="800"
              font-family="Segoe UI, sans-serif">{ap:.1f}%</text>
        <text x="{cx}" y="{cy + 10}" text-anchor="middle"
              fill="{threat_color}" font-size="8.5" font-weight="700"
              font-family="Segoe UI, sans-serif" letter-spacing="2" opacity="0.7">ATTACKER</text>
        <text x="{cx}" y="{cy + 26}" text-anchor="middle"
              fill="rgba(255,255,255,.22)" font-size="8"
              font-family="Segoe UI, sans-serif" letter-spacing="1">{total} TOTAL NODES</text>
    </svg>'''


def styled_event_log(log_lines, placeholder):
    rows = ""
    for line in log_lines[-60:]:
        u = line.upper()
        cls = (
            "ev-attack"  if ("ATTACK" in u or "[!]" in u or "PRIVATE" in u) else
            "ev-defense" if ("DEFENSE" in u or "LPC" in u or "SAFE MODE" in u or "REJECTED" in u) else
            "ev-result"  if ("RESULT" in u or "SUCCESS" in u or "FAILED" in u or "CONCLUSION" in u) else
            "ev-mine"    if ("MINED" in u or "BLOCK" in u) else
            "ev-info"
        )
        safe = line.replace("<", "&lt;").replace(">", "&gt;")
        rows += f'<div class="ev {cls}">{safe}</div>'
    placeholder.markdown(f'<div class="elog">{rows}</div>', unsafe_allow_html=True)


def run_single(method, prog, log_ph, chart_ph, anim_delay):
    sim = Simulation(
        honest_nodes=st.session_state["honest_nodes"],
        attacker_nodes=st.session_state["attacker_nodes"],
        total_blocks=st.session_state["total_blocks"],
        difficulty=st.session_state["difficulty"],
        max_consecutive=st.session_state["max_consecutive"],
        attack_start_fraction=st.session_state["attack_start_pct"] / 100.0,
    )
    log_lines, history = [], []

    def on_event(ev):
        kind, msg = ev["kind"], ev.get("message", "")
        if kind == "progress":
            step, total = ev["step"], ev["total"]
            prog.progress(step / total, text=f"⛏  Mining block {step} / {total}")
            history.append((step, ev["honest_len"], ev["private_len"]))
            df = pd.DataFrame(history, columns=["step", "honest", "private"])
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["step"], y=df["honest"], mode="lines", name="Honest chain",
                line=dict(color="#00d4ff", width=2.5),
                fill="tozeroy", fillcolor="rgba(0,212,255,.07)",
            ))
            fig.add_trace(go.Scatter(
                x=df["step"], y=df["private"], mode="lines", name="Attacker private",
                line=dict(color="#ff4757", width=2.5, dash="dash"),
                fill="tozeroy", fillcolor="rgba(255,71,87,.07)",
            ))
            fig.update_layout(
                paper_bgcolor="#0b1424", plot_bgcolor="#060b14",
                font_color="#6b7d99", height=300,
                margin=dict(l=10, r=10, t=36, b=10),
                title=dict(text="Chain Growth — Honest vs Attacker",
                           font=dict(size=12, color="#00d4ff")),
                xaxis=dict(title="Step", gridcolor="#182035", color="#4a5568"),
                yaxis=dict(title="Length", gridcolor="#182035", color="#4a5568"),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
            )
            chart_ph.plotly_chart(fig, use_container_width=True, key=f"lc_{method}_{step}")
        elif msg:
            log_lines.append(msg)
            styled_event_log(log_lines, log_ph)
        if anim_delay > 0 and kind == "progress":
            time.sleep(anim_delay)

    sim.on_event = on_event
    result = sim.run_baseline() if method == "baseline" else sim.run_protected()
    result["log"] = log_lines
    result["chain_history"] = history
    result["honest_miners"] = [
        {"miner_id": m.miner_id, "num_nodes": m.num_nodes,
         "blocks_mined": m.blocks_mined, "hashrate": m.hashrate}
        for m in sim.honest_miners
    ]
    result["attacker_info"] = {
        "miner_id": sim.attacker.miner_id,
        "num_nodes": sim.attacker.num_nodes,
        "blocks_mined": sim.attacker.blocks_mined,
        "hashrate": sim.attacker.hashrate,
    }
    return result


# ═════════════════════════════════════════════════════════════════════════════
# HERO HEADER — animated chain
# ═════════════════════════════════════════════════════════════════════════════
CHAIN_ITEMS = "".join([
    f'<span class="hcb">{h}</span><span class="hc-arrow">→</span>'
    for h in ["#001","#002","#003","#004","#005","#006","#007","#008","#009","#010",
              "#011","#012","#013","#014","#015","#016","#017","#018"]
] + [
    f'<span class="hcb atk">{h}</span><span class="hc-arrow" style="color:rgba(255,71,87,.3)">→</span>'
    for h in ["#P1","#P2","#P3"]
] + [
    f'<span class="hcb">{h}</span><span class="hc-arrow">→</span>'
    for h in ["#001","#002","#003","#004","#005","#006","#007","#008","#009","#010",
              "#011","#012","#013","#014","#015","#016","#017","#018"]
] + [
    f'<span class="hcb atk">{h}</span><span class="hc-arrow" style="color:rgba(255,71,87,.3)">→</span>'
    for h in ["#P1","#P2","#P3"]
])

st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-inner">
    <div>
      <div class="hero-title">⛓ &nbsp;51% ATTACK SIMULATION</div>
      <div class="hero-sub">Blockchain Security · CS619 FYP · Virtual University of Pakistan</div>
    </div>
    <div class="hero-chain">
      <div class="hero-chain-inner">{CHAIN_ITEMS}</div>
    </div>
    <div class="hero-badge">F25PROJECT5043F</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# CONFIGURATION BENTO
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-lbl">Configuration</div>', unsafe_allow_html=True)

col_h, col_a, col_p = st.columns([1.05, 0.85, 1.55], gap="medium")

# ── Honest miners card ────────────────────────────────────────────────────────
with col_h:
    with st.container(border=True):
        st.markdown('<div class="card-lbl card-lbl-blue">🔷 Honest Miners</div>',
                    unsafe_allow_html=True)

        ci1, ci2 = st.columns(2, gap="small")
        with ci1:
            num_honest = st.number_input(
                "Miners", min_value=2, max_value=10, value=5, step=1, key="num_honest"
            )
        with ci2:
            npe = st.number_input(
                "Nodes / Miner", min_value=1, max_value=20, value=2, step=1, key="npe"
            )

        honest_nodes = [int(npe)] * int(num_honest)
        total_honest = sum(honest_nodes)

        st.markdown(node_dot_grid_html(int(num_honest), int(npe)),
                    unsafe_allow_html=True)

        st.markdown(
            f'<div style="font-size:10px;color:rgba(255,255,255,.28);margin-top:10px;'
            f'letter-spacing:1px;text-align:center;">'
            f'{int(num_honest)} miners · <strong style="color:rgba(0,212,255,.6);">'
            f'{total_honest}</strong> total honest nodes</div>',
            unsafe_allow_html=True,
        )

# ── Attacker card ─────────────────────────────────────────────────────────────
with col_a:
    with st.container(border=True):
        st.markdown('<div class="card-lbl card-lbl-red">🔴 Attacker</div>',
                    unsafe_allow_html=True)

        attacker_nodes = st.number_input(
            "Nodes", min_value=1, max_value=200, value=12, step=1,
            key="attacker_nodes_input"
        )
        attacker_nodes = int(attacker_nodes)
        total_nodes = total_honest + attacker_nodes
        atk_pct = attacker_nodes / total_nodes * 100

        if atk_pct > 50:
            atk_color = "#ff4757"; threat_label = "⚠ CRITICAL"
        elif atk_pct > 40:
            atk_color = "#ffa502"; threat_label = "⚡ WARNING"
        else:
            atk_color = "#2ed573"; threat_label = "✓ LOW RISK"

        # ring border color from threat
        ring_shadow = (
            "0 0 0 3px rgba(255,71,87,.25), 0 0 30px rgba(255,71,87,.15)"
            if atk_pct > 50 else
            "0 0 0 3px rgba(255,165,2,.2), 0 0 24px rgba(255,165,2,.1)"
            if atk_pct > 40 else
            "0 0 0 3px rgba(46,213,115,.2), 0 0 24px rgba(46,213,115,.1)"
        )

        st.markdown(f"""
        <div style="text-align:center;padding:14px 0 4px;">
          <div style="width:120px;height:120px;margin:0 auto;border-radius:50%;
                      background:#08111e;border:1px solid #1d2e48;
                      display:flex;align-items:center;justify-content:center;
                      flex-direction:column;box-shadow:{ring_shadow};">
            <div style="font-size:34px;font-weight:900;color:{atk_color};
                        font-family:'Segoe UI',sans-serif;line-height:1;">
              {atk_pct:.1f}%
            </div>
            <div style="font-size:8px;letter-spacing:2.5px;font-weight:800;
                        color:{atk_color};opacity:.7;text-transform:uppercase;
                        margin-top:3px;">
              {threat_label}
            </div>
          </div>
          <div style="font-size:10.5px;color:rgba(255,255,255,.28);
                      margin-top:10px;letter-spacing:1px;">
            {attacker_nodes} / {total_nodes} nodes
          </div>
        </div>
        {attacker_dot_grid_html(attacker_nodes)}
        """, unsafe_allow_html=True)

# ── Parameters card ───────────────────────────────────────────────────────────
with col_p:
    with st.container(border=True):
        st.markdown('<div class="card-lbl card-lbl-gray">⚙ Parameters</div>',
                    unsafe_allow_html=True)

        pr1, pr2 = st.columns(2, gap="medium")
        with pr1:
            total_blocks = st.slider(
                "Total Blocks", 10, 200, 30, key="total_blocks_s"
            )
            max_consec = st.slider(
                "LPC Limit (consecutive)", 2, 20, 6, key="max_consec_s"
            )
        with pr2:
            attack_start = st.slider(
                "Attack Starts At (%)", 10, 90, 33, key="attack_start_s"
            )
            anim_ms = st.slider(
                "Animation Speed (ms/block)", 0, 300, 40, key="anim_ms_s"
            )

        st.markdown(
            '<div style="font-size:9px;letter-spacing:2.5px;text-transform:uppercase;'
            'color:rgba(255,255,255,.3);font-weight:700;margin:12px 0 6px;">PoW Difficulty</div>',
            unsafe_allow_html=True,
        )
        difficulty = st.select_slider(
            "", options=[1, 2, 3, 4, 5], value=2,
            key="difficulty_sel", label_visibility="collapsed"
        )

        st.markdown(
            '<div style="font-size:9px;letter-spacing:2.5px;text-transform:uppercase;'
            'color:rgba(255,255,255,.3);font-weight:700;margin:12px 0 6px;">Run Mode</div>',
            unsafe_allow_html=True,
        )
        run_mode = st.radio(
            "", ["Compare Both", "Baseline Only", "Protected Only"],
            horizontal=True, key="run_mode_r", label_visibility="collapsed"
        )

# save to session state
st.session_state["honest_nodes"]     = honest_nodes
st.session_state["attacker_nodes"]   = attacker_nodes
st.session_state["total_blocks"]     = total_blocks
st.session_state["difficulty"]       = difficulty
st.session_state["max_consecutive"]  = max_consec
st.session_state["attack_start_pct"] = attack_start


# ═════════════════════════════════════════════════════════════════════════════
# NETWORK TOPOLOGY
# ═════════════════════════════════════════════════════════════════════════════
hp = total_honest / total_nodes * 100
ap = atk_pct

stat_color = "#ff4757" if ap > 50 else ("#ffa502" if ap > 40 else "#2ed573")
status_msg = (
    f"⚠ 51% attack is possible — attacker has majority hashrate"
    if ap > 50 else
    f"⚡ Attacker is approaching majority — {ap:.1f}% hashrate"
    if ap > 40 else
    f"✓ Honest nodes hold the majority — network is secure"
)

net_svg_col, net_stats_col = st.columns([1, 1.6], gap="medium")

with net_svg_col:
    st.markdown(
        '<div style="background:#0b1424;border:1px solid #182035;border-radius:18px;'
        'padding:18px;text-align:center;height:100%;">'
        + network_topology_svg(total_honest, attacker_nodes)
        + '</div>',
        unsafe_allow_html=True,
    )

with net_stats_col:
    st.markdown(f"""
<div style="background:#0b1424;border:1px solid #182035;border-radius:18px;
            padding:24px 28px;height:100%;">
  <div style="font-size:9.5px;font-weight:800;letter-spacing:3px;text-transform:uppercase;
              color:rgba(255,255,255,.28);margin-bottom:6px;">Network Hashrate Distribution</div>
  <div style="font-size:13px;color:{stat_color};font-weight:700;margin-bottom:20px;
              letter-spacing:.3px;">{status_msg}</div>

  <div class="net-stat-row">
    <div>
      <div class="nsr-label" style="color:rgba(0,212,255,.7);">🔷 Honest Network</div>
      <div class="nsr-bar" style="width:{hp:.0f}%;background:rgba(0,212,255,.4);max-width:200px;"></div>
    </div>
    <div class="nsr-val" style="color:#00d4ff;">{hp:.1f}%</div>
  </div>

  <div class="net-stat-row">
    <div>
      <div class="nsr-label" style="color:rgba(255,71,87,.7);">🔴 Attacker</div>
      <div class="nsr-bar" style="width:{ap:.0f}%;background:rgba(255,71,87,.4);max-width:200px;"></div>
    </div>
    <div class="nsr-val" style="color:#ff4757;">{ap:.1f}%</div>
  </div>

  <div class="net-stat-row">
    <div class="nsr-label" style="color:rgba(255,255,255,.28);">Total Nodes</div>
    <div class="nsr-val" style="color:rgba(255,255,255,.55);">{total_nodes}</div>
  </div>

  <div class="net-stat-row">
    <div class="nsr-label" style="color:rgba(255,255,255,.28);">Majority Threshold</div>
    <div class="nsr-val" style="color:rgba(255,255,255,.35);">50%</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# RUN BUTTON — centered, pill shape
# ═════════════════════════════════════════════════════════════════════════════
if ap > 50:
    btn_bg = "linear-gradient(135deg,#c0392b,#922b21)"
    btn_lbl = "▶  Run Simulation — Attack Likely to Succeed"
elif ap > 40:
    btn_bg = "linear-gradient(135deg,#d35400,#a04000)"
    btn_lbl = "▶  Run Simulation — Borderline Attack"
else:
    btn_bg = "linear-gradient(135deg,#1a7a3a,#145a2c)"
    btn_lbl = "▶  Run Simulation — Honest Majority"

st.markdown(f"""
<style>
div[data-testid="stButton"] > button {{
    background: {btn_bg} !important;
    color: white !important;
    box-shadow: 0 6px 28px rgba(0,0,0,.5) !important;
}}
</style>
""", unsafe_allow_html=True)

_, btn_col, _ = st.columns([1.4, 2, 1.4])
with btn_col:
    run_btn = st.button(btn_lbl, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# LIVE SIMULATION — auto-scroll + inline rendering
# ═════════════════════════════════════════════════════════════════════════════
if run_btn:
    st.session_state.baseline_result  = None
    st.session_state.protected_result = None
    st.session_state.last_run_mode    = run_mode

    # anchor + auto-scroll
    st.markdown('<div id="sim-anchor"></div>', unsafe_allow_html=True)
    components.html("""
    <script>
    setTimeout(function () {
        var a = window.parent.document.getElementById('sim-anchor');
        if (a) a.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 120);
    </script>
    """, height=0)

    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sec-lbl">Live Simulation</div>', unsafe_allow_html=True)

    # ── Baseline ─────────────────────────────────────────────────────────────
    if run_mode in ("Compare Both", "Baseline Only"):
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:10.5px;letter-spacing:4px;text-transform:uppercase;'
                'font-weight:800;color:#ff8591;padding-bottom:12px;'
                'border-bottom:1px solid #182035;margin-bottom:16px;">'
                '⛓ &nbsp;BASELINE — No Defense</div>',
                unsafe_allow_html=True,
            )
            prog_b = st.progress(0.0, text="Starting baseline...")
            chart_col_b, log_col_b = st.columns([1.55, 1], gap="medium")
            chart_ph_b = chart_col_b.empty()
            log_col_b.markdown(
                '<div style="font-size:9px;letter-spacing:2.5px;text-transform:uppercase;'
                'color:rgba(255,255,255,.25);margin-bottom:5px;font-weight:700;">Event Log</div>',
                unsafe_allow_html=True,
            )
            log_ph_b = log_col_b.empty()

        st.session_state.baseline_result = run_single(
            "baseline", prog_b, log_ph_b, chart_ph_b, anim_ms / 1000
        )
        prog_b.progress(1.0, text="✅  Baseline complete")

    # ── Protected ────────────────────────────────────────────────────────────
    if run_mode in ("Compare Both", "Protected Only"):
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:10.5px;letter-spacing:4px;text-transform:uppercase;'
                'font-weight:800;color:#7cf5a0;padding-bottom:12px;'
                'border-bottom:1px solid #182035;margin-bottom:16px;">'
                '🛡 &nbsp;PROTECTED — LPC + Safe Mode Defense</div>',
                unsafe_allow_html=True,
            )
            prog_p = st.progress(0.0, text="Starting protected run...")
            chart_col_p, log_col_p = st.columns([1.55, 1], gap="medium")
            chart_ph_p = chart_col_p.empty()
            log_col_p.markdown(
                '<div style="font-size:9px;letter-spacing:2.5px;text-transform:uppercase;'
                'color:rgba(255,255,255,.25);margin-bottom:5px;font-weight:700;">Event Log</div>',
                unsafe_allow_html=True,
            )
            log_ph_p = log_col_p.empty()

        st.session_state.protected_result = run_single(
            "protected", prog_p, log_ph_p, chart_ph_p, anim_ms / 1000
        )
        prog_p.progress(1.0, text="✅  Protected run complete")

    st.markdown(
        '<div style="text-align:center;padding:14px 0 0;font-size:10px;'
        'letter-spacing:2px;color:rgba(0,212,255,.4);">▼ RESULTS BELOW</div>',
        unsafe_allow_html=True,
    )


# ═════════════════════════════════════════════════════════════════════════════
# RESULTS BENTO
# ═════════════════════════════════════════════════════════════════════════════
baseline  = st.session_state.baseline_result
protected = st.session_state.protected_result

if baseline is not None or protected is not None:
    st.markdown("<div style='margin-top:32px;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sec-lbl">Results Dashboard</div>', unsafe_allow_html=True)

    any_r = baseline or protected
    b_ok  = baseline["attack_success"]  if baseline  else None
    p_ok  = protected["attack_success"] if protected else None
    rej   = protected["blocks_rejected"] if protected else "—"
    hr    = f"{any_r['attacker_hashrate']*100:.1f}%" if any_r else "—"
    total_b = any_r["total_blocks"] if any_r else "—"

    # ── Metric cards ──────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4, gap="medium")

    def mcard(col, label, val, cls, sub=""):
        col.markdown(
            f'<div class="mcard"><div class="mcard-label">{label}</div>'
            f'<div class="mcard-val {cls}">{val}</div>'
            f'<div class="mcard-sub">{sub}</div></div>',
            unsafe_allow_html=True,
        )

    mcard(m1, "Baseline — Attack",
          "SUCCEEDED" if b_ok else ("BLOCKED" if b_ok is False else "N/A"),
          "val-danger" if b_ok else "val-safe",
          "Attacker won" if b_ok else ("Honest chain won" if b_ok is False else ""))
    mcard(m2, "Protected — Attack",
          "SUCCEEDED" if p_ok else ("BLOCKED" if p_ok is False else "N/A"),
          "val-danger" if p_ok else "val-safe",
          "Defense bypassed" if p_ok else ("LPC / Safe Mode held" if p_ok is False else ""))
    mcard(m3, "Blocks Rejected",
          rej, "val-neutral", "by LPC defense" if rej != "—" else "")
    mcard(m4, "Attacker Hashrate", hr,
          "val-danger" if any_r and any_r["attacker_hashrate"] > .5 else
          ("val-warn" if any_r and any_r["attacker_hashrate"] > .4 else "val-neutral"),
          f"{total_b} blocks mined total")

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    # ── Comparison chart + chain growth ───────────────────────────────────────
    if baseline and protected:
        cl, cr = st.columns([1, 1.65], gap="medium")

        with cl:
            with st.container(border=True):
                st.markdown(
                    '<div style="font-size:9.5px;letter-spacing:3px;text-transform:uppercase;'
                    'color:rgba(0,212,255,.5);font-weight:800;margin-bottom:14px;">'
                    'Outcome Comparison</div>', unsafe_allow_html=True,
                )

                # build each outcome card
                def outcome_card(label, success, sub):
                    bg  = "rgba(255,71,87,.08)"  if success else "rgba(46,213,115,.07)"
                    bdr = "rgba(255,71,87,.35)"  if success else "rgba(46,213,115,.3)"
                    col = "#ff4757"              if success else "#2ed573"
                    txt = "SUCCEEDED"            if success else "BLOCKED"
                    ico = "⚠"                   if success else "🛡"
                    return (
                        f'<div style="flex:1;text-align:center;padding:18px 10px 14px;'
                        f'background:{bg};border:1px solid {bdr};border-radius:12px;">'
                        f'<div style="font-size:9px;letter-spacing:3px;text-transform:uppercase;'
                        f'color:rgba(255,255,255,.35);font-weight:700;margin-bottom:8px;">{label}</div>'
                        f'<div style="font-size:10px;margin-bottom:4px;">{ico}</div>'
                        f'<div style="font-size:26px;font-weight:900;color:{col};letter-spacing:1px;">{txt}</div>'
                        f'<div style="font-size:10px;color:rgba(255,255,255,.28);margin-top:5px;">{sub}</div>'
                        f'</div>'
                    )

                b_card = outcome_card(
                    "Baseline (No Defense)",
                    baseline["attack_success"],
                    "Attacker won" if baseline["attack_success"] else "Honest chain held"
                )
                p_card = outcome_card(
                    "Protected (LPC + Safe Mode)",
                    protected["attack_success"],
                    "Defense bypassed" if protected["attack_success"] else "Defense held"
                )
                st.markdown(
                    f'<div style="display:flex;gap:10px;margin-bottom:14px;">{b_card}{p_card}</div>',
                    unsafe_allow_html=True,
                )

                st.dataframe(
                    pd.DataFrame([
                        {"Metric": "Attack outcome",
                         "Baseline": "Succeeded" if baseline["attack_success"] else "Blocked",
                         "Protected": "Succeeded" if protected["attack_success"] else "Blocked"},
                        {"Metric": "Final chain length",
                         "Baseline": baseline["total_blocks"],
                         "Protected": protected["total_blocks"]},
                        {"Metric": "Blocks rejected by LPC",
                         "Baseline": 0,
                         "Protected": protected["blocks_rejected"]},
                        {"Metric": "Attacker hashrate",
                         "Baseline": f"{baseline['attacker_hashrate']*100:.1f}%",
                         "Protected": f"{protected['attacker_hashrate']*100:.1f}%"},
                    ]),
                    use_container_width=True, hide_index=True,
                )

        with cr:
            with st.container(border=True):
                st.markdown(
                    '<div style="font-size:9.5px;letter-spacing:3px;text-transform:uppercase;'
                    'color:rgba(0,212,255,.5);font-weight:800;margin-bottom:12px;">'
                    'Chain Growth — All Runs</div>', unsafe_allow_html=True,
                )
                fig_g = go.Figure()
                traces = [
                    ("Baseline – Honest",    baseline,  "#3b82f6", "solid"),
                    ("Baseline – Attacker",  baseline,  "#ef4444", "dash"),
                    ("Protected – Honest",   protected, "#2ed573", "solid"),
                    ("Protected – Attacker", protected, "#ffa502", "dot"),
                ]
                for lbl, res, col, dash in traces:
                    if res and res.get("chain_history"):
                        df = pd.DataFrame(res["chain_history"], columns=["step","honest","private"])
                        ycol = "honest" if "Honest" in lbl else "private"
                        fig_g.add_trace(go.Scatter(
                            x=df["step"], y=df[ycol], mode="lines",
                            name=lbl, line=dict(color=col, width=2, dash=dash),
                        ))
                fig_g.update_layout(
                    paper_bgcolor="#0b1424", plot_bgcolor="#060b14",
                    font_color="#6b7d99", height=340,
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis=dict(title="Step", gridcolor="#182035", color="#4a5568"),
                    yaxis=dict(title="Length", gridcolor="#182035", color="#4a5568"),
                    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10),
                                orientation="h", y=-0.2),
                )
                st.plotly_chart(fig_g, use_container_width=True, key="chain_both")

    elif any_r and any_r.get("chain_history"):
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:9.5px;letter-spacing:3px;text-transform:uppercase;'
                'color:rgba(0,212,255,.5);font-weight:800;margin-bottom:12px;">'
                'Chain Growth</div>', unsafe_allow_html=True,
            )
            df = pd.DataFrame(any_r["chain_history"], columns=["step","honest","private"])
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["step"], y=df["honest"], mode="lines",
                                     name="Honest", line=dict(color="#00d4ff", width=2.5),
                                     fill="tozeroy", fillcolor="rgba(0,212,255,.07)"))
            fig.add_trace(go.Scatter(x=df["step"], y=df["private"], mode="lines",
                                     name="Attacker", line=dict(color="#ff4757", width=2.5, dash="dash"),
                                     fill="tozeroy", fillcolor="rgba(255,71,87,.07)"))
            fig.update_layout(paper_bgcolor="#0b1424", plot_bgcolor="#060b14",
                              font_color="#6b7d99", height=290,
                              margin=dict(l=10,r=10,t=10,b=10),
                              xaxis=dict(gridcolor="#182035"),
                              yaxis=dict(gridcolor="#182035"),
                              legend=dict(bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig, use_container_width=True, key="chain_single")

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    # ── Miner stats + Chain viz ───────────────────────────────────────────────
    active = protected if protected else baseline
    mc, cc = st.columns([1, 1.4], gap="medium")

    with mc:
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:9.5px;letter-spacing:3px;text-transform:uppercase;'
                'color:rgba(0,212,255,.5);font-weight:800;margin-bottom:12px;">'
                'Miner Statistics</div>', unsafe_allow_html=True,
            )
            if active:
                rows = [{"Miner": m["miner_id"], "Nodes": m["num_nodes"],
                         "Hashrate": f"{m['hashrate']*100:.1f}%",
                         "Blocks Mined": m["blocks_mined"]}
                        for m in active["honest_miners"]]
                rows.append({
                    "Miner": "Attacker",
                    "Nodes": active["attacker_info"]["num_nodes"],
                    "Hashrate": f"{active['attacker_info']['hashrate']*100:.1f}%",
                    "Blocks Mined": active["attacker_info"]["blocks_mined"],
                })
                df_m = pd.DataFrame(rows)

                # horizontal bar chart — avoids the "100% attacker" pie problem
                cmap = {r["Miner"]: ("#ff4757" if r["Miner"] == "Attacker" else "#00d4ff")
                        for r in rows}
                fig_bar = px.bar(
                    df_m, x="Blocks Mined", y="Miner",
                    orientation="h", color="Miner",
                    color_discrete_map=cmap,
                    text="Blocks Mined",
                )
                fig_bar.update_traces(textposition="outside", textfont_size=11)
                fig_bar.update_layout(
                    paper_bgcolor="#0b1424", plot_bgcolor="#060b14",
                    font_color="#6b7d99", showlegend=False,
                    height=220, margin=dict(l=10, r=30, t=10, b=10),
                    xaxis=dict(gridcolor="#182035", title=""),
                    yaxis=dict(title="", categoryorder="total ascending"),
                )
                st.plotly_chart(fig_bar, use_container_width=True, key="bar_miners")
                st.dataframe(df_m, use_container_width=True, hide_index=True)

    with cc:
        with st.container(border=True):
            st.markdown(
                '<div style="font-size:9.5px;letter-spacing:3px;text-transform:uppercase;'
                'color:rgba(0,212,255,.5);font-weight:800;margin-bottom:12px;">'
                'Final Chain Visualization</div>', unsafe_allow_html=True,
            )

            def chain_viz(res, lbl):
                chain = res["chain"].chain
                df = pd.DataFrame([{
                    "Block": b.index, "Miner": b.miner_id,
                    "Hash": b.hash[:12] + "…",
                    "Prev": b.previous_hash[:12] + "…",
                } for b in chain])
                palette = px.colors.qualitative.Set2
                cmap = {}
                for i, m in enumerate(df["Miner"].unique()):
                    cmap[m] = "#ff4757" if m == "Attacker" else (
                        "#4a5568" if m == "system" else palette[i % len(palette)])
                fig = px.bar(df, x="Block", y=[1]*len(df), color="Miner",
                             color_discrete_map=cmap,
                             hover_data=["Hash", "Prev"])
                fig.update_layout(
                    yaxis=dict(showticklabels=False, title=""),
                    height=155, paper_bgcolor="#0b1424", plot_bgcolor="#060b14",
                    font_color="#6b7d99",
                    legend=dict(font=dict(size=10), bgcolor="rgba(0,0,0,0)",
                                orientation="h", y=1.3),
                    margin=dict(l=5,r=5,t=44,b=5),
                    title=dict(text=lbl, font=dict(size=10.5, color="#6b7d99")),
                    bargap=0.06,
                )
                st.plotly_chart(fig, use_container_width=True, key=f"cv_{lbl[:8]}")

            if baseline:
                chain_viz(baseline, "Baseline — red blocks = attacker mined")
            if protected:
                chain_viz(protected, "Protected — fewer/no attacker blocks")

    st.markdown("<div style='margin-top:22px;'></div>", unsafe_allow_html=True)

    # ── Logs + Downloads ──────────────────────────────────────────────────────
    st.markdown('<div class="sec-lbl">Event Logs &amp; Downloads</div>',
                unsafe_allow_html=True)

    pairs = [(l, r) for l, r in [("Baseline", baseline), ("Protected", protected)] if r]
    log_cols = st.columns(len(pairs), gap="medium")

    for idx, (label, result) in enumerate(pairs):
        with log_cols[idx]:
            with st.container(border=True):
                st.markdown(
                    f'<div style="font-size:9.5px;letter-spacing:3px;text-transform:uppercase;'
                    f'color:rgba(0,212,255,.5);font-weight:800;margin-bottom:10px;">'
                    f'{label} Log</div>', unsafe_allow_html=True,
                )
                log_html = "".join(
                    f'<div class="ev '
                    + ("ev-attack"  if ("ATTACK" in l.upper() or "[!]" in l.upper() or "PRIVATE" in l.upper()) else
                       "ev-defense" if ("DEFENSE" in l.upper() or "LPC" in l.upper() or "SAFE" in l.upper() or "REJECTED" in l.upper()) else
                       "ev-result"  if ("RESULT" in l.upper() or "SUCCESS" in l.upper() or "FAILED" in l.upper()) else
                       "ev-mine"    if ("MINED" in l.upper() or "BLOCK" in l.upper()) else
                       "ev-info")
                    + f'">{l.replace("<","&lt;").replace(">","&gt;")}</div>'
                    for l in result["log"]
                )
                st.markdown(f'<div class="elog">{log_html}</div>',
                            unsafe_allow_html=True)
                st.download_button(
                    f"⬇  Download {label} Log (CSV)",
                    pd.DataFrame({"event": result["log"]}).to_csv(index=False),
                    file_name=f"{label.lower()}_log.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key=f"dl_{label}",
                )

    st.markdown("<div style='padding-bottom:48px;'></div>", unsafe_allow_html=True)

st.markdown("<div style='padding-bottom:48px;'></div>", unsafe_allow_html=True)
