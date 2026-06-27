from __future__ import annotations

from pathlib import Path
import json
import shutil


UPLOADED_ASSETS = {
    "hero_video": (
        Path("/Users/macbook/Downloads/download (1)/Moon_rover_space_station_astronaut_202606241733.mp4"),
        "hero-lunar.mp4",
    ),
    "rover_path": (
        Path("/Users/macbook/Downloads/ChatGPT Image Jun 24, 2026 at 05_35_54 PM.png"),
        "rover-path.png",
    ),
    "moon_hotspot": (
        Path("/Users/macbook/Downloads/ChatGPT Image Jun 24, 2026 at 05_36_00 PM.png"),
        "moon-hotspot.png",
    ),
    "astronaut": (
        Path("/Users/macbook/Downloads/ChatGPT Image Jun 24, 2026 at 05_35_51 PM.png"),
        "astronaut.png",
    ),
    "rover_moon": (
        Path("/Users/macbook/Downloads/ChatGPT Image Jun 24, 2026 at 04_18_10 PM.png"),
        "rover-moon.png",
    ),
}


def format_value(value: object, digits: int = 1) -> str:
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def cubic_meters(value: object) -> str:
    return f"{format_value(value)} m&sup3;"


def prepare_uploaded_assets(repo_root: Path) -> dict[str, str]:
    assets_dir = repo_root / "outputs/assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    prepared = {
        "hero_video": "assets/landing-bg.png",
        "rover_path": "assets/landing-bg.png",
        "moon_hotspot": "assets/internal-bg.png",
        "astronaut": "assets/transition-bg.png",
        "rover_moon": "assets/landing-bg.png",
    }

    for key, (source, filename) in UPLOADED_ASSETS.items():
        if source.exists():
            target = assets_dir / filename
            shutil.copy2(source, target)
            prepared[key] = f"assets/{filename}"

    return prepared


