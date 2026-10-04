import cv2
import os
import datetime
from saakshi.db import get_db
from saakshi.modules.custody import append_custody

def detect_motion():
    os.makedirs("out/events", exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, channel, file_path, normalized_time FROM segments WHERE file_path IS NOT NULL")
    segments = c.fetchall()
    
    total_events = 0
    for seg in segments:
        path = seg["file_path"]
        cap = cv2.VideoCapture(path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        
        norm_time_str = seg["normalized_time"]
        try:
            seg_start = datetime.datetime.strptime(norm_time_str, "%Y-%m-%d %H:%M:%S").timestamp()
        except:
            seg_start = 0.0
            
        fgbg = cv2.createBackgroundSubtractorMOG2(history=50, varThreshold=16, detectShadows=False)
        
        frame_idx = 0
        in_event = False
        event_start_frame = 0
        peak_area = 0.0
        peak_frame_img = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            fgmask = fgbg.apply(frame)
            fgmask = cv2.dilate(fgmask, None, iterations=2)
            contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_found = False
            max_area_in_frame = 0.0
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:
                    motion_found = True
                    if area > max_area_in_frame:
                        max_area_in_frame = area
                        
            if motion_found:
                if not in_event:
                    in_event = True
                    event_start_frame = frame_idx
                    peak_area = max_area_in_frame
                    peak_frame_img = frame.copy()
                else:
                    if max_area_in_frame > peak_area:
                        peak_area = max_area_in_frame
                        peak_frame_img = frame.copy()
            else:
                if in_event:
                    # Event ended
                    in_event = False
                    start_t = datetime.datetime.fromtimestamp(seg_start + event_start_frame/fps).strftime("%Y-%m-%d %H:%M:%S")
                    end_t = datetime.datetime.fromtimestamp(seg_start + frame_idx/fps).strftime("%Y-%m-%d %H:%M:%S")
                    
                    thumb_path = f"out/events/seg{seg['id']}_{event_start_frame}.jpg"
                    if peak_frame_img is not None:
                        cv2.imwrite(thumb_path, peak_frame_img)
                        
                    c.execute("INSERT INTO motion_events (segment_id, channel, start_time, end_time, peak_area, thumbnail_path) VALUES (?, ?, ?, ?, ?, ?)",
                              (seg["id"], seg["channel"], start_t, end_t, peak_area, thumb_path))
                    total_events += 1
                    
            frame_idx += 1
            
        if in_event:
            start_t = datetime.datetime.fromtimestamp(seg_start + event_start_frame/fps).strftime("%Y-%m-%d %H:%M:%S")
            end_t = datetime.datetime.fromtimestamp(seg_start + frame_idx/fps).strftime("%Y-%m-%d %H:%M:%S")
            thumb_path = f"out/events/seg{seg['id']}_{event_start_frame}.jpg"
            if peak_frame_img is not None:
                cv2.imwrite(thumb_path, peak_frame_img)
            c.execute("INSERT INTO motion_events (segment_id, channel, start_time, end_time, peak_area, thumbnail_path) VALUES (?, ?, ?, ?, ?, ?)",
                      (seg["id"], seg["channel"], start_t, end_t, peak_area, thumb_path))
            total_events += 1
            
        cap.release()
        
    conn.commit()
    conn.close()
    
    append_custody("Analytics", f"Detected {total_events} motion events across videos")
    return total_events

if __name__ == "__main__":
    print(detect_motion())
