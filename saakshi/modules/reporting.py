import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from saakshi.db import get_db
from saakshi.modules.custody import compute_merkle_root

def generate_report(out_path="out/report.pdf"):
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT * FROM custody_log ORDER BY id")
    custody_logs = c.fetchall()
    
    c.execute("SELECT * FROM segments")
    segments = c.fetchall()
    
    c.execute("SELECT * FROM motion_events")
    events = c.fetchall()
    
    merkle_root = compute_merkle_root()
    conn.close()
    
    c = canvas.Canvas(out_path, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Saakshi Forensic Report")
    
    c.setFont("Helvetica", 12)
    y = height - 80
    c.drawString(50, y, f"Merkle Root: {merkle_root}")
    
    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Recovered Segments")
    c.setFont("Helvetica", 10)
    y -= 20
    for seg in segments:
        text = f"CH{seg['channel']} | Offset {seg['offset']} | Len {seg['length']} | Recovered: {seg['is_recovered']} | Hash: {seg['file_hash'][:16]}..."
        c.drawString(50, y, text)
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50
            
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Motion Events")
    c.setFont("Helvetica", 10)
    y -= 20
    for ev in events:
        text = f"Seg {ev['segment_id']} | CH {ev['channel']} | Frame {ev['frame_index']}"
        c.drawString(50, y, text)
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50

    c.showPage()
    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Certificate under Section 63, Bharatiya Sakshya Adhiniyam 2023")
    y -= 30
    c.setFont("Helvetica", 10)
    cert_text = [
        "This is to certify that the electronic record contained in this report",
        "was produced by the Saakshi Forensic Platform in the ordinary course",
        "of its operation.",
        "",
        f"Cryptographic Hash (Merkle Root): {merkle_root}",
        "",
        "Signature: ___________________________",
        "Date: ________________________________",
        "Name: ________________________________"
    ]
    for line in cert_text:
        c.drawString(50, y, line)
        y -= 15

    c.save()
    return out_path

if __name__ == "__main__":
    generate_report()