def build_fallback_html(repo_root: Path) -> Path:
    manifest_path = repo_root / "outputs/final_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    visual_assets = prepare_uploaded_assets(repo_root)
    landing_bg = "assets/landing-bg.png"
    internal_bg = "assets/internal-bg.png"
    transition_bg = "assets/transition-bg.png"

    story = "".join(f"<li>{item}</li>" for item in payload.get("story_beats", []))
    rankings = "".join(
        f"<tr><td>{item['site']}</td><td>{item['score']:.4f}</td><td>({item['row']}, {item['col']})</td></tr>"
        for item in payload.get("site_rankings", [])
    )
    cost_rows = "".join(
        f"<tr><td>{key.replace('_', ' ').title()}</td><td>{format_value(value, 2)}</td></tr>"
        for key, value in payload.get("traverse_summary", {}).get("cost_breakdown", {}).items()
    )
    artifact_cards = []
    for index, artifact in enumerate(payload.get("artifacts", []), start=1):
        label = Path(artifact).name.replace("_", " ").replace(".svg", "").title()
        artifact_cards.append(
            f"""
            <article class="dashboard-card artifact-card reveal">
              <div class="card-kicker">Artifact {index:02d}</div>
              <h3>{label}</h3>
              <img src="{Path(artifact).name}" alt="{label}" loading="lazy" />
            </article>
            """
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>LunaTrace Mission Experience</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Rajdhani:wght@400;500;600;700&display=swap');
    :root {{
      --bg-0: #000000;
      --bg-1: #020617;
      --bg-2: #0b1535;
      --panel: rgba(255,255,255,0.05);
      --panel-strong: rgba(8,15,34,0.74);
      --border: rgba(255,255,255,0.12);
      --text: #ffffff;
      --muted: #d1d5db;
      --soft: #94a3b8;
      --orange: #ff6a00;
      --orange-2: #ff8c1a;
      --blue: #2563eb;
      --blue-2: #60a5fa;
      --cyan: #22d3ee;
      --purple: #8b5cf6;
      --shadow: 0 10px 50px rgba(0,0,0,0.5);
      --radius: 28px;
      --max: 1400px;
      --font-display: "Michroma", "Arial Rounded MT Bold", sans-serif;
      --font-body: "Rajdhani", "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      color: var(--text);
      font-family: var(--font-body);
      background:
        radial-gradient(circle at 20% 0%, rgba(37,99,235,.22), transparent 25%),
        radial-gradient(circle at 85% 18%, rgba(255,106,0,.18), transparent 22%),
        radial-gradient(circle at 50% 90%, rgba(34,211,238,.12), transparent 28%),
        linear-gradient(180deg, #000000 0%, #020617 35%, #06112a 100%);
      overflow-x: hidden;
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      background-image:
        radial-gradient(2px 2px at 8% 14%, rgba(255,255,255,.82), transparent 60%),
        radial-gradient(1.5px 1.5px at 22% 62%, rgba(255,255,255,.58), transparent 60%),
        radial-gradient(2px 2px at 35% 18%, rgba(255,255,255,.72), transparent 60%),
        radial-gradient(1px 1px at 58% 12%, rgba(255,255,255,.48), transparent 60%),
        radial-gradient(2px 2px at 76% 28%, rgba(255,255,255,.76), transparent 60%),
        radial-gradient(1px 1px at 90% 66%, rgba(255,255,255,.62), transparent 60%),
        radial-gradient(2px 2px at 44% 84%, rgba(255,255,255,.7), transparent 60%),
        radial-gradient(1px 1px at 12% 88%, rgba(255,255,255,.52), transparent 60%);
      opacity: .9;
      pointer-events: none;
      z-index: -3;
    }}
    body::after {{
      content: "";
      position: fixed;
      inset: 0;
      background:
        linear-gradient(120deg, rgba(2,6,23,.65), rgba(2,6,23,.2)),
        url("{internal_bg}") center/cover no-repeat fixed;
      opacity: .12;
      pointer-events: none;
      z-index: -4;
      filter: saturate(1.08);
    }}
    a {{ color: inherit; }}
    img, video {{ display: block; max-width: 100%; }}
    .shell {{ position: relative; }}
    .orb {{
      position: fixed;
      border-radius: 999px;
      filter: blur(60px);
      opacity: .3;
      pointer-events: none;
      z-index: -2;
      animation: drift 16s ease-in-out infinite alternate;
    }}
    .orb-a {{ width: 260px; height: 260px; top: 8%; left: -4%; background: rgba(37,99,235,.35); }}
    .orb-b {{ width: 320px; height: 320px; top: 42%; right: -8%; background: rgba(255,106,0,.28); animation-duration: 22s; }}
    .orb-c {{ width: 200px; height: 200px; bottom: 8%; left: 18%; background: rgba(34,211,238,.2); animation-duration: 18s; }}
    .navbar {{
      position: fixed;
      top: 18px;
      left: 50%;
      transform: translateX(-50%);
      width: min(calc(100% - 32px), 1320px);
      padding: 16px 22px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      background: rgba(3,8,20,.48);
      backdrop-filter: blur(24px);
      border: 1px solid var(--border);
      border-radius: 999px;
      box-shadow: var(--shadow);
      z-index: 40;
      transition: padding .35s ease, background .35s ease, transform .35s ease;
    }}
    .navbar.compact {{
      padding: 10px 18px;
      background: rgba(3,8,20,.72);
    }}
    .brandlock {{
      display: flex;
      align-items: center;
      gap: 14px;
      min-width: 0;
    }}
    .brandmark {{
      width: 42px;
      height: 42px;
      border-radius: 16px;
      display: grid;
      place-items: center;
      background:
        linear-gradient(135deg, rgba(37,99,235,.95), rgba(255,106,0,.9));
      box-shadow: 0 0 34px rgba(37,99,235,.3);
      font-weight: 800;
      letter-spacing: .08em;
    }}
    .brandtext strong {{
      display: block;
      font-size: 15px;
      letter-spacing: .22em;
      text-transform: uppercase;
      font-family: var(--font-display);
    }}
    .brandtext span {{
      color: var(--soft);
      font-size: 12px;
      letter-spacing: .08em;
      text-transform: uppercase;
    }}
    .navlinks {{
      display: flex;
      align-items: center;
      gap: 18px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }}
    .navlinks a {{
      position: relative;
      text-decoration: none;
      color: var(--muted);
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: .12em;
      padding-bottom: 5px;
      font-family: var(--font-display);
    }}
    .navlinks a::after {{
      content: "";
      position: absolute;
      left: 0;
      bottom: 0;
      width: 100%;
      height: 2px;
      transform: scaleX(0);
      transform-origin: left;
      background: linear-gradient(90deg, var(--blue-2), var(--orange-2));
      transition: transform .3s ease;
    }}
    .navlinks a:hover::after,
    .navlinks a:focus-visible::after {{ transform: scaleX(1); }}
    .hero {{
      min-height: 100vh;
      display: grid;
      grid-template-columns: minmax(0, 1.02fr) minmax(420px, .98fr);
      align-items: stretch;
      padding-top: 102px;
      position: relative;
      isolation: isolate;
    }}
    .hero-panel {{
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 54px clamp(24px, 4vw, 64px);
      background:
        radial-gradient(circle at 25% 18%, rgba(37,99,235,.15), transparent 24%),
        radial-gradient(circle at 72% 86%, rgba(255,106,0,.08), transparent 22%),
        #000000;
    }}
    .hero-copy {{
      width: min(100%, 620px);
      position: relative;
      z-index: 2;
    }}
    .hero-kicker {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 10px 14px;
      border-radius: 999px;
      margin-bottom: 24px;
      border: 1px solid rgba(96,165,250,.28);
      background: rgba(10,20,45,.52);
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: .18em;
      font-size: 11px;
    }}
    .hero-kicker::before {{
      content: "";
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: linear-gradient(135deg, var(--cyan), var(--orange));
      box-shadow: 0 0 18px rgba(34,211,238,.8);
    }}
    .hero h1 {{
      margin: 0 0 20px;
      font-size: clamp(2.8rem, 5.8vw, 5.4rem);
      line-height: .96;
      letter-spacing: -.05em;
      text-transform: uppercase;
      font-family: var(--font-display);
    }}
    .gradient-blue {{
      background: linear-gradient(135deg, #dbeafe 0%, #60a5fa 30%, #2563eb 100%);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
    }}
    .gradient-orange {{
      background: linear-gradient(135deg, #fff7ed 0%, #ffb36b 32%, #ff6a00 100%);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
    }}
    .hero p {{
      color: var(--muted);
      font-size: 1.05rem;
      line-height: 1.9;
      max-width: 560px;
      margin: 0 0 28px;
    }}
    .cta-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 14px;
      margin-bottom: 28px;
    }}
    .cta {{
      text-decoration: none;
      min-width: 188px;
      padding: 15px 22px;
      border-radius: 999px;
      font-weight: 700;
      letter-spacing: .04em;
      transition: transform .28s ease, box-shadow .28s ease, border-color .28s ease;
    }}
    .cta:hover {{ transform: translateY(-2px); }}
    .cta-primary {{
      background: linear-gradient(135deg, var(--blue), var(--cyan));
      color: #fff;
      box-shadow: 0 18px 45px rgba(37,99,235,.32);
    }}
    .cta-secondary {{
      border: 1px solid rgba(255,255,255,.18);
      background: rgba(255,255,255,.05);
      color: #fff;
    }}
    .feature-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 22px;
      margin-top: 26px;
    }}
    .glass {{
      background: var(--panel);
      backdrop-filter: blur(24px);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }}
    .feature-card {{
      min-height: 200px;
      padding: 26px 20px 22px;
      position: relative;
      overflow: hidden;
      transition: transform .35s ease, border-color .35s ease, box-shadow .35s ease;
      border-radius: 26px;
      background:
        linear-gradient(180deg, rgba(78,120,255,.95) 0%, rgba(32,47,104,.72) 42%, rgba(5,10,25,.88) 100%);
      border: 1px solid rgba(255,255,255,.85);
      box-shadow: 0 18px 50px rgba(0,0,0,.35);
    }}
    .feature-card.warm {{
      background:
        linear-gradient(180deg, rgba(255,106,0,.96) 0%, rgba(110,47,8,.7) 44%, rgba(7,10,23,.9) 100%);
    }}
    .feature-card.cool {{
      background:
        linear-gradient(180deg, rgba(78,120,255,.95) 0%, rgba(37,55,132,.72) 42%, rgba(5,10,25,.88) 100%);
    }}
    .feature-card:hover,
    .dashboard-card:hover {{
      transform: translateY(-4px) scale(1.01);
      border-color: rgba(96,165,250,.24);
      box-shadow: 0 16px 55px rgba(0,0,0,.55);
    }}
    .feature-card::before {{
      content: "";
      position: absolute;
      inset: auto 0 0 0;
      height: 44%;
      background: linear-gradient(180deg, transparent, rgba(0,0,0,.52));
      pointer-events: none;
    }}
    .feature-card strong {{
      display: block;
      margin-bottom: 16px;
      font-size: clamp(1.45rem, 2vw, 2rem);
      line-height: 1.35;
      letter-spacing: .02em;
      text-transform: none;
      overflow-wrap: break-word;
      font-family: var(--font-display);
      text-align: center;
    }}
    .feature-card span {{
      color: rgba(255,255,255,.88);
      font-size: 1rem;
      line-height: 1.6;
      overflow-wrap: break-word;
      text-align: center;
      display: block;
    }}
    .scroll-indicator {{
      display: inline-flex;
      align-items: center;
      gap: 12px;
      margin-top: 26px;
      color: var(--soft);
      text-transform: uppercase;
      letter-spacing: .18em;
      font-size: 11px;
    }}
    .scroll-indicator::before {{
      content: "";
      width: 32px;
      height: 52px;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,.22);
      background:
        radial-gradient(circle at 50% 24%, rgba(255,255,255,.85) 0 4px, transparent 5px),
        linear-gradient(180deg, rgba(34,211,238,.45), rgba(255,106,0,.18));
      background-repeat: no-repeat;
      animation: scrollPulse 2.2s ease-in-out infinite;
    }}
    .hero-visual {{
      position: relative;
      overflow: hidden;
      min-height: calc(100vh - 102px);
      background: #020617;
    }}
    .hero-visual::before {{
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(90deg, #000 0%, rgba(0,0,0,.82) 10%, rgba(0,0,0,.3) 30%, rgba(0,0,0,.1) 100%);
      z-index: 2;
      pointer-events: none;
    }}
    .hero-visual::after {{
      content: "";
      position: absolute;
      inset: 0;
      background:
        radial-gradient(circle at 70% 18%, rgba(96,165,250,.18), transparent 22%),
        radial-gradient(circle at 56% 76%, rgba(255,106,0,.22), transparent 18%);
      z-index: 3;
      pointer-events: none;
      mix-blend-mode: screen;
    }}
    .hero-video {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transform: scale(1.06);
      animation: slowZoom 18s ease-in-out infinite alternate;
    }}
    .hero-overlay-card {{
      position: absolute;
      right: 42px;
      bottom: 38px;
      z-index: 4;
      width: min(340px, calc(100% - 48px));
      padding: 20px;
    }}
    .hero-overlay-card .eyebrow,
    .section-kicker,
    .card-kicker {{
      margin: 0 0 12px;
      color: var(--blue-2);
      text-transform: none;
      letter-spacing: .08em;
      font-size: 12px;
      line-height: 1.4;
    }}
    .hero-overlay-card h3 {{
      margin: 0 0 10px;
      font-size: 1.2rem;
      font-family: var(--font-display);
      line-height: 1.45;
    }}
    .hero-overlay-card p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.75;
      font-size: .96rem;
    }}
    .content {{
      position: relative;
      z-index: 2;
    }}
    .section-shell {{
      padding: 88px 24px;
      position: relative;
    }}
    .section-shell::before {{
      content: "";
      position: absolute;
      inset: 0;
      background:
        linear-gradient(180deg, rgba(2,6,23,.84), rgba(2,6,23,.68)),
        url("{transition_bg}") center/cover no-repeat fixed;
      opacity: .12;
      z-index: -1;
    }}
    .section-inner {{
      max-width: var(--max);
      margin: 0 auto;
    }}
    .section-header {{
      max-width: 760px;
      margin-bottom: 36px;
    }}
    .section-header h2 {{
      margin: 0 0 14px;
      font-size: clamp(2.2rem, 4vw, 4rem);
      line-height: .96;
      text-transform: none;
      letter-spacing: 0;
      font-family: var(--font-display);
    }}
    .section-header h2.gradient-title {{
      background: linear-gradient(90deg, #bcd3ff, #dce7ff 45%, #ffb87d 92%);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
    }}
    .section-header p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.9;
      font-size: 1rem;
    }}
    .story-row {{
      min-height: 84vh;
      display: grid;
      grid-template-columns: minmax(0, 1.04fr) minmax(380px, .96fr);
      gap: clamp(22px, 4vw, 48px);
      align-items: center;
    }}
    .story-row.reverse .visual-panel {{ order: 2; }}
    .story-row.reverse .copy-panel {{ order: 1; }}
    .visual-panel {{
      position: relative;
      padding: 18px;
    }}
    .visual-stage {{
      position: relative;
      overflow: visible;
      min-height: 460px;
      padding: clamp(18px, 3vw, 28px);
      display: grid;
      gap: 18px;
      background:
        linear-gradient(145deg, rgba(8,15,34,.82), rgba(8,15,34,.48)),
        url("{landing_bg}") center/cover no-repeat;
    }}
    .visual-figure {{
      position: relative;
      overflow: hidden;
      border-radius: 22px;
    }}
    .visual-stage img {{
      width: 100%;
      height: auto;
      border-radius: 22px;
      border: 1px solid rgba(255,255,255,.1);
      box-shadow: 0 24px 70px rgba(0,0,0,.42);
      object-fit: cover;
    }}
    .visual-stage.asset-stage::after {{
      content: "";
      position: absolute;
      inset: auto 20px 20px auto;
      width: 34%;
      height: 34%;
      background: radial-gradient(circle, rgba(255,106,0,.2), transparent 70%);
      filter: blur(18px);
      pointer-events: none;
    }}
    .visual-caption {{
      position: relative;
      left: auto;
      bottom: auto;
      width: min(420px, 100%);
      padding: 18px;
      z-index: 2;
    }}
    .visual-caption strong {{
      display: block;
      margin-bottom: 8px;
      font-size: 1rem;
    }}
    .visual-caption span {{
      color: var(--muted);
      line-height: 1.7;
      font-size: .95rem;
    }}
    .hotspot {{
      position: absolute;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: var(--cyan);
      box-shadow: 0 0 0 0 rgba(34,211,238,.75);
      animation: ping 2.2s ease-out infinite;
    }}
    .hotspot.one {{ top: 34%; left: 64%; }}
    .hotspot.two {{ top: 60%; left: 24%; animation-delay: .8s; }}
    .hotspot.three {{ top: 22%; left: 78%; animation-delay: 1.4s; }}
    .artifact-frame {{
      position: relative;
      right: auto;
      bottom: auto;
      width: min(48%, 420px);
      padding: 14px;
      margin-left: auto;
      z-index: 2;
    }}
    .artifact-frame img {{
      border-radius: 18px;
      background: rgba(1,4,10,.86);
      object-fit: contain;
    }}
    .copy-panel {{
      padding: 14px 0;
    }}
    .copy-panel h3 {{
      margin: 0 0 16px;
      font-size: clamp(2rem, 3.4vw, 3.3rem);
      line-height: .98;
      text-transform: none;
      letter-spacing: 0;
      font-family: var(--font-display);
    }}
    .copy-panel p {{
      color: var(--muted);
      line-height: 1.9;
      font-size: 1rem;
      margin: 0 0 18px;
    }}
    .bullet-list {{
      display: grid;
      gap: 12px;
      margin: 22px 0 28px;
    }}
    .bullet-item {{
      display: flex;
      gap: 12px;
      align-items: flex-start;
      padding: 14px 16px;
      border-radius: 20px;
      background: rgba(255,255,255,.03);
      border: 1px solid rgba(255,255,255,.08);
    }}
    .bullet-item::before {{
      content: "";
      width: 10px;
      height: 10px;
      margin-top: 8px;
      border-radius: 999px;
      background: linear-gradient(135deg, var(--orange-2), var(--blue-2));
      box-shadow: 0 0 18px rgba(255,106,0,.4);
      flex: none;
    }}
    .metric-strip {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 24px;
    }}
    .metric-chip {{
      padding: 16px;
      border-radius: 22px;
      background: linear-gradient(180deg, rgba(64,89,184,.5), rgba(6,11,24,.72));
      border: 1px solid rgba(255,255,255,.6);
    }}
    .metric-chip .label {{
      display: block;
      color: var(--soft);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .16em;
      margin-bottom: 8px;
    }}
    .metric-chip strong {{
      font-size: clamp(1.05rem, 2vw, 1.3rem);
      line-height: 1.35;
      overflow-wrap: break-word;
    }}
    .resource-stack {{
      display: grid;
      gap: 14px;
      margin-top: 24px;
    }}
    .resource-band {{
      padding: 18px 20px;
      border-radius: 24px;
      border: 1px solid rgba(255,255,255,.08);
      background:
        linear-gradient(90deg, rgba(37,99,235,.14), rgba(255,106,0,.08)),
        rgba(255,255,255,.03);
    }}
    .resource-band span {{
      display: block;
      color: var(--soft);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .16em;
      margin-bottom: 8px;
    }}
    .resource-band strong {{
      font-size: 1.15rem;
      line-height: 1.5;
      overflow-wrap: break-word;
    }}
    .traverse-stage {{
      overflow: hidden;
    }}
    .traverse-line {{
      position: absolute;
      left: 9%;
      right: 12%;
      bottom: 18%;
      height: 6px;
      border-radius: 999px;
      background: rgba(34,211,238,.16);
      overflow: hidden;
      z-index: 2;
    }}
    .traverse-progress {{
      width: 0%;
      height: 100%;
      background: linear-gradient(90deg, #22d3ee, #60a5fa);
      box-shadow: 0 0 24px rgba(34,211,238,.7);
      transition: width 2.4s cubic-bezier(.2,.8,.2,1);
    }}
    .rover-marker {{
      position: absolute;
      left: 9%;
      bottom: calc(18% - 10px);
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: linear-gradient(135deg, #fff, #60a5fa);
      border: 2px solid rgba(255,255,255,.5);
      box-shadow: 0 0 24px rgba(96,165,250,.8);
      z-index: 3;
      transition: left 2.4s cubic-bezier(.2,.8,.2,1);
    }}
    .hazard-legend,
    .ops-grid,
    .dashboard-grid,
    .report-grid {{
      display: grid;
      gap: 16px;
    }}
    .hazard-legend {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
      margin-top: 24px;
    }}
    .legend-card,
    .dashboard-card {{
      padding: 20px;
    }}
    .legend-card,
    .dashboard-card,
    .artifact-card,
    .resource-band,
    .dashboard-metric {{
      background:
        linear-gradient(180deg, rgba(15,26,58,.88) 0%, rgba(7,12,24,.92) 100%);
      border: 1px solid rgba(255,255,255,.62);
      box-shadow: 0 18px 42px rgba(0,0,0,.32);
    }}
    .legend-swatch {{
      width: 100%;
      height: 10px;
      border-radius: 999px;
      margin-bottom: 12px;
    }}
    .legend-red {{ background: linear-gradient(90deg, rgba(239,68,68,.35), rgba(220,38,38,.95)); }}
    .legend-yellow {{ background: linear-gradient(90deg, rgba(250,204,21,.32), rgba(234,179,8,.96)); }}
    .legend-blue {{ background: linear-gradient(90deg, rgba(34,211,238,.32), rgba(59,130,246,.96)); }}
    .legend-card h4,
    .dashboard-card h3 {{
      margin: 0 0 8px;
      font-size: .98rem;
      text-transform: none;
      letter-spacing: .02em;
      line-height: 1.45;
      overflow-wrap: break-word;
      font-family: var(--font-display);
    }}
    .legend-card p,
    .dashboard-card p,
    .dashboard-card li {{
      color: var(--muted);
      line-height: 1.75;
      margin: 0;
      overflow-wrap: break-word;
      word-break: normal;
    }}
    .ops-grid {{
      grid-template-columns: repeat(4, minmax(0, 1fr));
      margin-top: 26px;
    }}
    .ops-grid .metric-chip {{ min-height: 118px; }}
    .button-inline {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 14px 20px;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,.14);
      background: linear-gradient(135deg, rgba(37,99,235,.16), rgba(34,211,238,.12));
      color: #fff;
      cursor: pointer;
      font: inherit;
      transition: transform .25s ease, border-color .25s ease;
    }}
    .button-inline:hover {{ transform: translateY(-2px); border-color: rgba(96,165,250,.35); }}
    .dashboard-shell {{
      padding-top: 16px;
    }}
    .dashboard-metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .dashboard-metric {{
      padding: 20px;
      min-height: 160px;
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 12px;
    }}
    .dashboard-metric::before {{
      content: "";
      position: absolute;
      inset: auto -18% -28% auto;
      width: 150px;
      height: 150px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(255,106,0,.18), transparent 70%);
      pointer-events: none;
    }}
    .dashboard-metric .metric-label {{
      color: var(--soft);
      font-size: 12px;
      text-transform: none;
      letter-spacing: .08em;
      line-height: 1.45;
      overflow-wrap: break-word;
    }}
    .dashboard-metric .metric-value {{
      margin-top: 18px;
      font-size: clamp(1.65rem, 2.6vw, 2.7rem);
      font-weight: 800;
      line-height: 1.15;
      overflow-wrap: break-word;
    }}
    .dashboard-grid {{
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
    .dashboard-card ul {{
      margin: 0;
      padding-left: 18px;
      display: grid;
      gap: 10px;
    }}
    .dashboard-card table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
    }}
    .dashboard-card th,
    .dashboard-card td {{
      padding: 10px 0;
      border-bottom: 1px solid rgba(255,255,255,.08);
      text-align: left;
      color: var(--muted);
      font-size: .95rem;
    }}
    .dashboard-card th {{ color: #fff; font-size: .8rem; text-transform: uppercase; letter-spacing: .14em; }}
    .artifact-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
      margin-top: 24px;
    }}
    .artifact-card img {{
      width: 100%;
      margin-top: 16px;
      padding: 12px;
      border-radius: 20px;
      border: 1px solid rgba(255,255,255,.08);
      background: rgba(1,4,10,.82);
    }}
    .artifact-card {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .report-grid {{
      grid-template-columns: repeat(2, minmax(0, 1fr));
      margin-top: 24px;
    }}
    .link-card {{
      text-decoration: none;
      padding: 24px;
      display: block;
      transition: transform .28s ease, border-color .28s ease;
    }}
    .link-card:hover {{ transform: translateY(-3px); border-color: rgba(255,140,26,.3); }}
    .link-card strong {{
      display: block;
      margin-bottom: 10px;
      font-size: 1.1rem;
      text-transform: none;
      letter-spacing: .02em;
      font-family: var(--font-display);
    }}
    .reference-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 22px;
      margin-top: 30px;
    }}
    .reference-card {{
      min-height: 310px;
      padding: 30px 26px;
      border-radius: 26px;
      border: 1px solid rgba(255,255,255,.88);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: 0 24px 64px rgba(0,0,0,.34);
    }}
    .reference-card.blue {{
      background:
        linear-gradient(180deg, rgba(86,117,255,.96) 0%, rgba(35,49,116,.72) 42%, rgba(5,10,24,.94) 100%);
    }}
    .reference-card.orange {{
      background:
        linear-gradient(180deg, rgba(255,111,16,.97) 0%, rgba(124,52,10,.72) 42%, rgba(8,10,23,.94) 100%);
    }}
    .reference-card h3 {{
      margin: 0 0 18px;
      font-family: var(--font-display);
      font-size: clamp(1.3rem, 2vw, 1.85rem);
      line-height: 1.55;
      font-weight: 400;
      text-align: center;
    }}
    .reference-card p {{
      margin: 0;
      font-size: 1rem;
      line-height: 1.65;
      text-align: center;
      color: rgba(255,255,255,.9);
    }}
    .process-row {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 24px;
      margin-top: 36px;
      align-items: start;
    }}
    .process-step {{
      position: relative;
      text-align: center;
      padding: 0 10px;
    }}
    .process-step::before {{
      content: "";
      position: absolute;
      top: 42px;
      left: calc(-50% + 44px);
      width: calc(100% - 12px);
      height: 2px;
      background: linear-gradient(90deg, rgba(255,140,26,.2), rgba(255,140,26,.75), rgba(255,140,26,.2));
    }}
    .process-step:first-child::before {{
      display: none;
    }}
    .process-icon {{
      width: 88px;
      height: 88px;
      margin: 0 auto 18px;
      display: grid;
      place-items: center;
      color: #ff8c1a;
      font-size: 2.6rem;
      border-radius: 50%;
      border: 2px solid rgba(255,140,26,.8);
      background: radial-gradient(circle, rgba(255,140,26,.12), rgba(4,10,22,.2));
      box-shadow: 0 0 38px rgba(255,140,26,.18);
    }}
    .process-step h3 {{
      margin: 0 0 12px;
      font-family: var(--font-display);
      font-size: 1.15rem;
      line-height: 1.55;
      color: #fff;
      font-weight: 400;
    }}
    .process-step p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.7;
      font-size: .98rem;
    }}
    .link-card span {{
      color: var(--muted);
      line-height: 1.8;
    }}
    .reveal {{
      opacity: 0;
      transform: translateY(40px) scale(.98);
      filter: blur(12px);
      transition: opacity .9s ease, transform .9s ease, filter .9s ease;
    }}
    .reveal.is-visible {{
      opacity: 1;
      transform: translateY(0) scale(1);
      filter: blur(0);
    }}
    @keyframes slowZoom {{
      from {{ transform: scale(1.05) translate3d(0, 0, 0); }}
      to {{ transform: scale(1.12) translate3d(1%, -1%, 0); }}
    }}
    @keyframes scrollPulse {{
      0%, 100% {{ background-position: center 12px, center; }}
      50% {{ background-position: center 26px, center; }}
    }}
    @keyframes ping {{
      0% {{ box-shadow: 0 0 0 0 rgba(34,211,238,.75); }}
      70% {{ box-shadow: 0 0 0 20px rgba(34,211,238,0); }}
      100% {{ box-shadow: 0 0 0 0 rgba(34,211,238,0); }}
    }}
    @keyframes drift {{
      from {{ transform: translate3d(0, 0, 0); }}
      to {{ transform: translate3d(40px, -24px, 0); }}
    }}
    @media (max-width: 1180px) {{
      .hero,
      .story-row {{
        grid-template-columns: 1fr;
      }}
      .hero-visual {{
        min-height: 58vh;
      }}
      .story-row.reverse .visual-panel,
      .story-row.reverse .copy-panel {{
        order: initial;
      }}
      .dashboard-metrics,
      .ops-grid,
      .metric-strip {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}
    @media (max-width: 860px) {{
      .navbar {{
        width: calc(100% - 20px);
        padding: 14px 16px;
        border-radius: 28px;
        align-items: flex-start;
        flex-direction: column;
      }}
      .navlinks {{
        width: 100%;
        justify-content: flex-start;
        gap: 12px 16px;
      }}
      .hero {{
        padding-top: 132px;
      }}
      .feature-grid,
      .dashboard-grid,
      .artifact-grid,
      .report-grid,
      .hazard-legend,
      .dashboard-metrics,
      .ops-grid,
      .metric-strip,
      .reference-grid,
      .process-row {{
        grid-template-columns: 1fr;
      }}
      .process-step::before {{
        display: none;
      }}
      .hero-overlay-card,
      .artifact-frame {{
        position: static;
        width: 100%;
        margin-top: 18px;
      }}
      .visual-caption {{
        position: static;
        width: 100%;
        margin-top: 18px;
      }}
      .visual-stage {{
        min-height: 360px;
      }}
      .visual-caption {{
        width: 100%;
      }}
      .artifact-frame {{
        width: 100%;
        margin-left: 0;
      }}
      .section-shell {{
        padding: 72px 18px;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <div class="orb orb-a"></div>
    <div class="orb orb-b"></div>
    <div class="orb orb-c"></div>

    <header class="navbar" id="navbar">
      <div class="brandlock">
        <div class="brandmark">LT</div>
        <div class="brandtext">
          <strong>LunaTrace</strong>
          <span>Lunar Mission Intelligence</span>
        </div>
      </div>
      <nav class="navlinks">
        <a href="#home">Home</a>
        <a href="#mission">Mission</a>
        <a href="#dashboard">Dashboard</a>
        <a href="#analysis">Analysis</a>
        <a href="#reports">Reports</a>
        <a href="#docs">Docs</a>
      </nav>
    </header>

    <main>
      <section class="hero" id="home">
        <div class="hero-panel">
          <div class="hero-copy reveal">
            <div class="hero-kicker">ISRO-style lunar command interface</div>
            <h1>
              <span class="gradient-blue">LunaTrace</span><br />
              <span>Subsurface </span><span class="gradient-orange">Ice</span><br />
              <span class="gradient-orange">Intelligence</span><br />
              <span>for Lunar Missions</span>
            </h1>
            <p>
              Physics-first lunar ice detection, Bayesian inference, terrain-aware landing analysis,
              and rover mission planning designed for a mission-control grade walkthrough.
            </p>
            <div class="cta-row">
              <a class="cta cta-primary" href="#mission">Explore Mission</a>
              <a class="cta cta-secondary" href="#dashboard">Launch Dashboard</a>
            </div>
            <div class="feature-grid">
              <article class="feature-card warm reveal">
                <strong>Learn from Mission Physics</strong>
                <span>Forward scattering logic grounds interpretation before any inversion or scoring.</span>
              </article>
              <article class="feature-card cool reveal">
                <strong>Dual-Band Radar Depth</strong>
                <span>L-band and S-band depth behavior stay visible all the way through the mission story.</span>
              </article>
              <article class="feature-card warm reveal">
                <strong>Network and Collaborate</strong>
                <span>Posterior confidence highlights where baseline-only calls can mislead the mission team.</span>
              </article>
              <article class="feature-card cool reveal">
                <strong>Mission-Grade Planning</strong>
                <span>Landing, hazards, energy, and traverse timing stay tied to the resource opportunity.</span>
              </article>
            </div>
            <div class="scroll-indicator">Scroll to mission layers</div>
          </div>
        </div>
        <div class="hero-visual">
          <video class="hero-video" autoplay muted loop playsinline preload="auto" poster="{landing_bg}">
            <source src="{visual_assets['hero_video']}" type="video/mp4" />
          </video>
          <div class="hero-overlay-card glass reveal">
            <div class="eyebrow">Mission narrative</div>
            <h3>Cinematic entry into lunar subsurface intelligence</h3>
            <p>
              Uploaded motion and science assets are staged as a premium launch experience without touching the underlying analysis logic.
            </p>
          </div>
        </div>
      </section>

      <div class="content">
        <section class="section-shell" id="mission">
          <div class="section-inner">
            <div class="section-header reveal">
              <div class="section-kicker">Mission Story</div>
              <h2 class="gradient-title">Why LunaTrace?</h2>
              <p>
                A mission-control style experience for detection, uncertainty, terrain analysis, landing intelligence, and rover execution.
              </p>
            </div>

            <div class="reference-grid">
              <article class="reference-card orange reveal">
                <h3>Physics-First Lunar Interpretation</h3>
                <p>Build confidence from explainable radar behavior before moving into posterior reasoning or landing decisions.</p>
              </article>
              <article class="reference-card blue reveal">
                <h3>Potential Mission Value from Ice Screening</h3>
                <p>Stand up a clearer understanding of subsurface opportunity using dual-band logic, volume estimates, and uncertainty tracking.</p>
              </article>
              <article class="reference-card orange reveal">
                <h3>Decision-Centered Team Collaboration</h3>
                <p>Connect scientists, judges, and operators through one navigable story instead of fragmented technical plots.</p>
              </article>
              <article class="reference-card blue reveal">
                <h3>National-Level Mission Readiness</h3>
                <p>Showcase a coherent end-to-end platform for lunar mission planning with stronger visual and analytical credibility.</p>
              </article>
            </div>

            <div class="section-header reveal" style="margin-top: 72px;">
              <h2 class="gradient-title" style="background: linear-gradient(90deg, #fff1e2, #ffbf8c 35%, #ff8c1a 90%); -webkit-background-clip: text; background-clip: text; color: transparent;">How the Mission Flows?</h2>
            </div>

            <div class="process-row">
              <article class="process-step reveal">
                <div class="process-icon">&#128208;</div>
                <h3>Register the Signals</h3>
                <p>Collect radar evidence, baseline inputs, and lunar terrain context into one science workflow.</p>
              </article>
              <article class="process-step reveal">
                <div class="process-icon">&#128101;</div>
                <h3>Form the Mission View</h3>
                <p>Merge physics, Bayesian reasoning, and hazard analysis into a shared operational picture.</p>
              </article>
              <article class="process-step reveal">
                <div class="process-icon">&#9651;</div>
                <h3>Choose the Best Target</h3>
                <p>Select the most promising crater sectors and landing candidates from evidence-backed rankings.</p>
              </article>
              <article class="process-step reveal">
                <div class="process-icon">&#128640;</div>
                <h3>Innovate and Traverse</h3>
                <p>Turn landing intelligence into rover-safe movement with energy, timing, and hazard awareness.</p>
              </article>
              <article class="process-step reveal">
                <div class="process-icon">&#128161;</div>
                <h3>Submit the Decision</h3>
                <p>Deliver a polished mission narrative with visuals, metrics, and artifacts ready for expert review.</p>
              </article>
            </div>

            <div class="section-header reveal" style="margin-top: 84px;">
              <div class="section-kicker">Deep Dive</div>
              <h2>From radar physics to rover execution</h2>
              <p>
                Each major capability gets a near full-screen storytelling row with visuals, scientific context, and mission-relevant takeaways.
              </p>
            </div>

            <div class="story-row reveal">
              <div class="visual-panel">
                <div class="visual-stage glass asset-stage">
                  <div class="visual-figure">
                    <img src="{visual_assets['moon_hotspot']}" alt="Moon hotspot analysis visual" loading="lazy" />
                    <div class="hotspot one"></div>
                    <div class="hotspot two"></div>
                    <div class="hotspot three"></div>
                  </div>
                  <div class="visual-caption glass">
                    <strong>Why LunaTrace</strong>
                    <span>Glowing lunar hotspots turn complex resource screening into a clear mission story for judges and operators.</span>
                  </div>
                </div>
              </div>
              <div class="copy-panel">
                <div class="section-kicker">01 / Why LunaTrace</div>
                <h3>Mission-control clarity for subsurface ice intelligence</h3>
                <p>
                  LunaTrace connects detection, uncertainty, safety, and traversal into one deliberate operational narrative instead of isolated plots.
                </p>
                <div class="bullet-list">
                  <div class="bullet-item">Physics-grounded interpretation rather than black-box scoring.</div>
                  <div class="bullet-item">Mission-readiness tied to safe access, not just peak probability.</div>
                  <div class="bullet-item">Premium storytelling layer built around the uploaded moon and rover visuals.</div>
                </div>
                <div class="metric-strip">
                  <div class="metric-chip glass">
                    <span class="label">Expected Ice</span>
                    <strong>{cubic_meters(payload.get("resource_summary", {}).get("expected_ice_m3", "N/A"))}</strong>
                  </div>
                  <div class="metric-chip glass">
                    <span class="label">Peak Posterior</span>
                    <strong>{format_value(payload.get("detection_summary", {}).get("peak_posterior", "N/A"), 4)}</strong>
                  </div>
                  <div class="metric-chip glass">
                    <span class="label">Top Site</span>
                    <strong>{payload.get("top_site", {}).get("site", "N/A")}</strong>
                  </div>
                </div>
              </div>
            </div>

            <div class="story-row reverse reveal">
              <div class="visual-panel">
                <div class="visual-stage glass">
                  <div class="visual-figure">
                    <img src="{Path(payload.get('artifacts', [''])[0]).name}" alt="Forward radar model artifact" loading="lazy" />
                  </div>
                  <div class="visual-caption glass">
                    <strong>Forward Radar Model</strong>
                    <span>The model explains the scene before the platform interprets it, making later decisions easier to defend.</span>
                  </div>
                </div>
              </div>
              <div class="copy-panel">
                <div class="section-kicker">02 / Forward Radar Model</div>
                <h3>Physics-first signatures before inference</h3>
                <p>
                  The radar layer is presented as a mission instrument rather than a static chart. This section foregrounds how surface and subsurface structure shape the response field.
                </p>
                <div class="bullet-list">
                  <div class="bullet-item">Preserves the generated forward-model artifact exactly as produced by the backend.</div>
                  <div class="bullet-item">Adds cinematic framing, scan-line atmosphere, and larger visual hierarchy.</div>
                  <div class="bullet-item">Prepares users to trust the dual-band and posterior stages that follow.</div>
                </div>
              </div>
            </div>

            <div class="story-row reveal">
              <div class="visual-panel">
                <div class="visual-stage glass asset-stage">
                  <div class="visual-figure">
                    <img src="{visual_assets['rover_moon']}" alt="Rover and moon visual" loading="lazy" />
                  </div>
                  <div class="artifact-frame glass">
                    <img src="{Path(payload.get('artifacts', ['', ''])[1]).name}" alt="Dual band depth artifact" loading="lazy" />
                  </div>
                </div>
              </div>
              <div class="copy-panel">
                <div class="section-kicker">03 / Dual Band Detection</div>
                <h3>L-band and S-band depth behavior made legible</h3>
                <p>
                  Instead of burying the dual-band comparison in a small chart, LunaTrace frames it as a depth argument that directly informs mission confidence.
                </p>
                <div class="metric-strip">
                  <div class="metric-chip glass">
                    <span class="label">L-Band Depth</span>
                    <strong>{format_value(payload.get("penetration_depths_m", {}).get("l", "N/A"), 2)} m</strong>
                  </div>
                  <div class="metric-chip glass">
                    <span class="label">S-Band Depth</span>
                    <strong>{format_value(payload.get("penetration_depths_m", {}).get("s", "N/A"), 2)} m</strong>
                  </div>
                  <div class="metric-chip glass">
                    <span class="label">Metadata Count</span>
                    <strong>{payload.get("detection_summary", {}).get("radar_metadata_count", "N/A")}</strong>
                  </div>
                </div>
              </div>
            </div>

            <div class="story-row reverse reveal">
              <div class="visual-panel">
                <div class="visual-stage glass asset-stage">
                  <div class="visual-figure">
                    <img src="{visual_assets['astronaut']}" alt="Astronaut on lunar surface" loading="lazy" />
                  </div>
                  <div class="artifact-frame glass">
                    <img src="{Path(payload.get('artifacts', ['', '', ''])[2]).name}" alt="Posterior versus baseline artifact" loading="lazy" />
                  </div>
                </div>
              </div>
              <div class="copy-panel">
                <div class="section-kicker">04 / Bayesian Posterior</div>
                <h3>Uncertainty stays visible in the decision loop</h3>
                <p>
                  The posterior story is paired with the astronaut visual to make the analysis feel operational and human-centered rather than abstract.
                </p>
                <div class="resource-stack">
                  <div class="resource-band">
                    <span>Information Value</span>
                    <strong>{format_value(payload.get("detection_summary", {}).get("entropy_information_value", "N/A"), 4)}</strong>
                  </div>
                  <div class="resource-band">
                    <span>Posterior Delta</span>
                    <strong>{format_value(payload.get("detection_summary", {}).get("entropy_posterior_delta", "N/A"), 4)}</strong>
                  </div>
                  <div class="resource-band">
                    <span>Sensitivity Note</span>
                    <strong>{payload.get("sensitivity_note", "N/A")}</strong>
                  </div>
                </div>
              </div>
            </div>

            <div class="story-row reveal">
              <div class="visual-panel">
                <div class="visual-stage glass">
                  <div class="visual-figure">
                    <img src="{Path(payload.get('artifacts', ['', '', '', ''])[3]).name}" alt="Hazard morphology artifact" loading="lazy" />
                  </div>
                </div>
              </div>
              <div class="copy-panel">
                <div class="section-kicker">05 / Terrain Hazard Analysis</div>
                <h3>Safe, moderate, and dangerous terrain made immediate</h3>
                <p>
                  Hazard morphology is elevated into its own cinematic analysis layer so slope, boulder exposure, and access risk read instantly during a walkthrough.
                </p>
                <div class="hazard-legend">
                  <div class="legend-card glass">
                    <div class="legend-swatch legend-red"></div>
                    <h4>Danger</h4>
                    <p>High-risk regions where slope and obstruction amplify mission cost.</p>
                  </div>
                  <div class="legend-card glass">
                    <div class="legend-swatch legend-yellow"></div>
                    <h4>Moderate</h4>
                    <p>Watch zones that remain reachable but may compress margins.</p>
                  </div>
                  <div class="legend-card glass">
                    <div class="legend-swatch legend-blue"></div>
                    <h4>Safe</h4>
                    <p>Preferred corridors that support landing and traverse continuity.</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="story-row reverse reveal">
              <div class="visual-panel">
                <div class="visual-stage glass asset-stage">
                  <div class="visual-figure">
                    <img src="{visual_assets['moon_hotspot']}" alt="Resource estimation hotspot visual" loading="lazy" />
                  </div>
                  <div class="visual-caption glass">
                    <strong>Resource Estimation</strong>
                    <span>Expected yield and uncertainty remain prominent without hiding the supporting science.</span>
                  </div>
                </div>
              </div>
              <div class="copy-panel">
                <div class="section-kicker">06 / Resource Estimation</div>
                <h3>Expected ice volume translated into mission value</h3>
                <p>
                  Resource estimates are expressed as mission-ready numbers while keeping the dominant uncertainty explicit for technical credibility.
                </p>
                <div class="resource-stack">
                  <div class="resource-band">
                    <span>Expected Ice</span>
                    <strong>{cubic_meters(payload.get("resource_summary", {}).get("expected_ice_m3", "N/A"))}</strong>
                  </div>
                  <div class="resource-band">
                    <span>Water Yield</span>
                    <strong>{cubic_meters(payload.get("resource_summary", {}).get("water_yield_expected_m3", "N/A"))}</strong>
                  </div>
                  <div class="resource-band">
                    <span>Dominant Uncertainty</span>
                    <strong>{payload.get("resource_summary", {}).get("dominant_uncertainty", "N/A")}</strong>
                  </div>
                </div>
              </div>
            </div>

            <div class="story-row reveal">
              <div class="visual-panel">
                <div class="visual-stage glass asset-stage">
                  <div class="visual-figure">
                    <img src="{visual_assets['rover_moon']}" alt="Rover near large moon horizon" loading="lazy" />
                  </div>
                  <div class="artifact-frame glass">
                    <img src="{Path(payload.get('artifacts', ['', '', '', '', ''])[4]).name}" alt="Landing site artifact" loading="lazy" />
                  </div>
                </div>
              </div>
              <div class="copy-panel">
                <div class="section-kicker">07 / Landing Site Selection</div>
                <h3>Safe landing zones ranked with operational context</h3>
                <p>
                  The landing sequence is framed like a mission briefing, pairing the site-ranking artifact with the uploaded rover-and-moon visual.
                </p>
                <div class="metric-strip">
                  <div class="metric-chip glass">
                    <span class="label">Top Site</span>
                    <strong>{payload.get("top_site", {}).get("site", "N/A")}</strong>
                  </div>
                  <div class="metric-chip glass">
                    <span class="label">Grid Position</span>
                    <strong>({payload.get("top_site", {}).get("row", "N/A")}, {payload.get("top_site", {}).get("col", "N/A")})</strong>
                  </div>
                  <div class="metric-chip glass">
                    <span class="label">Landing Score</span>
                    <strong>{format_value(payload.get("top_site", {}).get("score", "N/A"), 4)}</strong>
                  </div>
                </div>
              </div>
            </div>

            <div class="story-row reverse reveal" id="analysis">
              <div class="visual-panel">
                <div class="visual-stage glass asset-stage traverse-stage">
                  <div class="visual-figure">
                    <img src="{visual_assets['rover_path']}" alt="Rover traverse with glowing path" loading="lazy" />
                    <div class="traverse-line"><div class="traverse-progress" id="traverse-progress"></div></div>
                    <div class="rover-marker" id="rover-marker"></div>
                  </div>
                  <div class="artifact-frame glass">
                    <img src="{Path(payload.get('artifacts', ['', '', '', '', '', ''])[5]).name}" alt="Traverse map artifact" loading="lazy" />
                  </div>
                </div>
              </div>
              <div class="copy-panel">
                <div class="section-kicker">08 / Rover Traverse</div>
                <h3>Traverse simulation anchored to energy, safety, and time</h3>
                <p>
                  The uploaded rover-path artwork becomes the cinematic backbone for the final operational section, while the backend-generated traverse artifact stays fully visible.
                </p>
                <div class="ops-grid">
                  <div class="metric-chip glass">
                    <span class="label">Traverse Status</span>
                    <strong>{payload.get("traverse_summary", {}).get("status", "N/A")}</strong>
                  </div>
                  <div class="metric-chip glass">
                    <span class="label">Round Trip Energy</span>
                    <strong>{payload.get("traverse_summary", {}).get("round_trip_energy_wh", "N/A")} Wh</strong>
                  </div>
                  <div class="metric-chip glass">
                    <span class="label">Dwell Margin</span>
                    <strong>{payload.get("traverse_summary", {}).get("dwell_margin_hr", "N/A")} hr</strong>
                  </div>
                  <div class="metric-chip glass">
                    <span class="label">Binding Constraint</span>
                    <strong>{payload.get("traverse_summary", {}).get("binding_constraint", "N/A")}</strong>
                  </div>
                </div>
                <div class="cta-row" style="margin-top: 28px; margin-bottom: 0;">
                  <button class="button-inline" id="simulate-traverse" type="button">Simulate Traverse</button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="section-shell" id="dashboard">
          <div class="section-inner dashboard-shell">
            <div class="section-header reveal">
              <div class="section-kicker">Command Dashboard</div>
              <h2>Existing analysis preserved, reframed as premium mission ops</h2>
              <p>
                Every existing metric, ranking, note, and artifact remains intact. The update changes presentation, spacing, and interaction without altering the backend logic.
              </p>
            </div>

            <div class="dashboard-metrics">
              <article class="dashboard-metric glass reveal">
                <div class="metric-label">Expected Ice</div>
                <div class="metric-value">{cubic_meters(payload.get("resource_summary", {}).get("expected_ice_m3", "N/A"))}</div>
              </article>
              <article class="dashboard-metric glass reveal">
                <div class="metric-label">Water Yield</div>
                <div class="metric-value">{cubic_meters(payload.get("resource_summary", {}).get("water_yield_expected_m3", "N/A"))}</div>
              </article>
              <article class="dashboard-metric glass reveal">
                <div class="metric-label">Traverse Energy</div>
                <div class="metric-value">{payload.get("traverse_summary", {}).get("round_trip_energy_wh", "N/A")}</div>
              </article>
              <article class="dashboard-metric glass reveal">
                <div class="metric-label">Dwell Margin</div>
                <div class="metric-value">{payload.get("traverse_summary", {}).get("dwell_margin_hr", "N/A")}</div>
              </article>
            </div>

            <div class="dashboard-grid">
              <article class="dashboard-card glass reveal">
                <div class="card-kicker">Story Beats</div>
                <h3>Why this is competitive</h3>
                <ul>{story}</ul>
              </article>
              <article class="dashboard-card glass reveal">
                <div class="card-kicker">Landing Ranking</div>
                <h3>Best landing candidates</h3>
                <table>
                  <tr><th>Site</th><th>Score</th><th>Grid</th></tr>
                  {rankings}
                </table>
              </article>
              <article class="dashboard-card glass reveal">
                <div class="card-kicker">Traverse Costs</div>
                <h3>Operational cost breakdown</h3>
                <table>
                  <tr><th>Term</th><th>Value</th></tr>
                  {cost_rows}
                </table>
              </article>
              <article class="dashboard-card glass reveal">
                <div class="card-kicker">Decision Notes</div>
                <h3>Mission logic</h3>
                <p><strong>Weight sensitivity:</strong> {payload.get("sensitivity_note", "N/A")}</p>
                <p style="margin-top: 14px;"><strong>Binding constraint:</strong> {payload.get("traverse_summary", {}).get("binding_constraint", "N/A")}</p>
                <p style="margin-top: 14px;"><strong>Entropy effect:</strong> posterior delta {payload.get("detection_summary", {}).get("entropy_posterior_delta", "N/A")}</p>
              </article>
            </div>

            <div class="artifact-grid">
              {"".join(artifact_cards)}
            </div>
          </div>
        </section>

        <section class="section-shell" id="reports">
          <div class="section-inner">
            <div class="section-header reveal">
              <div class="section-kicker">Reports</div>
              <h2>Briefing outputs ready for walkthrough and judging</h2>
              <p>{payload.get("final_statement", "Run Phase 8 first.")}</p>
            </div>
            <div class="report-grid">
              <a class="link-card glass reveal" href="final_manifest.json">
                <strong>Open Final Manifest</strong>
                <span>Review the packaged mission payload, summary metrics, top site, traverse status, and generated artifact references.</span>
              </a>
              <a class="link-card glass reveal" href="README.md" id="docs">
                <strong>Open Outputs Guide</strong>
                <span>Use the generated readme as the supporting document during a live demo, handoff, or submission walkthrough.</span>
              </a>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>

  <script>
    const navbar = document.getElementById("navbar");
    const onScroll = () => {{
      navbar.classList.toggle("compact", window.scrollY > 36);
    }};
    onScroll();
    window.addEventListener("scroll", onScroll, {{ passive: true }});

    const observer = new IntersectionObserver((entries) => {{
      entries.forEach((entry) => {{
        if (entry.isIntersecting) {{
          entry.target.classList.add("is-visible");
        }}
      }});
    }}, {{ threshold: 0.18 }});
    document.querySelectorAll(".reveal").forEach((node) => observer.observe(node));

    const simulateButton = document.getElementById("simulate-traverse");
    const traverseProgress = document.getElementById("traverse-progress");
    const roverMarker = document.getElementById("rover-marker");
    let traversing = false;
    if (simulateButton && traverseProgress && roverMarker) {{
      simulateButton.addEventListener("click", () => {{
        if (traversing) return;
        traversing = true;
        traverseProgress.style.width = "0%";
        roverMarker.style.left = "9%";
        requestAnimationFrame(() => {{
          traverseProgress.style.width = "79%";
          roverMarker.style.left = "78%";
        }});
        window.setTimeout(() => {{
          traversing = false;
        }}, 2600);
      }});
    }}
  </script>
</body>
</html>"""

    output = repo_root / "outputs/dashboard.html"
    output.write_text(html, encoding="utf-8")
    return output


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    output = build_fallback_html(repo_root)
    try:
        import streamlit as st
    except Exception:
        print(f"Streamlit is not installed. Open {output} for the cinematic dashboard.")
        return

    payload = json.loads((repo_root / "outputs/final_manifest.json").read_text(encoding="utf-8"))
    st.set_page_config(page_title="LunaTrace Mission Experience", layout="wide")
    st.title("LunaTrace Mission Experience")
    st.write("The cinematic HTML experience is generated alongside the existing payload-driven dashboard data.")
    st.markdown(f"[Open generated mission site]({output.as_uri()})")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Expected Ice (m^3)", payload["resource_summary"]["expected_ice_m3"])
    c2.metric("Water Yield (m^3)", payload["resource_summary"]["water_yield_expected_m3"])
    c3.metric("Round Trip Energy (Wh)", payload["traverse_summary"]["round_trip_energy_wh"])
    c4.metric("Dwell Margin (hr)", payload["traverse_summary"]["dwell_margin_hr"])
    st.subheader("Decision Story")
    for beat in payload.get("story_beats", []):
        st.write(f"- {beat}")
    st.subheader("Landing Site Ranking")
    st.table(payload.get("site_rankings", []))
    st.write(payload.get("sensitivity_note", ""))
    st.subheader("Traverse Cost Breakdown")
    st.json(payload["traverse_summary"]["cost_breakdown"])
    st.write(f"Binding constraint: {payload['traverse_summary']['binding_constraint']}")
    st.write(f"Entropy posterior delta: {payload['detection_summary']['entropy_posterior_delta']}")
    for artifact in payload["artifacts"]:
        st.image(str(repo_root / artifact), caption=artifact)


if __name__ == "__main__":
    main()
