/* ==========================================================================
   💎 STAKE 2011 v5.0 ULTRA • CLIENT ENGINE (12 GAMES + WEB AUDIO + PARTICLES + LIVE PVP)
   ========================================================================== */

const STATE = {
    token: localStorage.getItem("stake2011_token") || null,
    user: null,
    authMode: "login",
    selectedAvatar: "neon_wolf",
    activeTab: "apple",
    soundEnabled: true,
    seenPvpIds: new Set(),
    incomingPvpChallenge: null,

    apple: {
        active: false,
        currentLevel: 0,
        levelsConfig: [
            { level: 1, multiplier: 1.23 }, { level: 2, multiplier: 1.54 },
            { level: 3, multiplier: 1.93 }, { level: 4, multiplier: 2.85 },
            { level: 5, multiplier: 4.75 }, { level: 6, multiplier: 9.50 },
            { level: 7, multiplier: 18.00 }, { level: 8, multiplier: 45.00 },
        ],
    },
    mines: { active: false, minesCount: 5, opened: new Set() },
    plinko: { risk: "medium", buckets: {}, balls: [] },
    crash: { running: false, cashedOut: false, bet: 500, crashPoint: 1.0, currentMult: 1.0, autoCashout: 2.0, startTime: 0 },
    wheel: { spinning: false, currentRotation: 0, segments: [] },
    tower: {
        active: false,
        level: 0,
        levelsConfig: [
            { level: 1, multiplier: 1.42 }, { level: 2, multiplier: 2.05 },
            { level: 3, multiplier: 2.98 }, { level: 4, multiplier: 4.35 },
            { level: 5, multiplier: 6.40 }, { level: 6, multiplier: 14.50 },
            { level: 7, multiplier: 32.00 }, { level: 8, multiplier: 75.00 },
        ],
    },
    dice: { condition: "over", target: 50 },
    coinflip: { active: false, streak: 0 },
    keno: { picks: new Set() },
    fight: { fighters: [], pickedSlot: 1, tactic: "head", busy: false },
    pvp: { mode: "cards", tactic: "head" },
};

/* ==========================================================================
   🔊 WEB AUDIO API SYNTHESIZER (НАСТОЯЩИЕ ЗВУКИ КАЗИНО БЕЗ ВНЕШНИХ MP3!)
   ========================================================================== */
const SFX = {
    ctx: null,
    init() {
        if (!this.ctx) {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (AudioCtx) this.ctx = new AudioCtx();
        }
    },
    playTone(freq, type = "sine", duration = 0.12, vol = 0.12) {
        if (!STATE.soundEnabled) return;
        try {
            this.init();
            if (!this.ctx) return;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
            gain.gain.setValueAtTime(vol, this.ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start();
            osc.stop(this.ctx.currentTime + duration);
        } catch (_) {}
    },
    click() { this.playTone(520, "triangle", 0.06, 0.08); },
    gem(step = 1) { this.playTone(580 + step * 65, "sine", 0.18, 0.14); },
    win() {
        [523, 659, 783, 1046].forEach((f, i) => setTimeout(() => this.playTone(f, "triangle", 0.22, 0.16), i * 80));
    },
    boom() { this.playTone(110, "sawtooth", 0.38, 0.2); },
    alert() {
        [660, 880, 660, 880].forEach((f, i) => setTimeout(() => this.playTone(f, "square", 0.12, 0.1), i * 110));
    },
};

/* ==========================================================================
   ✨ PARTICLE ENGINE (САЛЮТ ЗОЛОТЫХ МОНЕТ И НЕОНОВЫХ ИСКР НА CANVAS)
   ========================================================================== */
const FX = {
    particles: [],
    burst(x, y, color = "#00e701", count = 38) {
        for (let i = 0; i < count; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = 2 + Math.random() * 7;
            this.particles.push({
                x, y,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed - 2,
                radius: 3 + Math.random() * 4,
                color,
                alpha: 1.0,
            });
        }
    },
    celebrateWin() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        this.burst(w * 0.35, h * 0.4, "#00e701", 40);
        this.burst(w * 0.65, h * 0.4, "#facc15", 40);
        this.burst(w * 0.5, h * 0.3, "#38bdf8", 35);
    },
};

function startParticleLoop() {
    const canvas = document.getElementById("fxParticlesCanvas");
    const ctx = canvas.getContext("2d");
    const resize = () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    };
    window.addEventListener("resize", resize);
    resize();

    const loop = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        for (let i = FX.particles.length - 1; i >= 0; i--) {
            const p = FX.particles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.18;
            p.alpha -= 0.018;
            if (p.alpha <= 0) {
                FX.particles.splice(i, 1);
                continue;
            }
            ctx.save();
            ctx.globalAlpha = Math.max(0, p.alpha);
            ctx.fillStyle = p.color;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
        requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
}

/* ==========================================================================
   🎨 КАСТОМНЫЕ SVG-ВЕКТОРЫ (БЕЗ ДЕШЁВЫХ СМАЙЛИКОВ!)
   ========================================================================== */
const SVG_VECTORS = {
    ripeApple: `
        <svg viewBox="0 0 64 64" width="32" height="32">
            <defs><radialGradient id="apG" cx="35%" cy="30%" r="70%"><stop offset="0%" stop-color="#86efac"/><stop offset="50%" stop-color="#00e701"/><stop offset="100%" stop-color="#047857"/></radialGradient></defs>
            <path d="M32 14 C35 6, 44 5, 47 9 C42 13, 36 14, 32 14 Z" fill="#4ade80"/>
            <path d="M32 16 C20 14, 10 24, 12 38 C14 50, 23 58, 32 55 C41 58, 50 50, 52 38 C54 24, 44 14, 32 16 Z" fill="url(#apG)" stroke="#bbf7d0" stroke-width="1.5"/>
        </svg>
    `,
    rottenApple: `
        <svg viewBox="0 0 64 64" width="32" height="32">
            <path d="M22 16 C28 14, 36 14, 42 16 C35 23, 35 41, 43 50 C36 55, 28 55, 21 50 C29 41, 29 23, 22 16 Z" fill="#ff2a5f" stroke="#fda4af" stroke-width="1.5"/>
            <path d="M16 20 L48 48 M48 20 L16 48" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
    `,
    gem: `
        <svg viewBox="0 0 64 64" width="38" height="38">
            <defs><linearGradient id="gmG" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#a7f3d0"/><stop offset="50%" stop-color="#00e701"/><stop offset="100%" stop-color="#065f46"/></linearGradient></defs>
            <polygon points="18,10 46,10 58,24 32,56 6,24" fill="url(#gmG)" stroke="#ffffff" stroke-width="1.8"/>
            <polyline points="6,24 58,24" stroke="rgba(255,255,255,0.55)" stroke-width="1.4"/>
        </svg>
    `,
    bomb: `
        <svg viewBox="0 0 64 64" width="38" height="38">
            <circle cx="30" cy="36" r="17" fill="#1e293b" stroke="#ff2a5f" stroke-width="2.5"/>
            <path d="M38 20 Q46 10 54 14" fill="none" stroke="#facc15" stroke-width="3"/>
            <circle cx="54" cy="14" r="4.5" fill="#ff2a5f"/>
        </svg>
    `,
    dragonEgg: `
        <svg viewBox="0 0 64 64" width="34" height="34">
            <ellipse cx="32" cy="34" rx="16" ry="22" fill="#facc15" stroke="#fef08a" stroke-width="2"/>
            <path d="M22 28 L32 22 L42 28 L32 36 Z" fill="#f97316"/>
        </svg>
    `,
    skull: `
        <svg viewBox="0 0 64 64" width="34" height="34">
            <circle cx="32" cy="28" r="16" fill="#ff2a5f"/>
            <rect x="24" y="38" width="16" height="12" rx="3" fill="#ff2a5f"/>
            <circle cx="26" cy="28" r="4" fill="#0b1620"/><circle cx="38" cy="28" r="4" fill="#0b1620"/>
        </svg>
    `,
    slotIcons: {
        seven: `<svg viewBox="0 0 64 64" width="60" height="60"><text x="50%" y="56%" dominant-baseline="middle" text-anchor="middle" fill="#ff2a5f" stroke="#fff" stroke-width="1.5" font-size="46" font-weight="900">777</text></svg>`,
        diamond: `<svg viewBox="0 0 64 64" width="56" height="56"><polygon points="32,6 56,24 32,58 8,24" fill="#38bdf8" stroke="#e0f2fe" stroke-width="2"/></svg>`,
        crown: `<svg viewBox="0 0 64 64" width="56" height="56"><polygon points="8,48 14,18 26,32 32,14 38,32 50,18 56,48" fill="#facc15" stroke="#fef08a" stroke-width="2"/></svg>`,
        flame: `<svg viewBox="0 0 64 64" width="56" height="56"><path d="M32 6 C46 22, 52 34, 44 48 C38 56, 26 56, 20 48 C12 34, 22 22, 32 6 Z" fill="#f97316"/></svg>`,
        cherry: `<svg viewBox="0 0 64 64" width="56" height="56"><circle cx="22" cy="42" r="10" fill="#ef4444"/><circle cx="42" cy="42" r="10" fill="#ef4444"/><path d="M22 32 L34 12 L42 32" stroke="#00e701" stroke-width="3" fill="none"/></svg>`,
        bell: `<svg viewBox="0 0 64 64" width="56" height="56"><path d="M32 10 C20 10, 14 22, 14 38 L10 46 L54 46 L50 38 C50 22, 44 10, 32 10 Z" fill="#eab308"/></svg>`,
        clover: `<svg viewBox="0 0 64 64" width="56" height="56"><circle cx="24" cy="24" r="10" fill="#00e701"/><circle cx="40" cy="24" r="10" fill="#00e701"/><circle cx="24" cy="40" r="10" fill="#00e701"/><circle cx="40" cy="40" r="10" fill="#00e701"/></svg>`,
    },
};

