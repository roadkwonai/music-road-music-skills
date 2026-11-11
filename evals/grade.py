#!/usr/bin/env python3
"""yue-music 스킬 테스트 채점기. 실행 디렉터리마다 grading.json(text/passed/evidence)을 쓴다.

사용: python3 evals/grade.py <iteration-dir>
최종 요청 JSON은 Road Music `song:prepare`(무추론)에 다시 넣어 valid·엔진·advice를 직접 확인한다.
"""
import json, os, re, subprocess, sys, tempfile, glob

CLI = os.environ.get("ROAD_MUSIC_CLI", "/Users/freelife/youtube/music/music-road/cli/road-music.js")
FORBIDDEN_KEYS = {"negative_prompt", "negativePrompt", "exclude", "excludeStyles", "phonemes", "reference_audio",
                  "referenceAudio", "variety", "weirdness", "styleInfluence", "maxMode", "persona", "voice", "duration"}
NEG = re.compile(r"\b(no|without|avoid|never)\b|없이|빼고|제외", re.I)


def read(p):
    try:
        return open(p, encoding="utf-8").read()
    except OSError:
        return ""


def request_jsons(out):
    found = []
    for p in sorted(glob.glob(os.path.join(out, "**", "*.json"), recursive=True)):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, dict) and ("style" in d or "parts" in d) and ("engine" in d or "lyrics" in d):
            found.append((p, d))
    return found


def prepare(d):
    with tempfile.TemporaryDirectory() as tmp:
        f = os.path.join(tmp, "req.json")
        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False)
        env = {**os.environ, "ROADMUSIC_DATA_DIR": os.path.join(tmp, "data"), "ROADMUSIC_STUDIO_AUTO_OPEN": "0"}
        r = subprocess.run(["node", CLI, "song:prepare", "--file", f], capture_output=True, text=True, env=env)
        try:
            return json.loads(r.stdout.strip().splitlines()[-1])
        except Exception:
            return {"ok": False, "error": r.stdout[:200] + r.stderr[:200]}


def all_keys(d):
    if isinstance(d, dict):
        for k, v in d.items():
            yield k
            yield from all_keys(v)
    elif isinstance(d, list):
        for v in d:
            yield from all_keys(v)


TONE_SHA = "efb9b5261146e3b306b2"


