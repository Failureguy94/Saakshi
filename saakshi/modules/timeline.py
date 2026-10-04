from saakshi.db import get_db
from saakshi.modules.custody import append_custody
import datetime
import statistics

def analyze_timeline():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, channel, dvr_time, camera_time FROM segments")
    segments = c.fetchall()
    
    ch_data = {}
    for s in segments:
        ch = s["channel"]
        if not s["dvr_time"] or not s["camera_time"]: continue
        
        try:
            d_time = datetime.datetime.strptime(s["dvr_time"], "%Y-%m-%d %H:%M:%S").timestamp()
            c_time = datetime.datetime.strptime(s["camera_time"], "%Y-%m-%d %H:%M:%S").timestamp()
        except:
            continue
            
        diff = d_time - c_time
        if ch not in ch_data: ch_data[ch] = []
        ch_data[ch].append((c_time, diff, s["id"], d_time))
        
    summary = {}
    
    for ch, data in ch_data.items():
        data.sort(key=lambda x: x[0])
        diffs = [x[1] for x in data]
        median_offset = statistics.median(diffs)
        
        n = len(data)
        slope = 0.0
        if n > 1:
            x = [d[0] for d in data]
            y = diffs
            sum_x = sum(x)
            sum_y = sum(y)
            sum_x2 = sum(xi*xi for xi in x)
            sum_xy = sum(xi*yi for xi, yi in zip(x, y))
            denominator = (n * sum_x2 - sum_x * sum_x)
            if denominator != 0:
                slope = (n * sum_xy - sum_x * sum_y) / denominator
            
        drift_per_hour = slope * 3600
        
        residuals = []
        for c_time, diff, seg_id, d_time in data:
            expected_diff = median_offset + slope * (c_time - data[0][0])
            residuals.append(abs(diff - expected_diff))
            
            norm_ts = d_time - expected_diff
            norm_str = datetime.datetime.fromtimestamp(norm_ts).strftime("%Y-%m-%d %H:%M:%S")
            c.execute("UPDATE segments SET normalized_time=? WHERE id=?", (norm_str, seg_id))
            
        spread = statistics.mean(residuals) if residuals else 0
        confidence = max(0.0, 1.0 - spread / 5.0)
        
        summary[ch] = {
            "channel": ch,
            "offset_seconds": median_offset,
            "drift_per_hour": drift_per_hour,
            "confidence": confidence
        }
    
    conn.commit()
    conn.close()
    
    max_disagree_before = 0.0
    max_disagree_after = 0.0
    if len(summary) >= 2:
        offsets = [v["offset_seconds"] for v in summary.values()]
        max_disagree_before = max(offsets) - min(offsets)
        
    append_custody("Timeline", f"Timeline analyzed. Max disagreement before: {max_disagree_before:.2f}s, after: {max_disagree_after:.2f}s.")
    return {"channels": summary, "max_disagreement_before": max_disagree_before, "max_disagreement_after": max_disagree_after}

if __name__ == "__main__":
    print(analyze_timeline())