// Генератор векторных неоновых аватарок и портретов бойцов 2011 (без эмодзи!)
function getAvatarSvg(presetName) {
    const map = {
        neon_wolf: ["#00e701", "#052e16", "WOLF"],
        cyber_skull: ["#06b6d4", "#083344", "CYBR"],
        gold_crown: ["#facc15", "#422006", "KING"],
        emerald_viper: ["#10b981", "#064e3b", "VIPR"],
        crimson_samurai: ["#ff2a5f", "#4c0519", "SMR"],
        plasma_tiger: ["#f97316", "#431407", "TIGR"],
        diamond_king: ["#38bdf8", "#0c4a6e", "DMND"],
        shadow_ninja: ["#a855f7", "#3b0764", "SHDW"],
        laser_eagle: ["#3b82f6", "#172554", "EAGL"],
        toxic_rhino: ["#84cc16", "#1a2e05", "RHNO"],
    };
    const [stroke, bg, code] = map[presetName] || map.neon_wolf;
    return `
        <svg viewBox="0 0 44 44" width="100%" height="100%">
            <polygon points="22,2 40,12 40,32 22,42 4,32 4,12" fill="${bg}" stroke="${stroke}" stroke-width="2.4"/>
            <text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle" fill="#fff" font-size="10" font-weight="900">${code}</text>
        </svg>
    `;
}

function getFighterPortraitSvg(fighter) {
    const c = fighter.color || "#00e701";
    const bg = fighter.accent || "#064e3b";
    const code = fighter.code || fighter.name.slice(0, 3).toUpperCase();
    return `
        <svg viewBox="0 0 90 90" width="100%" height="100%">
            <defs>
                <radialGradient id="fg_${fighter.key}" cx="50%" cy="40%" r="60%">
                    <stop offset="0%" stop-color="${c}" stop-opacity="0.45"/>
                    <stop offset="100%" stop-color="${bg}" stop-opacity="0.95"/>
                </radialGradient>
            </defs>
            <circle cx="45" cy="45" r="42" fill="url(#fg_${fighter.key})" stroke="${c}" stroke-width="3"/>
            <polygon points="45,10 76,27 76,63 45,80 14,63 14,27" fill="none" stroke="rgba(255,255,255,0.22)" stroke-width="1.5"/>
            <text x="50%" y="48%" dominant-baseline="middle" text-anchor="middle" fill="#ffffff" font-size="22" font-weight="900" letter-spacing="1">${code}</text>
            <text x="50%" y="72%" dominant-baseline="middle" text-anchor="middle" fill="${c}" font-size="10" font-weight="800">⚡${fighter.power_score}</text>
        </svg>
    `;
}

/* ==========================================================================
   🛠 УТИЛИТЫ API И БАЛАНСА
   ========================================================================== */
function showToast(message, isError = false) {
    const container = document.getElementById("toastContainer");
    const item = document.createElement("div");
    item.className = `toast-item ${isError ? "error" : ""}`;
    item.innerHTML = message;
    container.appendChild(item);
    setTimeout(() => {
        item.style.opacity = "0";
        setTimeout(() => item.remove(), 250);
    }, 3400);
}

async function apiCall(path, method = "GET", body = null) {
    const headers = { "Content-Type": "application/json" };
    if (STATE.token) headers["Authorization"] = `Bearer ${STATE.token}`;
    const opts = { method, headers, credentials: "include" };
    if (body !== null) opts.body = JSON.stringify(body);
    const res = await fetch(path, opts);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || "Ошибка сервера");
    return data;
}

function updateTopBalance(newBalance, isWin = false) {
    if (STATE.user) STATE.user.balance = newBalance;
    const el = document.getElementById("topBalanceValue");
    el.textContent = Number(newBalance).toLocaleString("ru-RU");
    if (isWin) {
        SFX.win();
        FX.celebrateWin();
        el.classList.remove("pulse-win");
        void el.offsetWidth;
        el.classList.add("pulse-win");
        setTimeout(() => el.classList.remove("pulse-win"), 650);
    }
}

function triggerScreenShake(id = "mainStage") {
    SFX.boom();
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.remove("screen-shake");
    void el.offsetWidth;
    el.classList.add("screen-shake");
}

/* ==========================================================================
   🔐 АВТОРИЗАЦИЯ И СЕССИЯ
   ========================================================================== */
function initAuthModal() {
    const grid = document.getElementById("avatarPickerGrid");
    const presets = [
        "neon_wolf", "cyber_skull", "gold_crown", "emerald_viper", "crimson_samurai",
        "plasma_tiger", "diamond_king", "shadow_ninja", "laser_eagle", "toxic_rhino",
    ];
    grid.innerHTML = "";
    presets.forEach((p) => {
        const d = document.createElement("div");
        d.className = `avatar-pick-item ${p === STATE.selectedAvatar ? "selected" : ""}`;
        d.innerHTML = getAvatarSvg(p);
        d.onclick = () => {
            STATE.selectedAvatar = p;
            document.querySelectorAll(".avatar-pick-item").forEach((el) => el.classList.remove("selected"));
            d.classList.add("selected");
        };
        grid.appendChild(d);
    });

    const tabL = document.getElementById("tabLoginBtn");
    const tabR = document.getElementById("tabRegisterBtn");
    const extra = document.getElementById("registerExtraFields");

    tabL.onclick = () => {
        STATE.authMode = "login";
        tabL.classList.add("active");
        tabR.classList.remove("active");
        extra.classList.add("hidden");
    };
    tabR.onclick = () => {
        STATE.authMode = "register";
        tabR.classList.add("active");
        tabL.classList.remove("active");
        extra.classList.remove("hidden");
    };

    document.getElementById("authForm").onsubmit = async (e) => {
        e.preventDefault();
        const errEl = document.getElementById("authErrorMsg");
        errEl.classList.add("hidden");
        const username = document.getElementById("authUsername").value.trim();
        const password = document.getElementById("authPassword").value.trim();
        const display_name = document.getElementById("authDisplayName").value.trim() || username;

        try {
            const url = STATE.authMode === "login" ? "/api/auth/login" : "/api/auth/register";
            const res = await apiCall(url, "POST", { username, password, display_name, avatar: STATE.selectedAvatar });
            STATE.token = res.token;
            localStorage.setItem("stake2011_token", res.token);
            applyUser(res.user);
            document.getElementById("authModalBackdrop").classList.add("hidden");
            showToast(`🔥 Салам, ${res.user.display_name}! Удачной игры!`);
            syncClubHub();
        } catch (err) {
            errEl.textContent = err.message;
            errEl.classList.remove("hidden");
        }
    };

    document.getElementById("logoutBtn").onclick = async () => {
        await apiCall("/api/auth/logout", "POST").catch(() => {});
        localStorage.removeItem("stake2011_token");
        STATE.token = null;
        STATE.user = null;
        document.getElementById("authModalBackdrop").classList.remove("hidden");
    };
}

function applyUser(u) {
    STATE.user = u;
    updateTopBalance(u.balance, false);
    document.getElementById("topUserName").textContent = u.display_name;
    document.getElementById("topUserAvatar").innerHTML = getAvatarSvg(u.avatar);
    const vipEl = document.getElementById("topUserVip");
    vipEl.textContent = u.vip_title || "BRONZE";
    vipEl.style.color = u.vip_color || "#00e701";

    document.getElementById("topAdminBtn").classList.toggle("hidden", !u.is_admin);
    document.getElementById("sidebarAdminBtn").classList.toggle("hidden", !u.is_admin);
}

async function checkSession() {
    try {
        const res = await apiCall("/api/auth/me", "GET");
        applyUser(res.user);
        document.getElementById("authModalBackdrop").classList.add("hidden");
    } catch (_) {
        document.getElementById("authModalBackdrop").classList.remove("hidden");
    }
}

/* ==========================================================================
   🍏 1. APPLE OF FORTUNE
   ========================================================================== */
function renderAppleTower() {
    const grid = document.getElementById("appleTowerGrid");
    grid.innerHTML = "";
    STATE.apple.levelsConfig.forEach((cfg, idx) => {
        const row = document.createElement("div");
        row.className = `apple-floor-row ${STATE.apple.active && idx === STATE.apple.currentLevel ? "active-floor" : ""}`;
        row.id = `appleFloor_${idx}`;
        row.innerHTML = `<div class="floor-mult-badge">${cfg.multiplier.toFixed(2)}x</div>`;
        for (let c = 0; c < 5; c++) {
            const btn = document.createElement("button");
            btn.className = "apple-cell-btn";
            btn.id = `appleCell_${idx}_${c}`;
            btn.onclick = () => pickAppleCell(idx, c);
            row.appendChild(btn);
        }
        grid.appendChild(row);
    });
}

async function pickAppleCell(lvlIdx, col) {
    if (!STATE.apple.active || lvlIdx !== STATE.apple.currentLevel) return;
    SFX.click();
    try {
        const res = await apiCall("/api/games/apple/pick", "POST", { col });
        if (res.status === "boom") {
            STATE.apple.active = false;
            res.full_board.forEach((rLayout, l) => {
                for (let c = 0; c < 5; c++) {
                    const b = document.getElementById(`appleCell_${l}_${c}`);
                    if (!b) continue;
                    b.innerHTML = rLayout[c] === "good" ? SVG_VECTORS.ripeApple : SVG_VECTORS.rottenApple;
                    if (l === res.level && c === col) b.classList.add("revealed-rotten");
                    else b.classList.add("dimmed-cell");
                }
            });
            triggerScreenShake();
            updateTopBalance(res.balance, false);
            toggleAppleButtons(false, 0, 1.0, 0);
            if (res.cashback_triggered) showToast("🎁 Начислен спасательный кэшбэк: +1,000$!");
            syncClubHub();
            return;
        }

        SFX.gem(lvlIdx + 1);
        for (let c = 0; c < 5; c++) {
            const b = document.getElementById(`appleCell_${res.level}_${c}`);
            if (!b) continue;
            b.innerHTML = res.row_reveal[c] === "good" ? SVG_VECTORS.ripeApple : SVG_VECTORS.rottenApple;
            if (c === col) b.classList.add("revealed-good");
            else b.classList.add("dimmed-cell");
        }

        if (res.status === "max_win") {
            STATE.apple.active = false;
            updateTopBalance(res.balance, true);
            toggleAppleButtons(false, 8, res.multiplier, res.payout);
            showToast(`🏆 ПРОЙДЕНЫ ВСЕ 8 ЭТАЖЕЙ ЯБЛОЧЕК! +${res.payout}$!`);
            syncClubHub();
            return;
        }

        STATE.apple.currentLevel = res.next_level;
        toggleAppleButtons(true, res.next_level, res.multiplier, res.cashout_value);
    } catch (err) {
        showToast(err.message, true);
    }
}