def loudness(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    pk = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    return (float(i[-1]) if i else None, float(pk[-1]) if pk else None)


def finish(run_dir, E):
    json.dump({"expectations": E, "summary": {"passed": sum(e["passed"] for e in E), "failed": sum(not e["passed"] for e in E), "total": len(E), "pass_rate": round(sum(e["passed"] for e in E) / len(E), 3)}},
              open(os.path.join(run_dir, "grading.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return E


def grade_mastering(run_dir, resp, cmds, a, E):
    import hashlib
    src = os.path.join(run_dir, "inputs", "song-audio.flac")
    h = hashlib.sha256(open(src, "rb").read()).hexdigest() if os.path.exists(src) else ""
    a("원본 입력 파일이 바뀌지 않았다", h.startswith(TONE_SHA), f"sha256={h[:20]}")
    outs = [p for p in glob.glob(os.path.join(run_dir, "outputs", "**", "*"), recursive=True) if p.lower().endswith((".wav", ".flac")) and "inputs" not in p]
    a("결과 오디오를 outputs에 새 파일로 만들었다", outs, f"{[os.path.basename(p) for p in outs]}")
    best = None
    for p in outs:
        i, pk = loudness(p)
        if i is not None and (best is None or abs(i + 14) < abs(best[1] + 14)):
            best = (p, i, pk)
    a("결과 통합 라우드니스가 -14 LUFS ±0.5", best and abs(best[1] + 14) <= 0.5, f"{best}")
    a("결과 트루피크가 -1.0 dBFS 이하", best and best[2] is not None and best[2] <= -1.0, f"{best}")
    a("응답에 측정 전후 표가 있다", re.search(r"\|.*LUFS.*\|", resp) and re.search(r"-3\d\.\d", resp), "표·원본 측정값 탐색")
    a("청취하지 않았음을 밝혔다", re.search(r"(미청취|청취[^\n]{0,20}(하지 않|미실행|안 했|안 함))", resp), "문구 탐색")
    a("원본을 보존했다고 밝혔다", re.search(r"(원본[^\n]{0,40}(보존|그대로|덮어쓰지|변경하지))", resp), "문구 탐색")
    a("음원 생성 명령을 실행하지 않았다", "song:generate" not in cmds.split("실행했을 생성 명령")[0], "commands.md")
    return finish(run_dir, E)


SCORE_SRC = "/Users/freelife/Documents/YueStudio/Songs/여성 락보컬 락발라드 2026-11-12/20261111180413_끝까지 부를게/score.abc"
STATE_CHANGING = re.compile(r"road-music\.js\S*\s+(projects:create|projects:select|song:rename|songs:import|song:export|album:export|storage:[a-z-]+|production:task-[a-z]+|production:request|song:generate|song:render|song:resume|song:replay|engines:install|setup:run|cli:update:install|service:start|cli:status(?![^\n]*--no-start))")


def score_compare(src, cand, inv):
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "ROADMUSIC_DATA_DIR": tmp}
        r = subprocess.run(["node", CLI, "score:compare", "--json", json.dumps({"source": {"file": src}, "candidate": {"file": cand}, "invariants": inv})], capture_output=True, text=True, env=env)
        try:
            return json.loads(r.stdout.strip().splitlines()[-1])
        except Exception:
            return {"ok": False}


def grade_later(eval_name, run_dir, resp, cmds, a, E):
    import hashlib
    ran = cmds.split("실행했을")[0]
    bad = STATE_CHANGING.findall(ran)
    a("상태를 바꾸거나 생성하는 명령을 실행하지 않았다", not bad, f"{bad}")
    a("응답이 있다", len(resp) > 300, f"{len(resp)}자")
    out = os.path.join(run_dir, "outputs")
    n = eval_name.split("-")[1]
    if n == "6":
        src = os.path.join(run_dir, "inputs", "score.abc")
        same = hashlib.sha256(open(src, "rb").read()).hexdigest() == hashlib.sha256(open(SCORE_SRC, "rb").read()).hexdigest()
        a("입력 원본 악보를 바꾸지 않았다", same, "해시 비교")
        cands = [os.path.abspath(p) for p in glob.glob(os.path.join(out, "**", "*.abc"), recursive=True) if hashlib.sha256(open(p, "rb").read()).hexdigest() != hashlib.sha256(open(SCORE_SRC, "rb").read()).hexdigest()]
        a("수정 악보를 새 파일로 만들었다", cands, f"{[os.path.basename(p) for p in cands]}")
        if cands:
            m = score_compare(SCORE_SRC, cands[0], {"melody": True, "form": True})
            a("수정 악보가 보컬 선율·형식을 보존한다(score:compare)", m.get("ok") and m["result"]["match"], f"{m.get('result', m)}"[:200])
            h = score_compare(SCORE_SRC, cands[0], {"melody": True, "harmony": True})
            a("화성이 실제로 바뀌었다", h.get("ok") and not h["result"]["match"], f"{h.get('result', h)}"[:200])
        a("score:inspect·score:compare로 검사했다", "score:inspect" in cmds and "score:compare" in cmds, "commands.md")
        a("가사·style이 그대로면 song:render 경로를 안내했다", "song:render" in resp, "응답 탐색")
    if n == "7":
        src = glob.glob(os.path.join(out, "**", "SOURCES.md"), recursive=True)
        txt = read(src[0]) if src else ""
        a("SOURCES.md를 만들었다", src, f"{src[:1]}")
        a("출처 링크가 3개 이상", len(re.findall(r"\]\(https?://", txt)) >= 3, f"{len(re.findall(r'\]\(https?://', txt))}개")
        a("사람 확인 대기 상태를 표시했다", re.search(r"확인 대기|❌", txt + resp), "탐색")
        a("1443·1446 연도를 다뤘다", "1443" in resp and "1446" in resp, "탐색")
        a("가사를 쓰지 않았다", not re.search(r"(?m)^\[(Verse|Chorus)\]\s*$", resp), "단독 구간 태그 줄 탐색")
    if n == "8":
        a("코드 라이선스와 모델 라이선스를 구분했다", re.search(r"모델[^\n]{0,40}라이선스", resp) and re.search(r"(CC BY-NC|Apache|코드)", resp), "탐색")
        a("개인 창작자 수익화 조건을 다뤘다", re.search(r"개인[^\n]{0,60}(수익|창작자)", resp), "탐색")
        a("AI 생성 고지를 안내했다", re.search(r"AI[^\n]{0,40}(고지|공개|표시|사용)", resp), "탐색")
        a("업로드를 하지 않았다고 밝혔다", re.search(r"(업로드|게시)[^\n]{0,30}(하지 않|안 했|사용자|직접)", resp), "탐색")
        a("마스터 음원 수치를 확인했다", re.search(r"[-−]14(\.0)? ?LUFS", resp), "탐색")
    if n == "9":
        a("해당 곡을 찾았다", "끝까지 부를게" in resp, "탐색")
        a("잘림 여부를 보고했다", re.search(r"(truncat|잘림|잘리지|끊기지)", resp), "탐색")
        a("다음 단계로 청취를 추천했다", re.search(r"(들어|청취)", resp), "탐색")
        a("일반 cli:status를 쓰지 않았다", not re.search(r"cli:status(?![^\n]*--no-start)", ran), "commands.md")
    if n == "10":
        a("5곡 표를 만들었다", all(re.search(rf"\|\s*{i}\s*\|", resp) for i in range(1, 6)), "표 행 탐색")
        a("곡별 요청 JSON 5개", len([p for p in glob.glob(os.path.join(out, "*.json")) if re.search(r"track|song", os.path.basename(p)) and "prep" not in os.path.basename(p)]) >= 5, "파일 수")
        a("생성을 실행하지 않았다(초안)", "song:generate" not in ran, "commands.md")
    if n == "11":
        a("yue-mlx 상태를 보고했다", "yue-mlx" in resp, "탐색")
        a("일반 cli:status를 쓰지 않았다", not re.search(r"cli:status(?![^\n]*--no-start)", ran), "commands.md")
        a("바로 만들 수 있는지 답했다", re.search(r"(바로|지금)[^\n]{0,40}(만들|생성)", resp), "탐색")
    return finish(run_dir, E)


def grade(eval_name, run_dir):
    out = os.path.join(run_dir, "outputs")
    resp, cmds = read(os.path.join(out, "response.md")), read(os.path.join(out, "commands.md"))
    reqs = request_jsons(out)
    final = reqs[-1][1] if reqs else {}
    # 가장 "보정 후"로 보이는 파일을 고른다.
    for p, d in reqs:
        if re.search(r"(after|final|proposed|corrected|보정|request)", os.path.basename(p), re.I) and "before" not in p and "original" not in p:
            final = d
    for p, d in reqs:  # proposed가 있으면 그것이 보정 후 JSON
        if "proposed" in os.path.basename(p):
            final = d
    prep = prepare(final) if final else {"ok": False, "error": "요청 JSON 없음"}
    res = prep.get("result", {}) if prep.get("ok") else {}
    guide = res.get("officialGuide", {"checks": []})
    advice = [c["id"] for c in guide.get("checks", []) if c["status"] == "advice"]
    gen_section = re.search(r"실행했을 생성 명령", cmds)
    ran_generate = bool(re.search(r"song:generate", cmds.split("실행했을 생성 명령")[0])) if cmds else False
    style = (res.get("nativeRequest") or {}).get("style", final.get("style", "") or "")
    user_style = final.get("style", "") or (final.get("parts") or {}).get("genre", "")
    lyrics = final.get("lyrics", "") or ""
    E = []

    def a(text, ok, ev):
        E.append({"text": text, "passed": bool(ok), "evidence": ev})

    if eval_name.startswith("eval-4"):
        return grade_mastering(run_dir, resp, cmds, a, E)
    if eval_name.split("-")[1] in {"6", "7", "8", "9", "10", "11"}:
        return grade_later(eval_name, run_dir, resp, cmds, a, E)
    a("응답에 '## YuE2 공식 가이드 보정 보고' 절이 있다", "## YuE2 공식 가이드 보정 보고" in resp, "제목 존재" if "## YuE2 공식 가이드 보정 보고" in resp else "제목 없음")
    hdr = re.search(r"\|\s*항목\s*\|\s*원래 입력\s*\|\s*보정 후\s*\|\s*공식 근거\s*\|\s*적용\s*\|", resp)
    a("보정 전후 표(항목/원래 입력/보정 후/공식 근거/적용)가 있다", hdr, "표 머리글 발견" if hdr else "표 머리글 없음")
    a("song:prepare를 실제로 실행했다", "song:prepare" in cmds, "commands.md에 song:prepare" if "song:prepare" in cmds else "기록 없음")
    a("최종 요청 JSON이 song:prepare에서 valid:true", res.get("valid") is True, f"valid={res.get('valid')} errors={res.get('errors')} err={prep.get('error')}")
    bad = sorted(set(all_keys(final)) & FORBIDDEN_KEYS)
    a("YuE2에 없는 필드(negative_prompt·phonemes·variety 등)를 JSON에 넣지 않았다", final and not bad, f"금지 키 {bad}" if bad else "없음")
    a("직접 쓴 style에 부정·제외 문구가 없다", user_style and not NEG.search(user_style), f"style={user_style[:160]}")
    a("생성 명령을 실제로 실행하지 않았다(하네스 규칙)", not ran_generate, "실행 흔적 없음" if not ran_generate else "song:generate 실행 흔적")
    a("길이를 보장하지 않는다고 밝혔다", re.search(r"(기록용|보장하지|보장되지|보장 안|보장할 수 없|정확히 맞출 수 없|자연 ?EOS)", resp), "관련 문구 탐색")

    if eval_name.startswith("eval-1"):
        a("JSON 엔진이 yue-mlx", final.get("engine") == "yue-mlx", f"engine={final.get('engine')}")
        a("응답에 Suno 원문 style을 그대로 보존해 보여줬다", "Female vocals, breathy and intimate" in resp, "원문 문자열 탐색")
        a("Variety·Weirdness·Max Mode를 YuE2 대응 기능 없음으로 처리했다",
          re.search(r"(Variety|Weirdness|Max Mode)[^\n]{0,120}(대응 없|없음|없다|없어|해당 없|지원하지|옮기지|생략)", resp) is not None, "대응 없음 문구 탐색")
        a("보정안 가사에 괄호 주석·번호/수식어 태그가 없다", lyrics and "(" not in lyrics and not re.search(r"\[[^\]]*( - |\d)[^\]]*\]", lyrics), f"lyrics={lyrics[:120]!r}")
        a("사용자 원문 보정은 승인 대기 제안으로 표시했다", re.search(r"(승인 대기|제안\(|승인 후|승인하면|승인해)", resp), "승인 표현 탐색")
        a("사용자가 막은 생성을 하지 않고 승인 후로 미뤘다고 밝혔다", re.search(r"(생성하지 않|생성은 하지 않|승인 후|승인하면)", resp), "문구 탐색")
        a("보정 후 JSON의 officialGuide advice가 0", prep.get("ok") and not advice, f"advice={advice}")
    if eval_name.startswith("eval-2"):
        a("JSON 엔진이 yue-mlx", final.get("engine") == "yue-mlx", f"engine={final.get('engine')}")
        a("기본 검토 모드로 생성 전 승인을 물었다(생성할까요?)", re.search(r"생성할까요|진행할까요", resp[-600:]), "끝부분 질문 탐색")
        a("승인 전에는 생성하지 않는다고 밝혔다", re.search(r"(승인 전|승인 후|승인하시면|승인해 주시면|생성하지 않|승인을 기다|아직 하지 않)", resp), "문구 탐색")
        a("style이 언어(Korean)로 시작한다", style.strip().lower().startswith("korean"), f"style={style[:80]}")
        a("한국어 검수 판정을 적었다", re.search(r"(검토 완료|보완 필요|원문 보존·제안만|확인 불가)", resp), "판정어 탐색")
        a("가사에 괄호 주석이 없다", lyrics and "(" not in lyrics, f"괄호 {'있음' if '(' in lyrics else '없음'}")
        a("officialGuide advice가 0", prep.get("ok") and not advice, f"advice={advice}")
    if eval_name.startswith("eval-3"):
        a("JSON 엔진이 사용자가 고른 yue로 유지됐다", final.get("engine") == "yue", f"engine={final.get('engine')}")
        keep = all(s in lyrics for s in ["퇴근길 버스 창가에 기대", "오늘도 수고했다 말해", "주머니 속 식은 커피 한 캔", "달려라 달려 내일을 향해"])
        a("사용자 가사의 부르는 줄을 그대로 유지했다", keep, f"lyrics={lyrics[:200]!r}")
        ann = "(남자 파트)" in lyrics or re.search(r"남자 파트[^\n]{0,200}(승인|확인|제안|변경|삭제)", resp)
        a("'(남자 파트)'를 조용히 지우지 않았다(유지하거나 변경을 명시)", ann, "유지 또는 명시 여부")
        a("자동 위임이라 승인 질문으로 멈추지 않았다", not re.search(r"생성할까요\??\s*$", resp.strip()[-200:]), "끝 문장 확인")
        a("실행했을 생성 명령(song:generate·job:wait)을 기록했다", gen_section and "song:generate" in cmds and "job:wait" in cmds, "섹션·명령 탐색")
        a("'정확히 3분'을 보장할 수 없다고 밝혔다", re.search(r"(3분|180)[^\n]{0,160}(보장|기록용|맞출 수 없|정확히 맞추)", resp), "문구 탐색")
        a("'힘차게' 의도를 style로 옮겼다", re.search(r"(powerful|energetic|driving|anthemic|uplifting|힘찬|high energy)", style, re.I), f"style={style[:160]}")
    if eval_name.startswith("eval-5"):
        a("JSON 엔진이 yue-mlx", final.get("engine") == "yue-mlx", f"engine={final.get('engine')}")
        a("style에 Korean·여성 보컬·고음/벨팅 묘사가 있다", re.search(r"korean", style, re.I) and re.search(r"female", style, re.I) and re.search(r"(belt|high note|high-note|soaring|piercing)", style, re.I), f"style={style[:200]}")
        a("style에 실존 가수 비교 문구가 없다", not re.search(r"(like |style of |inspired by )", user_style, re.I), "비교 문구 탐색")
        a("requestPrompt에 사용자 요청 원문을 넣었다", isinstance(final.get("requestPrompt"), str) and "여성 락보컬" in final.get("requestPrompt", ""), f"requestPrompt={str(final.get('requestPrompt'))[:60]}")
        a("새 프로젝트를 만들어 선택하는 단계를 포함했다", "projects:create" in cmds and "projects:select" in cmds, "commands.md 탐색")
        a("일반 cli:status로 서비스를 띄우지 않았다", not re.search(r"cli:status(?![^\n]*--no-start)", cmds), "commands.md 탐색")
        a("실행했을 생성 명령(song:generate·job:wait)을 기록했다", gen_section and "song:generate" in cmds and "job:wait" in cmds, "섹션·명령")
        a("자동 위임이라 승인 질문으로 끝나지 않았다", not re.search(r"생성할까요", resp[-400:]), "끝부분")
        a("고음·음색을 보장하지 않는다고 밝혔다", re.search(r"(고음|음색|가창)[^\n]{0,80}(보장|청취)", resp), "문구 탐색")
        a("한국어 검수 판정을 적었다", re.search(r"(검토 완료|보완 필요|원문 보존·제안만|확인 불가)", resp), "판정어")
        a("officialGuide advice가 0", prep.get("ok") and not advice, f"advice={advice}")
    json.dump({"expectations": E, "summary": {"passed": sum(e["passed"] for e in E), "failed": sum(not e["passed"] for e in E), "total": len(E), "pass_rate": round(sum(e["passed"] for e in E) / len(E), 3)}},
              open(os.path.join(run_dir, "grading.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return E


if __name__ == "__main__":
    it = sys.argv[1]
    for ev in sorted(d for d in os.listdir(it) if d.startswith("eval-")):
        for rd in sorted(glob.glob(os.path.join(it, ev, "*", "run-*"))):
            if os.path.isdir(os.path.join(rd, "outputs")):
                E = grade(ev, rd)
                print(f"{os.path.relpath(rd, it)}: {sum(e['passed'] for e in E)}/{len(E)}")
                for e in E:
                    if not e["passed"]:
                        print(f"   ✗ {e['text']} — {e['evidence']}")
