#!/usr/bin/env python3
"""테스트 산출물(요청 JSON·ABC)이 YuE2 공식 입력 계약을 따르는지 기계적으로 감사한다.

사용: python3 evals/official_compliance.py <iteration-dir> [...]
근거(고정 공식 원문, Road Music 보관본):
  official/docs/generation.md — style(장르·악기·보컬·언어·템포), lyrics(부를 말 + [Verse]/[Chorus] 같은 구간), cot full/melody/off, abc는 full/melody만
  official/skills/yue2-music/references/generation-and-covers.md — 요청 필드(style·lyrics·cot·seed·abc·cfg_scale·id), 없는 필드, 템포는 ABC와 style 일치, melody는 코드 자동 제거 안 함
  current/docs/generation.md — 가사의 발음·화자 주석은 제어 채널이 아님, 악보는 Vocal·Ins 두 선율
  official/skills/yue2-music/references/abc-editing.md — 지원 방언
결과는 <iteration>/official-compliance.md·.json에 쓴다.
"""
import glob, json, os, re, subprocess, sys, tempfile

CLI = os.environ.get("ROAD_MUSIC_CLI", "/Users/freelife/youtube/music/music-road/cli/road-music.js")
ALLOWED_TOP = {"title", "engine", "count", "style", "lyrics", "bpm", "parts", "instrumental", "targetSeconds", "seed", "cot", "abc", "mode", "advanced", "runtime", "requestPrompt", "requestId"}
NONEXISTENT = {"negative_prompt", "negativePrompt", "phonemes", "reference_audio", "referenceAudio", "bpm_field", "duration", "edit_interval", "reference_singer", "singer", "voice", "persona", "variety", "weirdness", "maxMode", "excludeStyles", "tags"}
TAG_LINE = re.compile(r"^\[([^\]]+)\]\s*$")
ROAD_TAGS = {"Verse", "Pre-Chorus", "Chorus", "Bridge", "Intro", "Interlude", "Outro", "instrumental"}
LANG = re.compile(r"\b(korean|english|chinese|mandarin|cantonese|japanese|spanish|french)\b|한국어", re.I)
VOICE = re.compile(r"vocal|voice|singer|choir|\brap\b|duet|male|female", re.I)
TEMPO = re.compile(r"\b\d{2,3}\s*bpm\b|tempo", re.I)
INSTR = re.compile(r"drum|guitar|bass|piano|synth|string|brass|organ|percussion|pad|orchestra|accordion|violin|cello|flute|sax|trumpet|harp|ukulele|rhodes|keys", re.I)
INSTRUCTION = re.compile(r"\b(you are|generate|create a song|make a song|ignore|prompt)\b|만들어|생성해", re.I)


def cli(args, tmp):
    r = subprocess.run(["node", CLI, *args], capture_output=True, text=True, env={**os.environ, "ROADMUSIC_DATA_DIR": tmp, "ROADMUSIC_STUDIO_AUTO_OPEN": "0"})
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        return {"ok": False, "error": (r.stdout + r.stderr)[:200]}


def is_request(d):
    return isinstance(d, dict) and "engine" in d and ("style" in d or "parts" in d) and str(d.get("engine", "")).startswith("yue")