function toggleAppleButtons(active, floor, mult, cashVal) {
    document.getElementById("appleCurrentFloorText").textContent = `${floor} / 8`;
    document.getElementById("appleCurrentMultText").textContent = `${mult.toFixed(2)}x`;
    document.getElementById("appleCashoutAmountText").textContent = `${cashVal} $`;
    document.getElementById("appleBtnCashoutVal").textContent = `${cashVal}$`;

    document.getElementById("appleStartBtn").classList.toggle("hidden", active);
    document.getElementById("appleCashoutBtn").classList.toggle("hidden", !(active && floor > 0));
    document.getElementById("appleRandomPickBtn").classList.toggle("hidden", !active);

    document.querySelectorAll(".apple-floor-row").forEach((r, i) => {
        r.classList.toggle("active-floor", active && i === floor);
    });
}

function initAppleGame() {
    renderAppleTower();
    document.getElementById("appleStartBtn").onclick = async () => {
        const bet = parseInt(document.getElementById("appleBetInput").value, 10) || 100;
        try {
            const res = await apiCall("/api/games/apple/start", "POST", { bet });
            STATE.apple.active = true;
            STATE.apple.currentLevel = 0;
            renderAppleTower();
            updateTopBalance(res.balance);
            toggleAppleButtons(true, 0, 1.0, bet);
        } catch (err) {
            showToast(err.message, true);
        }
    };
    document.getElementById("appleCashoutBtn").onclick = async () => {
        try {
            const res = await apiCall("/api/games/apple/cashout", "POST");
            STATE.apple.active = false;
            updateTopBalance(res.balance, true);
            toggleAppleButtons(false, 0, 1.0, 0);
            showToast(`🍏 Выведено +${res.payout}$ (${res.multiplier}x)!`);
            syncClubHub();
        } catch (err) {
            showToast(err.message, true);
        }
    };
    document.getElementById("appleRandomPickBtn").onclick = () => {
        if (STATE.apple.active) pickAppleCell(STATE.apple.currentLevel, Math.floor(Math.random() * 5));
    };
}

/* ==========================================================================
   💣 2. STAKE MINES 5x5
   ========================================================================== */
function renderMinesGrid() {
    const grid = document.getElementById("minesGrid5x5");
    grid.innerHTML = "";
    for (let i = 0; i < 25; i++) {
        const btn = document.createElement("button");
        btn.className = "mine-tile";
        btn.id = `mineTile_${i}`;
        btn.onclick = () => clickMineTile(i);
        grid.appendChild(btn);
    }
}

async function clickMineTile(idx) {
    if (!STATE.mines.active || STATE.mines.opened.has(idx)) return;
    try {
        const res = await apiCall("/api/games/mines/click", "POST", { cell_index: idx });
        if (res.status === "boom") {
            STATE.mines.active = false;
            const bSet = new Set(res.bombs);
            for (let i = 0; i < 25; i++) {
                const t = document.getElementById(`mineTile_${i}`);
                if (!t) continue;
                t.classList.add("opened");
                if (i === res.exploded_index) {
                    t.classList.add("bomb-tile");
                    t.innerHTML = SVG_VECTORS.bomb;
                } else if (bSet.has(i)) {
                    t.classList.add("bomb-tile", "unopened-reveal");
                    t.innerHTML = SVG_VECTORS.bomb;
                }
            }
            triggerScreenShake("minesArenaBox");
            updateTopBalance(res.balance, false);
            toggleMinesUI(false, 0, 1.0, 1.2, 0);
            if (res.cashback_triggered) showToast("🎁 Баланс упал ниже 100$ — начислен кэшбэк 1,000$!");
            syncClubHub();
            return;
        }

        STATE.mines.opened.add(idx);
        SFX.gem(res.opened_count);
        const tile = document.getElementById(`mineTile_${idx}`);
        if (tile) {
            tile.classList.add("opened", "gem-tile");
            tile.innerHTML = SVG_VECTORS.gem;
        }

        if (res.status === "max_win") {
            STATE.mines.active = false;
            updateTopBalance(res.balance, true);
            toggleMinesUI(false, 0, 1.0, 1.2, 0);
            showToast(`💎 ВСЕ КРИСТАЛЛЫ ОТКРЫТЫ! +${res.payout}$!`);
            syncClubHub();
            return;
        }

        toggleMinesUI(true, res.opened_count, res.multiplier, res.next_multiplier, res.cashout_value);
    } catch (err) {
        showToast(err.message, true);
    }
}

function toggleMinesUI(active, count, mult, nextM, cashVal) {
    document.getElementById("minesOpenedCount").textContent = count;
    document.getElementById("minesCurrentMult").textContent = `${mult.toFixed(2)}x`;
    document.getElementById("minesNextMult").textContent = `${nextM.toFixed(2)}x`;
    document.getElementById("minesCashoutVal").textContent = `${cashVal}$`;

    document.getElementById("minesStartBtn").classList.toggle("hidden", active);
    document.getElementById("minesCashoutBtn").classList.toggle("hidden", !(active && count > 0));
    document.getElementById("minesRandomBtn").classList.toggle("hidden", !active);
}

function initMinesGame() {
    renderMinesGrid();
    document.querySelectorAll("#minesCountSelector .sel-chip").forEach((btn) => {
        btn.onclick = () => {
            if (STATE.mines.active) return;
            STATE.mines.minesCount = parseInt(btn.dataset.mines, 10);
            document.querySelectorAll("#minesCountSelector .sel-chip").forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
        };
    });

    document.getElementById("minesStartBtn").onclick = async () => {
        const bet = parseInt(document.getElementById("minesBetInput").value, 10) || 100;
        try {
            const res = await apiCall("/api/games/mines/start", "POST", { bet, mines_count: STATE.mines.minesCount });
            STATE.mines.active = true;
            STATE.mines.opened.clear();
            renderMinesGrid();
            updateTopBalance(res.balance);
            toggleMinesUI(true, 0, 1.0, res.next_multiplier, bet);
        } catch (err) {
            showToast(err.message, true);
        }
    };

    document.getElementById("minesCashoutBtn").onclick = async () => {
        try {
            const res = await apiCall("/api/games/mines/cashout", "POST");
            STATE.mines.active = false;
            const bSet = new Set(res.bombs);
            for (let i = 0; i < 25; i++) {
                const t = document.getElementById(`mineTile_${i}`);
                if (t && bSet.has(i)) {
                    t.classList.add("bomb-tile", "unopened-reveal");
                    t.innerHTML = SVG_VECTORS.bomb;
                }
            }
            updateTopBalance(res.balance, true);
            toggleMinesUI(false, 0, 1.0, 1.2, 0);
            showToast(`💎 Кэшаут в Минах: +${res.payout}$ (${res.multiplier}x)!`);
            syncClubHub();
        } catch (err) {
            showToast(err.message, true);
        }
    };

    document.getElementById("minesRandomBtn").onclick = () => {
        if (!STATE.mines.active) return;
        const closed = [];
        for (let i = 0; i < 25; i++) if (!STATE.mines.opened.has(i)) closed.push(i);
        if (closed.length) clickMineTile(closed[Math.floor(Math.random() * closed.length)]);
    };
}

/* ==========================================================================
   🟣 3. PLINKO PHYSICS (ПИРАМИДА ШАРИКОВ НА CANVAS)
   ========================================================================== */
function renderPlinkoBucketsUI() {
    const row = document.getElementById("plinkoBucketsRow");
    const list = STATE.plinko.buckets[STATE.plinko.risk] || [22, 7, 3, 1.5, 0.9, 0.4, 0.2, 0.4, 0.9, 1.5, 3, 7, 22];
    row.innerHTML = "";
    list.forEach((m, i) => {
        const b = document.createElement("div");
        b.className = "plinko-bucket";
        b.id = `plinkoBucket_${i}`;
        b.textContent = `${m}x`;
        if (m >= 10) b.style.borderColor = "#ff2a5f";
        else if (m >= 2) b.style.borderColor = "#facc15";
        row.appendChild(b);
    });
}

