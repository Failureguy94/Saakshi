import asyncio
import os
import shutil
import binascii
import traceback
from fastapi import FastAPI, Response, Request
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging

from saakshi.db import get_db, init_db
from saakshi.modules.identification import identify_image
from saakshi.modules.acquisition import acquire_image
from saakshi.modules.parsing import parse_vendorx
from saakshi.modules.recovery import extract_and_carve
from saakshi.modules.timeline import analyze_timeline
from saakshi.modules.analytics import detect_motion
from saakshi.modules.custody import create_manifest, verify_chain, verify_manifest, tamper_clip_copy, restore_clip_copy, merkle_proof
from saakshi.modules.reporting import generate_report

app = FastAPI(title="Saakshi Forensic Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IMG_PATH = "out/synthetic_dvr.img"
sse_queue = asyncio.Queue()

def log_msg(msg):
    asyncio.run_coroutine_threadsafe(sse_queue.put(f"event: log\ndata: {msg}\n\n"), asyncio.get_event_loop())

def send_progress(stage_name, pct, msg):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    asyncio.run_coroutine_threadsafe(sse_queue.put(f"event: progress\ndata: {{\"stage\": \"{stage_name}\", \"pct\": {pct}, \"msg\": \"{msg}\"}}\n\n"), loop)

@app.get("/api/case")
def get_case():
    if not os.path.exists(IMG_PATH):
        return {"file": "Not found", "size": 0, "read_only": True}
    size = os.path.getsize(IMG_PATH)
    return {"file": IMG_PATH, "size": size, "read_only": True}

@app.get("/api/evidence/hex")
def get_hex(offset: int = 0, length: int = 256):
    if not os.path.exists(IMG_PATH):
        return {"data": []}
    with open(IMG_PATH, "rb") as f:
        f.seek(offset)
        data = f.read(length)
    
    rows = []
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_str = " ".join([f"{b:02X}" for b in chunk])
        ascii_str = "".join([chr(b) if 32 <= b <= 126 else "." for b in chunk])
        rows.append({"offset": f"{offset+i:08X}", "hex": hex_str, "ascii": ascii_str})
    return {"data": rows}

@app.post("/api/stage/{n}")
async def run_stage(n: int):
    init_db() # ensure db is there
    try:
        if n == 1:
            log_msg("Stage 1: Identify Image")
            best_match, conf = await asyncio.to_thread(identify_image, IMG_PATH)
            return {"match": best_match, "confidence": conf}
        elif n == 2:
            log_msg("Stage 2: Acquire & Hash")
            def acq_cb(processed, total, msg):
                pct = int((processed/total)*100) if total else 0
                send_progress("Acquire", pct, msg)
            res = await asyncio.to_thread(acquire_image, IMG_PATH, acq_cb)
            return res
        elif n == 3:
            log_msg("Stage 3: Parse Index")
            count = await asyncio.to_thread(parse_vendorx, IMG_PATH)
            return {"parsed_count": count}
        elif n == 4:
            log_msg("Stage 4: Recover & Carve")
            def rec_cb(idx, total, msg):
                pct = int((idx/total)*100) if total else 0
                send_progress("Recover", pct, msg)
            idx_cnt, rec_cnt = await asyncio.to_thread(extract_and_carve, IMG_PATH, "out", rec_cb)
            return {"indexed": idx_cnt, "recovered": rec_cnt}
        elif n == 5:
            log_msg("Stage 5: Timeline & Analytics")
            timeline_summary = await asyncio.to_thread(analyze_timeline)
            motion_cnt = await asyncio.to_thread(detect_motion)
            return {"timeline": timeline_summary, "motion_events": motion_cnt}
        elif n == 6:
            log_msg("Stage 6: Integrity & Reporting")
            root = await asyncio.to_thread(create_manifest, IMG_PATH)
            report_path = await asyncio.to_thread(generate_report)
            return {"merkle_root": root, "report": report_path}
        else:
            return JSONResponse(status_code=400, content={"error": "Invalid stage"})
    except Exception as e:
        log_msg(f"Error in stage {n}: {str(e)}")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/stream")
async def sse_stream(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            try:
                msg = await asyncio.wait_for(sse_queue.get(), timeout=1.0)
                yield msg
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/segments")
def get_segments():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM segments")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"segments": rows}

@app.get("/api/timeline")
def get_timeline():
    # Similar to timeline module output
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM segments")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"segments": rows}

@app.get("/api/events")
def get_events():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM motion_events")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"events": rows}

@app.get("/api/custody")
def get_custody():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM custody_log ORDER BY id ASC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"log": rows}

@app.get("/api/merkle/proof/{clip_id}")
def get_proof(clip_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT file_hash FROM segments WHERE id=?", (clip_id,))
    row = c.fetchone()
    conn.close()
    if row and row["file_hash"]:
        proof = merkle_proof(row["file_hash"], IMG_PATH)
        return {"proof": proof, "hash": row["file_hash"]}
    return JSONResponse(status_code=404, content={"error": "Not found"})

@app.get("/api/clip/{clip_id}")
def get_clip(clip_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT file_path FROM segments WHERE id=?", (clip_id,))
    row = c.fetchone()
    conn.close()
    if row and row["file_path"] and os.path.exists(row["file_path"]):
        return FileResponse(row["file_path"])
    return JSONResponse(status_code=404, content={"error": "Not found"})

@app.get("/api/report.pdf")
def get_report():
    if os.path.exists("out/report.pdf"):
        return FileResponse("out/report.pdf")
    return JSONResponse(status_code=404, content={"error": "Not found"})

@app.post("/api/custody/verify")
def do_verify_chain():
    valid, failed_id = verify_chain()
    m_valid, m_path, m_exp, m_act = verify_manifest()
    return {
        "chain_valid": valid,
        "failed_chain_id": failed_id,
        "manifest_valid": m_valid,
        "failed_path": m_path,
        "expected_hash": m_exp,
        "actual_hash": m_act
    }

class TamperReq(BaseModel):
    clip_id: int

@app.post("/api/custody/tamper")
def do_tamper(req: TamperReq):
    res = tamper_clip_copy(req.clip_id)
    return {"tampered_file": res}

@app.post("/api/custody/restore")
def do_restore(req: TamperReq):
    restore_clip_copy(req.clip_id)
    return {"restored": True}

@app.post("/api/reset")
def do_reset():
    os.system("rm -rf out/* && python scripts/make_synthetic_dvr.py")
    return {"reset": True}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