def audit(path, d, tmp):
    issues, notes = [], []
    # 실제로 YuE2에 가는 것은 Road Music 정리·조합 뒤의 nativeRequest다. 가능하면 그것을 감사한다.
    req0 = {k: v for k, v in d.items() if k in ALLOWED_TOP}
    f0 = os.path.join(tmp, "req0.json"); json.dump(req0, open(f0, "w"), ensure_ascii=False)
    p0 = cli(["song:prepare", "--file", f0], tmp)
    native = p0["result"].get("nativeRequest", {}) if p0.get("ok") else {}
    keys = set(d)
    bad = sorted(keys & NONEXISTENT)
    if bad: issues.append(f"YuE2에 없는 필드 {bad}")
    unknown = sorted(keys - ALLOWED_TOP - NONEXISTENT)
    if unknown: issues.append(f"Road Music 계약 밖 필드 {unknown}")
    cot = d.get("cot", "full")
    if cot not in ("full", "melody", "off"): issues.append(f"cot 값 {cot}")
    if d.get("abc") and cot == "off": issues.append("cot off + abc(공식: abc는 full/melody만)")
    if d.get("advanced"): notes.append(f"advanced 사용 {sorted(d['advanced'])} — 실험으로 밝혔는지 확인")
    if d.get("runtime"): notes.append(f"runtime 변경 {d['runtime']}")
    # lyrics: 부를 말 + 구간 태그만
    lyrics = native.get("lyrics", d.get("lyrics") or "")
    if not d.get("instrumental"):
        for ln in lyrics.splitlines():
            s = ln.strip()
            if not s: continue
            m = TAG_LINE.match(s)
            if m:
                if m.group(1) not in ROAD_TAGS: issues.append(f"구간 태그 외 대괄호 [{m.group(1)}]")
            elif re.search(r"[\[\]]", s): issues.append(f"줄 안 대괄호 지시: {s[:30]}")
            elif re.search(r"[(（].*[)）]|/\S+/|^\s*(남|여|male|female)\s*:|^(Style|BPM|Tempo)\s*:", s, re.I): issues.append(f"가사 속 주석·지시: {s[:30]}")
        if lyrics and not any(TAG_LINE.match(l.strip()) and TAG_LINE.match(l.strip()).group(1) in ("Verse", "Chorus") for l in lyrics.splitlines()):
            issues.append("[Verse]/[Chorus] 구간 없음")
    # style: 장르·악기·보컬·언어·템포
    style = native.get("style") or d.get("style") or (d.get("parts") or {}).get("genre", "")
    user_style = d.get("style") or (d.get("parts") or {}).get("genre", "")
    tempo_given = bool(d.get("bpm") or (d.get("parts") or {}).get("bpm") or TEMPO.search(style))
    lacks = [n for n, ok in (("언어", d.get("instrumental") or LANG.search(style)), ("보컬", d.get("instrumental") or VOICE.search(style) or (d.get("parts") or {}).get("vocal")), ("악기", INSTR.search(style) or (d.get("parts") or {}).get("instruments") or (d.get("parts") or {}).get("instrumentation")), ("템포", tempo_given)) if not ok]
    if lacks: issues.append(f"style에 {lacks} 없음")
    if INSTRUCTION.search(user_style): issues.append("style에 명령문")
    if re.search(r"\b(like|style of|inspired by)\b", user_style, re.I): issues.append("style에 실존 가수·곡 비교 의심")
    # ABC
    if d.get("abc"):
        q = re.search(r"^Q:\s*(?:\d+/\d+\s*=\s*)?(\d{2,3})", d["abc"], re.M)
        bpm = d.get("bpm") or (d.get("parts") or {}).get("bpm") or (re.search(r"(\d{2,3})\s*BPM", style, re.I) or [None, None])[1]
        if q and bpm and abs(int(q.group(1)) - int(bpm)) > 2: issues.append(f"ABC Q:{q.group(1)} ≠ style BPM {bpm}")
        if cot == "melody" and re.search(r'"[A-G]', d["abc"]): issues.append("melody 모드 ABC에 코드 기호")
        f = os.path.join(tmp, "x.abc"); open(f, "w").write(d["abc"])
        ins = cli(["score:inspect", "--json", json.dumps({"file": f})], tmp)
        if not ins.get("ok"): issues.append(f"ABC 방언 검사 실패: {str(ins.get('error'))[:80]}")
    # Road Music song:prepare (공식 점검 포함)
    req = {k: v for k, v in d.items() if k in ALLOWED_TOP}
    f = os.path.join(tmp, "req.json"); json.dump(req, open(f, "w"), ensure_ascii=False)
    p = cli(["song:prepare", "--file", f], tmp)
    if not p.get("ok"): issues.append(f"song:prepare 거부: {str(p.get('error'))[:100]}")
    else:
        r = p["result"]
        if not r.get("valid"): issues.append(f"valid:false {r.get('errors')}")
        adv = [c["id"] for c in r.get("officialGuide", {}).get("checks", []) if c["status"] == "advice"]
        if adv: notes.append(f"officialGuide advice {adv} — 보고서에 유지 이유가 있어야 함")
        eff = r.get("effective", {}).get("advanced", {})
        if not d.get("advanced") and eff.get("cfgScale") not in (1, 1.01): issues.append(f"기본 CFG 아님 {eff.get('cfgScale')}(strict+strong?)")
    return issues, notes


def main():
    rows = []
    for it in sys.argv[1:]:
        for f in sorted(glob.glob(os.path.join(it, "eval-*", "*", "run-*", "outputs", "**", "*.json"), recursive=True)):
            if any(x in os.path.basename(f) for x in ("prep", "prepare", "result", "check", "clean", "compose", "schema", "engines", "appstate", "songs", "detail", "metadata")): continue
            try: d = json.load(open(f, encoding="utf-8"))
            except Exception: continue
            if not is_request(d): continue
            with tempfile.TemporaryDirectory() as tmp:
                issues, notes = audit(f, d, tmp)
            role = "사용자 원문" if re.search(r"original|before", os.path.basename(f)) else ("가사 전 초안" if ".draft." in os.path.basename(f) else "제출안")
            if role == "가사 전 초안":
                issues = [i for i in issues if "부를 가사" not in i and "[Verse]/[Chorus]" not in i]
            rows.append({"file": os.path.relpath(f, it), "iteration": os.path.basename(it.rstrip("/")), "role": role, "issues": issues, "notes": notes})
    out_md = ["# YuE2 공식 계약 감사", "", f"- 감사한 요청 JSON: {len(rows)}개(제출안 {sum(r['role']=='제출안' for r in rows)}, 가사 전 초안 {sum(r['role']=='가사 전 초안' for r in rows)}, 사용자 원문 {sum(r['role']=='사용자 원문' for r in rows)})", f"- 위반 있는 제출안·초안: {sum(bool(r['issues']) and r['role']!='사용자 원문' for r in rows)}개 (사용자 원문의 위반은 보정안 제시 여부로 판단)", "- 가사·style 검사는 Road Music 정리 뒤 실제 YuE2로 가는 nativeRequest 기준", "", "| 회차 | 파일 | 구분 | 위반 | 확인 필요 |", "| --- | --- | --- | --- | --- |"]
    for r in rows:
        out_md.append(f"| {r['iteration']} | {r['file']} | {r['role']} | {'; '.join(r['issues']) or '없음'} | {'; '.join(r['notes']) or '—'} |")
    print("\n".join(out_md))
    for it in sys.argv[1:]:
        sub = [r for r in rows if r["iteration"] == os.path.basename(it.rstrip("/"))]
        json.dump(sub, open(os.path.join(it, "official-compliance.json"), "w"), ensure_ascii=False, indent=2)
        open(os.path.join(it, "official-compliance.md"), "w").write("\n".join([l for l in out_md[:8]] + [l for l in out_md[8:] if l.startswith(f"| {os.path.basename(it.rstrip('/'))} ")]))


if __name__ == "__main__":
    main()