function initPlinkoGame() {
    const canvas = document.getElementById("plinkoCanvas");
    const ctx = canvas.getContext("2d");
    const rows = 12;

    const drawLoop = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const startY = 36;
        const gapY = (canvas.height - 65) / rows;
        const gapX = 44;

        // Рисуем пирамиду неоновых штырьков
        for (let r = 0; r < rows; r++) {
            const pinsInRow = r + 3;
            const rowWidth = (pinsInRow - 1) * gapX;
            const startX = (canvas.width - rowWidth) / 2;
            for (let c = 0; c < pinsInRow; c++) {
                const px = startX + c * gapX;
                const py = startY + r * gapY;
                ctx.fillStyle = "#475569";
                ctx.beginPath();
                ctx.arc(px, py, 4.5, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Двигаем падающие шарики по серверному пути
        for (let i = STATE.plinko.balls.length - 1; i >= 0; i--) {
            const ball = STATE.plinko.balls[i];
            ball.progress += 0.16;
            const stepIdx = Math.floor(ball.progress);
            const frac = ball.progress - stepIdx;

            if (stepIdx >= rows) {
                const bucketEl = document.getElementById(`plinkoBucket_${ball.bucketIndex}`);
                if (bucketEl) {
                    bucketEl.classList.add("hit-pulse");
                    setTimeout(() => bucketEl.classList.remove("hit-pulse"), 350);
                }
                updateTopBalance(ball.finalBalance, ball.isWin);
                if (ball.cashback) showToast("🎁 Начислен спасательный кэшбэк 1,000$!");
                STATE.plinko.balls.splice(i, 1);
                syncClubHub();
                continue;
            }

            let leftRightOffset = 0;
            for (let s = 0; s < stepIdx; s++) {
                leftRightOffset += ball.path[s] === 1 ? 0.5 : -0.5;
            }
            const nextDir = ball.path[stepIdx] === 1 ? 0.5 : -0.5;
            const curOffset = leftRightOffset + nextDir * frac;

            const bx = canvas.width / 2 + curOffset * gapX;
            const by = startY + (stepIdx + frac) * gapY - Math.sin(frac * Math.PI) * 8;

            ctx.fillStyle = "#00e701";
            ctx.shadowColor = "#00e701";
            ctx.shadowBlur = 12;
            ctx.beginPath();
            ctx.arc(bx, by, 8.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        }
        requestAnimationFrame(drawLoop);
    };
    requestAnimationFrame(drawLoop);

    document.querySelectorAll("#plinkoRiskSelector .sel-chip").forEach((btn) => {
        btn.onclick = () => {
            STATE.plinko.risk = btn.dataset.risk;
            document.querySelectorAll("#plinkoRiskSelector .sel-chip").forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
            renderPlinkoBucketsUI();
        };
    });

    document.getElementById("plinkoDropBtn").onclick = async () => {
        const bet = parseInt(document.getElementById("plinkoBetInput").value, 10) || 100;
        try {
            SFX.click();
            const res = await apiCall("/api/games/plinko/drop", "POST", { bet, risk: STATE.plinko.risk });
            STATE.plinko.balls.push({
                path: res.path,
                bucketIndex: res.bucket_index,
                progress: 0,
                finalBalance: res.balance,
                isWin: res.is_win,
                cashback: res.cashback_triggered,
            });
        } catch (err) {
            showToast(err.message, true);
        }
    };
}

/* ==========================================================================
   🚀 4. CRASH / AVIATOR
   ========================================================================== */
function drawCrashGraph(mult, crashed = false) {
    const canvas = document.getElementById("crashCanvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const w = canvas.width, h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    const progress = Math.min(1, Math.log(mult) / Math.log(12));
    const ex = 45 + progress * (w - 100);
    const ey = h - 40 - Math.pow(progress, 1.35) * (h - 100);

    ctx.beginPath();
    ctx.moveTo(40, h - 40);
    ctx.quadraticCurveTo(ex * 0.55, h - 40, ex, ey);
    ctx.strokeStyle = crashed ? "#ff2a5f" : "#00e701";
    ctx.lineWidth = 4.5;
    ctx.stroke();

    ctx.fillStyle = crashed ? "#ff2a5f" : "#00e701";
    ctx.beginPath();
    ctx.arc(ex, ey, 7, 0, Math.PI * 2);
    ctx.fill();
}

function initCrashGame() {
    drawCrashGraph(1.0, false);
    document.querySelectorAll(".crash-preset").forEach((b) => {
        b.onclick = () => (document.getElementById("crashAutoInput").value = b.dataset.mult);
    });

    const startBtn = document.getElementById("crashStartBtn");
    const cashBtn = document.getElementById("crashCashoutBtn");
    const multEl = document.getElementById("crashBigMultiplier");
    const subEl = document.getElementById("crashSubStatus");

    startBtn.onclick = async () => {
        if (STATE.crash.running) return;
        const bet = parseInt(document.getElementById("crashBetInput").value, 10) || 100;
        const autoM = parseFloat(document.getElementById("crashAutoInput").value) || 2.0;

        try {
            const res = await apiCall("/api/games/crash/start", "POST", { bet, auto_cashout: autoM });
            updateTopBalance(res.balance);
            STATE.crash.running = true;
            STATE.crash.cashedOut = false;
            STATE.crash.bet = bet;
            STATE.crash.crashPoint = res.crash_point;
            STATE.crash.autoCashout = autoM;
            STATE.crash.startTime = performance.now();

            multEl.classList.remove("crashed-text");
            subEl.textContent = "РАКЕТА В ПОЛЁТЕ...";
            startBtn.classList.add("hidden");
            cashBtn.classList.remove("hidden");

            const frame = async (now) => {
                if (!STATE.crash.running) return;
                const sec = (now - STATE.crash.startTime) / 1000;
                const m = Math.pow(Math.E, 0.25 * sec);
                STATE.crash.currentMult = m;

                if (!STATE.crash.cashedOut && autoM >= 1.1 && m >= autoM && autoM <= STATE.crash.crashPoint) {
                    STATE.crash.cashedOut = true;
                    cashoutCrash(autoM);
                }

                if (m >= STATE.crash.crashPoint) {
                    STATE.crash.running = false;
                    multEl.textContent = `${STATE.crash.crashPoint.toFixed(2)}x`;
                    multEl.classList.add("crashed-text");
                    subEl.textContent = "РАКЕТА ВЗОРВАЛАСЬ!";
                    drawCrashGraph(STATE.crash.crashPoint, true);
                    startBtn.classList.remove("hidden");
                    cashBtn.classList.add("hidden");

                    if (!STATE.crash.cashedOut) {
                        triggerScreenShake("view-crash");
                        const bust = await apiCall("/api/games/crash/bust", "POST").catch(() => null);
                        if (bust) updateTopBalance(bust.balance, false);
                        syncClubHub();
                    }
                    return;
                }

                multEl.textContent = `${m.toFixed(2)}x`;
                document.getElementById("crashLiveCashoutVal").textContent = `${Math.round(bet * m)}$`;
                drawCrashGraph(m, false);
                requestAnimationFrame(frame);
            };
            requestAnimationFrame(frame);
        } catch (err) {
            showToast(err.message, true);
        }
    };

    async function cashoutCrash(multToClaim) {
        try {
            STATE.crash.cashedOut = true;
            cashBtn.classList.add("hidden");
            const res = await apiCall("/api/games/crash/cashout", "POST", { current_multiplier: multToClaim });
            if (res.status === "cashed_out") {
                updateTopBalance(res.balance, true);
                subEl.textContent = `ВЫВЕДЕНО НА ${res.multiplier.toFixed(2)}x (+${res.payout}$)`;
                showToast(`🚀 Вывод на ${res.multiplier.toFixed(2)}x (+${res.payout}$)!`);
                syncClubHub();
            }
        } catch (err) {
            showToast(err.message, true);
        }
    }

    cashBtn.onclick = () => {
        if (STATE.crash.running && !STATE.crash.cashedOut) cashoutCrash(STATE.crash.currentMult);
    };
}

/* ==========================================================================
   🎡 5. CRAZY NEON WHEEL
   ========================================================================== */
function buildWheelSvg(segments) {
    const svg = document.getElementById("wheelSvg");
    if (!svg || !segments.length) return;
    svg.innerHTML = "";
    const cx = 200, cy = 200, r = 190, cnt = segments.length;
    const step = (2 * Math.PI) / cnt;

    segments.forEach((seg, i) => {
        const a1 = i * step - Math.PI / 2 - step / 2;
        const a2 = a1 + step;
        const x1 = cx + r * Math.cos(a1), y1 = cy + r * Math.sin(a1);
        const x2 = cx + r * Math.cos(a2), y2 = cy + r * Math.sin(a2);

        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute("d", `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 0 1 ${x2} ${y2} Z`);
        path.setAttribute("fill", seg.color);
        path.setAttribute("stroke", "#071018");
        path.setAttribute("stroke-width", "2.5");
        svg.appendChild(path);

        const mid = a1 + step / 2;
        const tx = cx + r * 0.72 * Math.cos(mid), ty = cy + r * 0.72 * Math.sin(mid);
        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", tx);
        text.setAttribute("y", ty);
        text.setAttribute("fill", "#fff");
        text.setAttribute("font-size", "14");
        text.setAttribute("font-weight", "900");
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("dominant-baseline", "middle");
        text.setAttribute("transform", `rotate(${(mid * 180) / Math.PI + 90}, ${tx}, ${ty})`);
        text.textContent = seg.label;
        svg.appendChild(text);
    });
}

function initWheelGame() {
    const btn = document.getElementById("wheelSpinBtn");
    const disc = document.getElementById("wheelRotator");
    const hub = document.getElementById("wheelHubText");
    const banner = document.getElementById("wheelResultBanner");

    btn.onclick = async () => {
        if (STATE.wheel.spinning) return;
        const bet = parseInt(document.getElementById("wheelBetInput").value, 10) || 100;
        try {
            STATE.wheel.spinning = true;
            btn.disabled = true;
            SFX.click();
            const res = await apiCall("/api/games/wheel/spin", "POST", { bet });

            const extra = 6 * 360;
            const curMod = STATE.wheel.currentRotation % 360;
            const targetMod = (360 - res.target_angle_deg) % 360;
            let delta = targetMod - curMod;
            if (delta < 0) delta += 360;

            STATE.wheel.currentRotation += extra + delta;
            disc.style.transform = `rotate(${STATE.wheel.currentRotation}deg)`;

            setTimeout(() => {
                STATE.wheel.spinning = false;
                btn.disabled = false;
                hub.textContent = `${res.multiplier}x`;
                updateTopBalance(res.balance, res.is_win);
                banner.innerHTML = res.is_win
                    ? `🎉 Сектор <strong class="neon-accent">${res.multiplier}x</strong>! Выигрыш: <strong>+${res.payout}$</strong>!`
                    : `Выпал сектор <strong>${res.multiplier}x</strong>.`;
                syncClubHub();
            }, 4150);
        } catch (err) {
            STATE.wheel.spinning = false;
            btn.disabled = false;
            showToast(err.message, true);
        }
    };
}

/* ==========================================================================
   🃏 6. BLACKJACK 21 PRO
   ========================================================================== */
function renderBjHand(containerId, cards) {
    const box = document.getElementById(containerId);
    box.innerHTML = "";
    cards.forEach((c) => {
        const div = document.createElement("div");
        if (c.hidden) {
            div.className = "playing-card-3d hidden-card";
            div.textContent = "♠";
        } else {
            div.className = `playing-card-3d ${c.is_red ? "red-card" : ""}`;
            div.innerHTML = `<div>${c.rank}${c.suit}</div><div style="font-size:1.8rem;align-self:center">${c.suit}</div><div style="align-self:flex-end">${c.rank}${c.suit}</div>`;
        }
        box.appendChild(div);
    });
}

function initBlackjackGame() {
    const dealBtn = document.getElementById("bjDealBtn");
    const actStack = document.getElementById("bjActionBtns");
    const doubleBtn = document.getElementById("bjDoubleBtn");
    const ribbon = document.getElementById("bjStatusRibbon");

    function applyBjState(res) {
        renderBjHand("bjPlayerCards", res.player_hand);
        renderBjHand("bjDealerCards", res.dealer_hand);
        document.getElementById("bjPlayerScore").textContent = res.player_score;
        document.getElementById("bjDealerScore").textContent = res.dealer_score !== undefined ? res.dealer_score : `${res.dealer_visible_score}+?`;

        if (res.status === "playing") {
            dealBtn.classList.add("hidden");
            actStack.classList.remove("hidden");
            doubleBtn.classList.toggle("hidden", !res.can_double);
            ribbon.textContent = "ТВОЙ ХОД: ВЗЯТЬ КАРТУ ИЛИ ОСТАНОВИТЬСЯ?";
        } else {
            dealBtn.classList.remove("hidden");
            actStack.classList.add("hidden");
            updateTopBalance(res.balance, res.payout > 0);
            const msgs = {
                blackjack: `🔥 BLACKJACK 21 С РАЗДАЧИ! Выплата: +${res.payout}$!`,
                win: `🎉 ПОБЕДА НАД ДИЛЕРОМ! Выплата: +${res.payout}$!`,
                push: `🤝 НИЧЬЯ! Ставка ${res.payout}$ возвращена.`,
                bust: `💥 ПЕРЕБОР (${res.player_score} очк.)! Дилер забирает банк.`,
                lose: `🤵 Дилер победил (${res.dealer_score} против ${res.player_score}).`,
            };
            ribbon.textContent = msgs[res.outcome] || "Раунд завершён";
            syncClubHub();
        }
    }

    dealBtn.onclick = async () => {
        const bet = parseInt(document.getElementById("bjBetInput").value, 10) || 100;
        try {
            SFX.click();
            const res = await apiCall("/api/games/blackjack/start", "POST", { bet });
            updateTopBalance(res.balance);
            applyBjState(res);
        } catch (err) {
            showToast(err.message, true);
        }
    };

    ["hit", "stand", "double"].forEach((act) => {
        const btnId = act === "hit" ? "bjHitBtn" : act === "stand" ? "bjStandBtn" : "bjDoubleBtn";
        document.getElementById(btnId).onclick = async () => {
            try {
                SFX.click();
                const res = await apiCall("/api/games/blackjack/action", "POST", { action: act });
                applyBjState(res);
            } catch (err) {
                showToast(err.message, true);
            }
        };
    });
}

/* ==========================================================================
   🐲 7. DRAGON TOWER
   ========================================================================== */
function renderDragonTower() {
    const grid = document.getElementById("dragonTowerGrid");
    grid.innerHTML = "";
    STATE.tower.levelsConfig.forEach((cfg, idx) => {
        const row = document.createElement("div");
        row.className = `tower-floor-row ${STATE.tower.active && idx === STATE.tower.level ? "active-floor" : ""}`;
        row.innerHTML = `<div class="floor-mult-badge">${cfg.multiplier.toFixed(2)}x</div>`;
        for (let c = 0; c < 3; c++) {
            const btn = document.createElement("button");
            btn.className = "tower-cell-btn";
            btn.id = `towerCell_${idx}_${c}`;
            btn.onclick = () => pickTowerCell(idx, c);
            row.appendChild(btn);
        }
        grid.appendChild(row);
    });
}

async function pickTowerCell(lvl, col) {
    if (!STATE.tower.active || lvl !== STATE.tower.level) return;
    try {
        const res = await apiCall("/api/games/tower/pick", "POST", { col });
        if (res.status === "boom") {
            STATE.tower.active = false;
            res.full_board.forEach((rLayout, l) => {
                for (let c = 0; c < 3; c++) {
                    const b = document.getElementById(`towerCell_${l}_${c}`);
                    if (!b) continue;
                    b.innerHTML = rLayout[c] === "egg" ? SVG_VECTORS.dragonEgg : SVG_VECTORS.skull;
                    if (l === res.level && c === col) b.classList.add("revealed-rotten");
                }
            });
            triggerScreenShake();
            updateTopBalance(res.balance, false);
            document.getElementById("towerStartBtn").classList.remove("hidden");
            document.getElementById("towerCashoutBtn").classList.add("hidden");
            syncClubHub();
            return;
        }

        SFX.gem(lvl + 1);
        for (let c = 0; c < 3; c++) {
            const b = document.getElementById(`towerCell_${res.level}_${c}`);
            if (b) {
                b.innerHTML = res.row_reveal[c] === "egg" ? SVG_VECTORS.dragonEgg : SVG_VECTORS.skull;
                if (c === col) b.classList.add("revealed-good");
            }
        }

        if (res.status === "max_win") {
            STATE.tower.active = false;
            updateTopBalance(res.balance, true);
            document.getElementById("towerStartBtn").classList.remove("hidden");
            document.getElementById("towerCashoutBtn").classList.add("hidden");
            showToast(`🐲 ВЕРШИНА БАШНИ ДРАКОНА ПОКОРЕНА! +${res.payout}$!`);
            syncClubHub();
            return;
        }

        STATE.tower.level = res.next_level;
        document.getElementById("towerLevelText").textContent = `${res.next_level} / 8`;
        document.getElementById("towerMultText").textContent = `${res.multiplier.toFixed(2)}x`;
        document.getElementById("towerCashoutVal").textContent = `${res.cashout_value}$`;
        document.getElementById("towerCashoutBtn").classList.remove("hidden");
        document.querySelectorAll(".tower-floor-row").forEach((r, i) => r.classList.toggle("active-floor", i === res.next_level));
    } catch (err) {
        showToast(err.message, true);
    }
}

function initTowerGame() {
    renderDragonTower();
    document.getElementById("towerStartBtn").onclick = async () => {
        const bet = parseInt(document.getElementById("towerBetInput").value, 10) || 100;
        try {
            const res = await apiCall("/api/games/tower/start", "POST", { bet });
            STATE.tower.active = true;
            STATE.tower.level = 0;
            renderDragonTower();
            updateTopBalance(res.balance);
            document.getElementById("towerStartBtn").classList.add("hidden");
        } catch (err) {
            showToast(err.message, true);
        }
    };
    document.getElementById("towerCashoutBtn").onclick = async () => {
        try {
            const res = await apiCall("/api/games/tower/cashout", "POST");
            STATE.tower.active = false;
            updateTopBalance(res.balance, true);
            document.getElementById("towerStartBtn").classList.remove("hidden");
            document.getElementById("towerCashoutBtn").classList.add("hidden");
            showToast(`🐲 Забрал из Башни Дракона +${res.payout}$!`);
            syncClubHub();
        } catch (err) {
            showToast(err.message, true);
        }
    };
}

/* ==========================================================================
   🎚 8. DICE SLIDER, ⚡ 9. LIMBO, 🪙 10. COINFLIP, 💎 11. KENO
   ========================================================================== */
function initDiceLimboCoinKeno() {
    // 8. DICE
    const slider = document.getElementById("diceRangeSlider");
    const updateDiceLabels = () => {
        const t = parseInt(slider.value, 10);
        STATE.dice.target = t;
        const chance = STATE.dice.condition === "over" ? 100 - t : t;
        const mult = (88.0 / Math.max(2, Math.min(95, chance))).toFixed(2);
        document.getElementById("diceTargetVal").textContent = t;
        document.getElementById("diceChanceVal").textContent = `${chance}%`;
        document.getElementById("diceMultVal").textContent = `${mult}x`;
    };
    slider.oninput = updateDiceLabels;
    document.getElementById("diceCondOver").onclick = () => {
        STATE.dice.condition = "over";
        document.getElementById("diceCondOver").classList.add("active");
        document.getElementById("diceCondUnder").classList.remove("active");
        updateDiceLabels();
    };
    document.getElementById("diceCondUnder").onclick = () => {
        STATE.dice.condition = "under";
        document.getElementById("diceCondUnder").classList.add("active");
        document.getElementById("diceCondOver").classList.remove("active");
        updateDiceLabels();
    };
    document.getElementById("diceRollBtn").onclick = async () => {
        const bet = parseInt(document.getElementById("diceBetInput").value, 10) || 100;
        try {
            const res = await apiCall("/api/games/dice/play", "POST", {
                bet,
                target: STATE.dice.target,
                condition: STATE.dice.condition,
            });
            const bub = document.getElementById("diceRollBubble");
            bub.textContent = res.roll.toFixed(2);
            bub.style.color = res.is_win ? "#00e701" : "#ff2a5f";
            bub.style.borderColor = res.is_win ? "#00e701" : "#ff2a5f";
            updateTopBalance(res.balance, res.is_win);
            syncClubHub();
        } catch (err) {
            showToast(err.message, true);
        }
    };

    // 9. LIMBO
    document.querySelectorAll(".limbo-preset").forEach((b) => {
        b.onclick = () => (document.getElementById("limboTargetInput").value = b.dataset.m);
    });
    document.getElementById("limboPlayBtn").onclick = async () => {
        const bet = parseInt(document.getElementById("limboBetInput").value, 10) || 100;
        const target = parseFloat(document.getElementById("limboTargetInput").value) || 2.0;
        try {
            const res = await apiCall("/api/games/limbo/play", "POST", { bet, target_multiplier: target });
            const disp = document.getElementById("limboBigDisplay");
            disp.textContent = `${res.result_multiplier.toFixed(2)}x`;
            disp.style.color = res.is_win ? "#00e701" : "#ff2a5f";
            updateTopBalance(res.balance, res.is_win);
            syncClubHub();
        } catch (err) {
            showToast(err.message, true);
        }
    };

    // 10. 3D COINFLIP
    const coinEl = document.getElementById("coin3dElement");
    document.getElementById("coinStartBtn").onclick = async () => {
        const bet = parseInt(document.getElementById("coinBetInput").value, 10) || 100;
        try {
            const res = await apiCall("/api/games/coinflip/start", "POST", { bet });
            updateTopBalance(res.balance);
            document.getElementById("coinStartBtn").classList.add("hidden");
            document.getElementById("coinPickControls").classList.remove("hidden");
            document.getElementById("coinCashoutBtn").classList.add("hidden");
            document.getElementById("coinStreakText").textContent = "0";
            document.getElementById("coinMultText").textContent = "1.00x";
        } catch (err) {
            showToast(err.message, true);
        }
    };

    ["heads", "tails"].forEach((side) => {
        const btn = document.getElementById(side === "heads" ? "coinPickHeads" : "coinPickTails");
        btn.onclick = async () => {
            try {
                coinEl.classList.add("flipping");
                const res = await apiCall("/api/games/coinflip/flip", "POST", { side });
                setTimeout(() => {
                    coinEl.classList.remove("flipping");
                    coinEl.innerHTML = `<div class="coin-face">${res.landed_side === "heads" ? "🦅" : "💎"}</div>`;
                    if (res.status === "lost") {
                        triggerScreenShake("view-coinflip");
                        updateTopBalance(res.balance, false);
                        document.getElementById("coinStartBtn").classList.remove("hidden");
                        document.getElementById("coinPickControls").classList.add("hidden");
                        document.getElementById("coinStatusMsg").textContent = "💥 Не угадал сторону! Серия сгорела.";
                    } else {
                        SFX.gem(res.streak);
                        document.getElementById("coinStreakText").textContent = res.streak;
                        document.getElementById("coinMultText").textContent = `${res.multiplier.toFixed(2)}x`;
                        document.getElementById("coinCashoutVal").textContent = `${res.cashout_value}$`;
                        document.getElementById("coinCashoutBtn").classList.remove("hidden");
                        document.getElementById("coinStatusMsg").textContent = `🔥 Угадал! Серия: ${res.streak} (${res.multiplier}x)`;
                    }
                    syncClubHub();
                }, 600);
            } catch (err) {
                coinEl.classList.remove("flipping");
                showToast(err.message, true);
            }
        };
    });

    document.getElementById("coinCashoutBtn").onclick = async () => {
        const res = await apiCall("/api/games/coinflip/cashout", "POST");
        updateTopBalance(res.balance, true);
        document.getElementById("coinStartBtn").classList.remove("hidden");
        document.getElementById("coinPickControls").classList.add("hidden");
        showToast(`🪙 Выведено из Coinflip: +${res.payout}$!`);
        syncClubHub();
    };

    // 11. KENO 40
    const kenoGrid = document.getElementById("kenoGrid40");
    for (let n = 1; n <= 40; n++) {
        const b = document.createElement("button");
        b.className = "keno-tile";
        b.id = `kenoTile_${n}`;
        b.textContent = n;
        b.onclick = () => {
            if (STATE.keno.picks.has(n)) STATE.keno.picks.delete(n);
            else if (STATE.keno.picks.size < 10) STATE.keno.picks.add(n);
            b.classList.toggle("picked", STATE.keno.picks.has(n));
            document.getElementById("kenoPickedCount").textContent = `${STATE.keno.picks.size} / 10`;
        };
        kenoGrid.appendChild(b);
    }

    document.getElementById("kenoAutoPickBtn").onclick = () => {
        STATE.keno.picks.clear();
        while (STATE.keno.picks.size < 8) STATE.keno.picks.add(1 + Math.floor(Math.random() * 40));
        for (let n = 1; n <= 40; n++) {
            const t = document.getElementById(`kenoTile_${n}`);
            t.className = `keno-tile ${STATE.keno.picks.has(n) ? "picked" : ""}`;
        }
        document.getElementById("kenoPickedCount").textContent = "8 / 10";
    };

    document.getElementById("kenoClearBtn").onclick = () => {
        STATE.keno.picks.clear();
        document.querySelectorAll(".keno-tile").forEach((t) => (t.className = "keno-tile"));
        document.getElementById("kenoPickedCount").textContent = "0 / 10";
    };

    document.getElementById("kenoPlayBtn").onclick = async () => {
        const bet = parseInt(document.getElementById("kenoBetInput").value, 10) || 100;
        try {
            document.querySelectorAll(".keno-tile").forEach((t) => t.classList.remove("drawn-hit", "drawn-miss"));
            const res = await apiCall("/api/games/keno/play", "POST", { bet, picks: Array.from(STATE.keno.picks) });
            const hitsSet = new Set(res.hits);
            res.drawn.forEach((dNum) => {
                const t = document.getElementById(`kenoTile_${dNum}`);
                if (t) t.classList.add(hitsSet.has(dNum) ? "drawn-hit" : "drawn-miss");
            });
            document.getElementById("kenoLastWin").textContent = `${res.payout} $ (${res.multiplier}x)`;
            updateTopBalance(res.balance, res.is_win);
            syncClubHub();
        } catch (err) {
            showToast(err.message, true);
        }
    };
}

/* ==========================================================================
   🥊 12. CYBER-OCTAGON 2011 & 🎰 SLOTS 777
   ========================================================================== */
function populateFightersSelects(fighters) {
    STATE.fight.fighters = fighters;
    const s1 = document.getElementById("fightSelect1");
    const s2 = document.getElementById("fightSelect2");
    const pvpSel = document.getElementById("pvpChallengerFighter");
    if (!s1 || !s2 || !fighters.length) return;

    const p1 = s1.value || "zabik";
    const p2 = s2.value || "nekit";
    s1.innerHTML = "";
    s2.innerHTML = "";
    pvpSel.innerHTML = "";

    fighters.forEach((f) => {
        [s1, s2, pvpSel].forEach((sel) => {
            const opt = document.createElement("option");
            opt.value = f.key;
            opt.textContent = `${f.name} (${f.weight_kg} кг • ⚡${f.power_score})`;
            sel.appendChild(opt);
        });
    });

    s1.value = p1;
    s2.value = p2 !== p1 ? p2 : fighters[1].key;
    updateOctagonCards();
}

async function updateOctagonCards() {
    const s1 = document.getElementById("fightSelect1");
    const s2 = document.getElementById("fightSelect2");
    if (s1.value === s2.value) {
        const alt = STATE.fight.fighters.find((f) => f.key !== s1.value);
        if (alt) s2.value = alt.key;
    }
    const f1 = STATE.fight.fighters.find((f) => f.key === s1.value);
    const f2 = STATE.fight.fighters.find((f) => f.key === s2.value);
    if (!f1 || !f2) return;

    document.getElementById("f1Portrait").innerHTML = getFighterPortraitSvg(f1);
    document.getElementById("f1Name").textContent = f1.name;
    document.getElementById("f1Title").textContent = f1.title;
    document.getElementById("f1Stats").textContent = `${f1.height_cm} см • ${f1.weight_kg} кг • ⚡${f1.power_score}`;

    document.getElementById("f2Portrait").innerHTML = getFighterPortraitSvg(f2);
    document.getElementById("f2Name").textContent = f2.name;
    document.getElementById("f2Title").textContent = f2.title;
    document.getElementById("f2Stats").textContent = `${f2.height_cm} см • ${f2.weight_kg} кг • ⚡${f2.power_score}`;

    document.getElementById("pickF1Name").textContent = f1.name;
    document.getElementById("pickF2Name").textContent = f2.name;

    try {
        const res = await apiCall(`/api/games/fight/matchup?f1=${f1.key}&f2=${f2.key}`);
        document.getElementById("pickF1Odds").textContent = `${res.odds1}x`;
        document.getElementById("pickF2Odds").textContent = `${res.odds2}x`;
    } catch (_) {}
}

function initFightAndSlots() {
    const s1 = document.getElementById("fightSelect1");
    const s2 = document.getElementById("fightSelect2");
    s1.onchange = updateOctagonCards;
    s2.onchange = updateOctagonCards;

    document.getElementById("pickF1Btn").onclick = () => {
        STATE.fight.pickedSlot = 1;
        document.getElementById("pickF1Btn").classList.add("active");
        document.getElementById("pickF2Btn").classList.remove("active");
    };
    document.getElementById("pickF2Btn").onclick = () => {
        STATE.fight.pickedSlot = 2;
        document.getElementById("pickF2Btn").classList.add("active");
        document.getElementById("pickF1Btn").classList.remove("active");
    };

    document.querySelectorAll(".tactic-btn").forEach((b) => {
        b.onclick = () => {
            STATE.fight.tactic = b.dataset.tactic;
            document.querySelectorAll(".tactic-btn").forEach((el) => el.classList.remove("active"));
            b.classList.add("active");
        };
    });

    document.getElementById("fightStartBtn").onclick = async () => {
        if (STATE.fight.busy) return;
        const f1Key = s1.value, f2Key = s2.value;
        const pickedKey = STATE.fight.pickedSlot === 1 ? f1Key : f2Key;
        const bet = parseInt(document.getElementById("fightBetInput").value, 10) || 0;

        try {
            STATE.fight.busy = true;
            const c1 = document.getElementById("fighterCard1");
            const c2 = document.getElementById("fighterCard2");
            c1.classList.remove("winner-glow");
            c2.classList.remove("winner-glow");

            const res = await apiCall("/api/games/fight/play", "POST", {
                fighter1_key: f1Key,
                fighter2_key: f2Key,
                picked_key: pickedKey,
                tactic: STATE.fight.tactic,
                bet,
            });

            const comm = document.getElementById("fightCommentaryBox");
            const rBadge = document.getElementById("fightRoundBadge");

            for (const r of res.rounds) {
                rBadge.textContent = `РАУНД ${r.round}/3`;
                comm.textContent = r.text;
                SFX.click();
                document.getElementById("f1HpBar").style.width = `${r.f1_hp}%`;
                document.getElementById("f1HpText").textContent = `${r.f1_hp}%`;
                document.getElementById("f2HpBar").style.width = `${r.f2_hp}%`;
                document.getElementById("f2HpText").textContent = `${r.f2_hp}%`;
                await new Promise((resolve) => setTimeout(resolve, 950));
            }

            rBadge.textContent = `ПОБЕДИЛ ${res.winner_name.toUpperCase()}`;
            if (res.winner_key === f1Key) c1.classList.add("winner-glow");
            else c2.classList.add("winner-glow");

            comm.innerHTML = `<strong>${res.winner_crit}</strong><br><em>${res.winner_quote}</em>`;
            updateTopBalance(res.balance, res.user_won_bet);
            syncClubHub();
        } catch (err) {
            showToast(err.message, true);
        } finally {
            STATE.fight.busy = false;
        }
    };

    // SLOTS 777
    ["seven", "diamond", "crown"].forEach((sym, i) => {
        document.getElementById(`slotReel${i}`).innerHTML = SVG_VECTORS.slotIcons[sym];
    });
    document.getElementById("slotsSpinBtn").onclick = async () => {
        const bet = parseInt(document.getElementById("slotsBetInput").value, 10) || 100;
        try {
            SFX.click();
            const res = await apiCall("/api/games/slots/spin", "POST", { bet });
            res.reels.forEach((sym, i) => {
                document.getElementById(`slotReel${i}`).innerHTML = SVG_VECTORS.slotIcons[sym] || SVG_VECTORS.slotIcons.seven;
            });
            document.getElementById("slotsCodeDigits").textContent = res.code_3digit;
            document.getElementById("slotsResultText").innerHTML = res.is_win
                ? `🎉 <span class="neon-accent">${res.combo_name}</span> Выигрыш: +${res.payout}$!`
                : "Мимо кассы! Крути ещё!";
            updateTopBalance(res.balance, res.is_win);
            syncClubHub();
        } catch (err) {
            showToast(err.message, true);
        }
    };
}

/* ==========================================================================
   ⚔️ ОНЛАЙН ВЫЗОВЫ ДРУЗЬЯМ (PVP КАРТЫ & БОЙЦЫ) + ЧАТ + ПЕРЕВОДЫ
   ========================================================================== */
function initPvpAndSocial() {
    const modal = document.getElementById("pvpModalBackdrop");
    document.getElementById("openPvpModalBtn").onclick = () => modal.classList.remove("hidden");
    document.getElementById("createPvpBtnTop").onclick = () => modal.classList.remove("hidden");
    document.getElementById("closePvpModalBtn").onclick = () => modal.classList.add("hidden");

    const mCards = document.getElementById("pvpModeCardsBtn");
    const mFight = document.getElementById("pvpModeFightersBtn");
    const fOpts = document.getElementById("pvpFighterOptions");

    mCards.onclick = () => {
        STATE.pvp.mode = "cards";
        mCards.classList.add("active");
        mFight.classList.remove("active");
        fOpts.classList.add("hidden");
    };
    mFight.onclick = () => {
        STATE.pvp.mode = "fighters";
        mFight.classList.add("active");
        mCards.classList.remove("active");
        fOpts.classList.remove("hidden");
    };

    document.querySelectorAll(".pvp-tact").forEach((b) => {
        b.onclick = () => {
            STATE.pvp.tactic = b.dataset.t;
            document.querySelectorAll(".pvp-tact").forEach((el) => el.classList.remove("active"));
            b.classList.add("active");
        };
    });

    document.getElementById("submitCreatePvpBtn").onclick = async () => {
        const target_id = parseInt(document.getElementById("pvpTargetSelect").value, 10) || 0;
        const bet = parseInt(document.getElementById("pvpBetAmount").value, 10) || 500;
        const fighter_key = document.getElementById("pvpChallengerFighter").value || "davrik";
        try {
            const res = await apiCall("/api/pvp/create", "POST", {
                target_id,
                mode: STATE.pvp.mode,
                bet,
                fighter_key,
                tactic: STATE.pvp.tactic,
            });
            modal.classList.add("hidden");
            updateTopBalance(res.balance);
            showToast(`⚔️ ${res.message}`);
            switchTab("pvp");
            syncClubHub();
        } catch (err) {
            showToast(err.message, true);
        }
    };

    // Живой чат
    document.getElementById("chatSendForm").onsubmit = async (e) => {
        e.preventDefault();
        const inp = document.getElementById("chatTextInput");
        const txt = inp.value.trim();
        if (!txt) return;
        inp.value = "";
        try {
            await apiCall("/api/chat/send", "POST", { text: txt });
            syncClubHub();
        } catch (err) {
            showToast(err.message, true);
        }
    };

    // Всплывающий баннер входящего вызова
    document.getElementById("incPvpDeclineBtn").onclick = () => {
        document.getElementById("incomingPvpBanner").classList.add("hidden");
    };
    document.getElementById("incPvpAcceptBtn").onclick = async () => {
        if (!STATE.incomingPvpChallenge) return;
        document.getElementById("incomingPvpBanner").classList.add("hidden");
        await acceptPvpChallenge(STATE.incomingPvpChallenge.id);
    };
}

async function acceptPvpChallenge(challengeId) {
    try {
        const res = await apiCall("/api/pvp/accept", "POST", {
            challenge_id: challengeId,
            fighter_key: "muham",
            tactic: "kick",
        });
        updateTopBalance(res.balance, res.you_won);
        if (res.you_won) {
            showToast(`🏆 ТЫ ПОБЕДИЛ В PVP-ДУЭЛИ И ЗАБРАЛ БАНК +${res.pot}$!`);
        } else {
            showToast(`💀 В PvP-дуэли победил ${res.winner_name} (Банк ${res.pot}$).`, true);
        }
        syncClubHub();
    } catch (err) {
        showToast(err.message, true);
    }
}

/* ==========================================================================
   🔄 СИНХРОНИЗАЦИЯ ХАБА (ЛИДЕРБОРД, ОНЛАЙН ДРУЗЕЙ, ЧАТ, PVP ВЫЗОВЫ)
   ========================================================================== */
async function syncClubHub() {
    try {
        const res = await apiCall("/api/hub", "GET");

        if (res.plinko_buckets && !Object.keys(STATE.plinko.buckets).length) {
            STATE.plinko.buckets = res.plinko_buckets;
            renderPlinkoBucketsUI();
        }
        if (res.wheel_segments && !STATE.wheel.segments.length) {
            STATE.wheel.segments = res.wheel_segments;
            buildWheelSvg(res.wheel_segments);
        }
        if (res.fighters && res.fighters.length && !STATE.fight.fighters.length) {
            populateFightersSelects(res.fighters);
        }

        // 1. Онлайн-друзья справа + селектор вызова
        const onlineBox = document.getElementById("onlineFriendsList");
        const targetSel = document.getElementById("pvpTargetSelect");
        const prevSel = targetSel.value;
        onlineBox.innerHTML = "";
        targetSel.innerHTML = `<option value="0">🌐 Открытый вызов для любого Online</option>`;

        document.getElementById("onlineFriendsCount").textContent = res.online_friends.length;

        if (res.online_friends.length === 0) {
            onlineBox.innerHTML = `<div style="font-size:0.76rem;color:var(--text-muted)">Сейчас никто из друзей не открыл сайт. Отправь им ссылку!</div>`;
        } else {
            res.online_friends.forEach((f) => {
                const opt = document.createElement("option");
                opt.value = f.id;
                opt.textContent = `🟢 ${f.display_name} (${f.balance}$)`;
                targetSel.appendChild(opt);

                const item = document.createElement("div");
                item.className = "friend-online-row";
                item.innerHTML = `
                    <div>
                        <strong style="font-size:0.82rem">${f.display_name}</strong>
                        <div class="neon-accent" style="font-size:0.72rem">${Number(f.balance).toLocaleString("ru-RU")} $</div>
                    </div>
                    <div class="friend-actions">
                        <button class="mini-act-btn pvp-quick" title="Вызвать на дуэль">⚔️ Дуэль</button>
                        <button class="mini-act-btn send-cash" title="Перевести 500$">💸 500$</button>
                    </div>
                `;
                item.querySelector(".pvp-quick").onclick = () => {
                    targetSel.value = f.id;
                    document.getElementById("pvpModalBackdrop").classList.remove("hidden");
                };
                item.querySelector(".send-cash").onclick = async () => {
                    try {
                        const tr = await apiCall("/api/friends/transfer", "POST", { target_user_id: f.id, amount: 500 });
                        updateTopBalance(tr.balance);
                        showToast(tr.message);
                        syncClubHub();
                    } catch (err) {
                        showToast(err.message, true);
                    }
                };
                onlineBox.appendChild(item);
            });
        }
        if (prevSel) targetSel.value = prevSel;

        // 2. Живой чат
        const chatBox = document.getElementById("chatMessagesBox");
        chatBox.innerHTML = "";
        res.chat_messages.forEach((m) => {
            const d = document.createElement("div");
            d.className = "chat-msg-item";
            const badge = m.is_admin ? `<span style="color:#facc15">[ROOT]</span> ` : "";
            d.innerHTML = `${badge}<strong style="color:#00e701">${m.display_name}:</strong> ${m.text}`;
            chatBox.appendChild(d);
        });
        chatBox.scrollTop = chatBox.scrollHeight;

        // 3. Активные PvP вызовы + звуковое уведомление при новом вызове!
        const pvpGrid = document.getElementById("pvpChallengesList");
        pvpGrid.innerHTML = "";
        const pendingChallenges = res.pvp_challenges.filter((c) => c.status === "pending");
        document.getElementById("headerPvpCount").textContent = pendingChallenges.length;

        res.pvp_challenges.forEach((ch) => {
            if (
                ch.status === "pending" &&
                STATE.user &&
                ch.challenger_id !== STATE.user.id &&
                (ch.target_id === 0 || ch.target_id === STATE.user.id) &&
                !STATE.seenPvpIds.has(ch.id)
            ) {
                STATE.seenPvpIds.add(ch.id);
                STATE.incomingPvpChallenge = ch;
                SFX.alert();
                document.getElementById("incPvpTitle").textContent = `🚨 ВЫЗОВ ОТ ${ch.challenger_name.toUpperCase()}!`;
                document.getElementById("incPvpDesc").textContent = `${ch.mode === "cards" ? "🃏 Карточная Дуэль" : "🥊 Бой Персонажей"} • Ставка: ${ch.bet}$ (Банк: ${ch.bet * 2}$)`;
                document.getElementById("incomingPvpBanner").classList.remove("hidden");
            }

            const card = document.createElement("div");
            card.className = "pvp-card-item";
            const modeBadge = ch.mode === "cards" ? "🃏 Карточная Дуэль 21" : `🥊 Бой Персонажей (${ch.c_fighter.toUpperCase()})`;
            if (ch.status === "pending") {
                const isMine = STATE.user && ch.challenger_id === STATE.user.id;
                card.innerHTML = `
                    <div style="display:flex;justify-content:space-between">
                        <strong>${modeBadge}</strong>
                        <span class="gold-txt">Банк: ${ch.bet * 2} $</span>
                    </div>
                    <div style="font-size:0.83rem">Вызывает: <strong>${ch.challenger_name}</strong> ➔ <em>${ch.target_name}</em></div>
                    <div>
                        ${isMine
                            ? `<button class="action-btn ghost small full pvp-cancel-btn">Отменить вызов</button>`
                            : `<button class="action-btn green small full pvp-acc-btn">⚔️ ПРИНЯТЬ ВЫЗОВ НА ${ch.bet}$</button>`
                        }
                    </div>
                `;
                const accB = card.querySelector(".pvp-acc-btn");
                if (accB) accB.onclick = () => acceptPvpChallenge(ch.id);
                const canB = card.querySelector(".pvp-cancel-btn");
                if (canB) {
                    canB.onclick = async () => {
                        const r = await apiCall(`/api/pvp/cancel?challenge_id=${ch.id}`, "POST");
                        updateTopBalance(r.balance);
                        syncClubHub();
                    };
                }
            } else {
                const s = ch.summary || {};
                const details = s.mode === "cards"
                    ? `Карты: ${s.challenger_name} (${(s.c_cards || []).join(" ")}=${s.c_score}) vs ${s.accepter_name} (${(s.a_cards || []).join(" ")}=${s.a_score})`
                    : `${s.crit_phrase || ""}`;
                card.innerHTML = `
                    <div style="display:flex;justify-content:space-between">
                        <strong class="neon-accent">🏆 Победил: ${ch.winner_name}</strong>
                        <span class="gold-txt">+${ch.bet * 2} $</span>
                    </div>
                    <div style="font-size:0.78rem;color:var(--text-muted)">${details}</div>
                `;
            }
            pvpGrid.appendChild(card);
        });

        // 4. Лидерборд
        const lbBody = document.getElementById("leaderboardTableBody");
        lbBody.innerHTML = "";
        res.leaderboard.forEach((u, i) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>#${i + 1}</strong></td>
                <td>
                    <div style="display:flex;align-items:center;gap:8px">
                        <div class="user-avatar-box">${getAvatarSvg(u.avatar)}</div>
                        <div>
                            <strong>${u.display_name}</strong>
                            <div style="font-size:0.68rem;color:${u.vip_color}">${u.vip_title}</div>
                        </div>
                    </div>
                </td>
                <td>${u.is_online ? '<span class="neon-accent">🟢 Online</span>' : '<span style="color:var(--text-muted)">⚪ Offline</span>'}</td>
                <td><strong class="neon-accent">${Number(u.balance).toLocaleString("ru-RU")} $</strong></td>
                <td><strong class="gold-txt">+${Number(u.total_won).toLocaleString("ru-RU")} $</strong></td>
                <td>+${Number(u.biggest_win).toLocaleString("ru-RU")} $</td>
                <td><button class="mini-act-btn lb-duel-btn">⚔️ Вызов</button></td>
            `;
            tr.querySelector(".lb-duel-btn").onclick = () => {
                targetSel.value = u.id;
                document.getElementById("pvpModalBackdrop").classList.remove("hidden");
            };
            lbBody.appendChild(tr);
        });

        // 5. Live-лента заносов
        const feedBody = document.getElementById("liveBetsFeedBody");
        feedBody.innerHTML = "";
        res.live_feed.forEach((f) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${f.game}</strong></td>
                <td>@${f.username}</td>
                <td>${f.bet} $</td>
                <td><span class="${f.is_win ? "neon-accent" : ""}">${f.multiplier.toFixed(2)}x</span></td>
                <td><strong class="${f.is_win ? "neon-accent" : ""}">${f.is_win ? `+${f.payout} $` : "0 $"}</strong></td>
            `;
            feedBody.appendChild(tr);
        });
    } catch (_) {}
}

/* ==========================================================================
   🛠 ROOT-КОНСОЛЬ АДМИНА (ДАВРОН)
   ========================================================================== */
async function loadAdminConsole() {
    if (!STATE.user || !STATE.user.is_admin) return;
    try {
        const res = await apiCall("/api/admin/users", "GET");
        const uList = document.getElementById("adminUsersList");
        const fList = document.getElementById("adminFightersList");
        uList.innerHTML = "";
        fList.innerHTML = "";

        res.users.forEach((u) => {
            const r = document.createElement("div");
            r.className = "adm-row";
            r.innerHTML = `
                <div>
                    <strong>${u.display_name}</strong> <small style="color:var(--text-muted)">(@${u.username})</small>
                    <div class="neon-accent">${Number(u.balance).toLocaleString("ru-RU")} $</div>
                </div>
                <div class="row-btns">
                    <button class="adm-chip green" data-m="add" data-v="5000">+5k$</button>
                    <button class="adm-chip green" data-m="add" data-v="25000">+25k$</button>
                    <button class="adm-chip green" data-m="add" data-v="100000">+100k$</button>
                    <button class="adm-chip purple" data-m="set" data-v="10000">=10k$</button>
                    <button class="adm-chip red" data-m="set" data-v="1000">=1k$</button>
                </div>
            `;
            r.querySelectorAll("button").forEach((b) => {
                b.onclick = async () => {
                    const out = await apiCall("/api/admin/balance", "POST", {
                        target_user_id: u.id,
                        mode: b.dataset.m,
                        amount: parseInt(b.dataset.v, 10),
                    });
                    if (STATE.user && out.user.id === STATE.user.id) updateTopBalance(out.user.balance, true);
                    showToast(`👑 ${out.message}`);
                    loadAdminConsole();
                    syncClubHub();
                };
            });
            uList.appendChild(r);
        });

        res.fighters.forEach((f) => {
            const r = document.createElement("div");
            r.className = "adm-row";
            r.innerHTML = `
                <div><strong>${f.name}</strong> — Сила: <span class="neon-accent">⚡${f.power_score}</span></div>
                <div class="row-btns">
                    <button class="adm-chip red" data-p="${Math.max(25, f.power_score - 3)}">-3</button>
                    <button class="adm-chip green" data-p="${Math.min(95, f.power_score + 3)}">+3</button>
                </div>
            `;
            r.querySelectorAll("button").forEach((b) => {
                b.onclick = async () => {
                    const out = await apiCall("/api/admin/fighter-power", "POST", {
                        fighter_key: f.key,
                        power_score: parseInt(b.dataset.p, 10),
                    });
                    showToast(out.message);
                    loadAdminConsole();
                };
            });
            fList.appendChild(r);
        });
    } catch (err) {
        showToast(err.message, true);
    }
}

/* ==========================================================================
   🧭 ГЛОБАЛЬНАЯ НАВИГАЦИЯ И ИНИЦИАЛИЗАЦИЯ
   ========================================================================== */
function switchTab(tabName) {
    STATE.activeTab = tabName;
    SFX.click();
    document.querySelectorAll(".game-view").forEach((v) => v.classList.remove("active"));
    const target = document.getElementById(`view-${tabName}`);
    if (target) target.classList.add("active");

    document.querySelectorAll(".nav-btn").forEach((b) => {
        b.classList.toggle("active", b.dataset.tab === tabName);
    });

    if (tabName === "admin") loadAdminConsole();
    if (tabName === "leaderboard" || tabName === "pvp") syncClubHub();
}

function initGlobalUI() {
    document.querySelectorAll("[data-tab]").forEach((el) => {
        el.addEventListener("click", () => switchTab(el.dataset.tab));
    });

    document.getElementById("sidebarToggleBtn").onclick = () => {
        document.getElementById("sidebarLeft").classList.toggle("collapsed");
    };

    document.getElementById("rightSocialToggleBtn").onclick = () => {
        document.getElementById("sidebarRight").classList.toggle("mobile-open");
    };

    const sndBtn = document.getElementById("soundToggleBtn");
    sndBtn.onclick = () => {
        STATE.soundEnabled = !STATE.soundEnabled;
        sndBtn.classList.toggle("active", STATE.soundEnabled);
        showToast(STATE.soundEnabled ? "🔊 Звуковые эффекты включены" : "🔇 Звук выключен");
    };

    document.querySelectorAll("[data-bet-target]").forEach((b) => {
        b.onclick = () => {
            SFX.click();
            const inp = document.getElementById(b.dataset.betTarget);
            if (!inp) return;
            const cur = parseInt(inp.value, 10) || 100;
            const maxB = STATE.user ? STATE.user.balance : 10000;
            if (b.dataset.act === "half") inp.value = Math.max(10, Math.floor(cur / 2));
            if (b.dataset.act === "double") inp.value = Math.min(maxB, cur * 2);
            if (b.dataset.act === "max") inp.value = Math.max(10, maxB);
        };
    });

    document.getElementById("refreshLeaderboardBtn").onclick = syncClubHub;
    document.getElementById("adminBonusAllBtn").onclick = async () => {
        const r = await apiCall("/api/admin/global-balance", "POST", { mode: "bonus_all", amount: 5000 });
        showToast(r.message);
        checkSession();
        loadAdminConsole();
        syncClubHub();
    };
    document.getElementById("adminResetAllBtn").onclick = async () => {
        const r = await apiCall("/api/admin/global-balance", "POST", { mode: "reset_all", amount: 10000 });
        showToast(r.message);
        checkSession();
        loadAdminConsole();
        syncClubHub();
    };
    document.getElementById("cashbackInfoBtn").onclick = () => {
        showToast("🛡 Страховка Даврона: если баланс упадёт ниже 100$, казик мгновенно вернёт тебе 1,000$!");
    };
}

window.addEventListener("DOMContentLoaded", async () => {
    startParticleLoop();
    initAuthModal();
    initGlobalUI();
    initAppleGame();
    initMinesGame();
    initPlinkoGame();
    initCrashGame();
    initWheelGame();
    initBlackjackGame();
    initTowerGame();
    initDiceLimboCoinKeno();
    initFightAndSlots();
    initPvpAndSocial();

    await checkSession();
    await syncClubHub();

    // Каждые 5 секунд синхронизируем Онлайн друзей, Чат и Входящие PvP-вызовы!
    setInterval(() => {
        syncClubHub();
    }, 5000);
});