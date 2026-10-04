import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from saakshi.db import get_db

def generate_report(out_path="out/report.pdf"):
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT count(*) as cnt FROM segments")
    seg_cnt = c.fetchone()["cnt"]
    c.execute("SELECT count(*) as cnt FROM segments WHERE source='carved'")
    rec_cnt = c.fetchone()["cnt"]
    
    offset = 0.0
    try:
        c.execute("SELECT camera_time, normalized_time FROM segments WHERE normalized_time IS NOT NULL LIMIT 1")
        row = c.fetchone()
        if row:
            import datetime
            c_time = datetime.datetime.strptime(row["camera_time"], "%Y-%m-%d %H:%M:%S").timestamp()
            n_time = datetime.datetime.strptime(row["normalized_time"], "%Y-%m-%d %H:%M:%S").timestamp()
            offset = n_time - c_time
    except Exception:
        pass
    
    c.execute("SELECT * FROM motion_events LIMIT 3")
    events = c.fetchall()
    
    conn.close()
    
    doc = SimpleDocTemplate(out_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("Saakshi Forensic Report", styles['Title']))
    story.append(Spacer(1, 12))
    
    merkle_root = "N/A"
    manifest_path = "out/manifest.json"
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
            merkle_root = manifest.get("merkle_root", "N/A")
            
    story.append(Paragraph(f"Merkle Root: {merkle_root}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Summary", styles['Heading2']))
    summary_data = [
        ["Total Segments", str(seg_cnt)],
        ["Recovered Segments", str(rec_cnt)],
        ["Timeline Offset (sec)", f"{offset:.2f}"]
    ]
    t = Table(summary_data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Motion Events (Top 3)", styles['Heading2']))
    
    img_row = []
    meta_row = []
    for ev in events:
        path = ev["thumbnail_path"]
        if os.path.exists(path):
            img_row.append(Image(path, width=150, height=150))
        else:
            img_row.append("No Image")
        meta_row.append(f"CH {ev['channel']} | Seg {ev['segment_id']} | {ev['start_time']}")
        
    if img_row:
        t2 = Table([img_row, meta_row])
        t2.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t2)
        
    story.append(Spacer(1, 24))
    
    story.append(Paragraph("Certificate under Section 63, BSA 2023", styles['Heading2']))
    cert_text = "This is to certify that the electronic record contained in this report was produced by the Saakshi Forensic Platform in the ordinary course of its operation."
    story.append(Paragraph(cert_text, styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Cryptographic Hash (Merkle Root): {merkle_root}", styles['Normal']))
    story.append(Spacer(1, 24))
    story.append(Paragraph("Signature: ___________________________", styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Date: ________________________________", styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Name: ________________________________", styles['Normal']))
    
    doc.build(story)
    return out_path

if __name__ == "__main__":
    generate_report()
