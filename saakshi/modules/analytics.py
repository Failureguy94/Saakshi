import cv2
from saakshi.db import get_db
from saakshi.modules.custody import append_custody

def detect_motion():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, channel, file_path FROM segments WHERE file_path IS NOT NULL")
    segments = c.fetchall()
    
    total_events = 0
    for seg in segments:
        path = seg["file_path"]
        cap = cv2.VideoCapture(path)
        
        ret, frame1 = cap.read()
        if not ret:
            continue
        
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
        
        frame_idx = 0
        events_in_seg = 0
        
        while True:
            ret, frame2 = cap.read()
            if not ret:
                break
                
            frame_idx += 1
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)
            
            delta = cv2.absdiff(gray1, gray2)
            thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            
            contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_found = False
            for contour in contours:
                if cv2.contourArea(contour) > 100:
                    motion_found = True
                    break
                    
            if motion_found:
                c.execute("INSERT INTO motion_events (segment_id, channel, frame_index) VALUES (?, ?, ?)",
                          (seg["id"], seg["channel"], frame_idx))
                events_in_seg += 1
                # Skip a few frames to avoid event flood
                for _ in range(5):
                    cap.read()
                    frame_idx += 1
                    
            # We don't update gray1 = gray2 so it compares with the static first frame
            
        cap.release()
        total_events += events_in_seg
        
    conn.commit()
    conn.close()
    
    append_custody("Analytics", f"Detected {total_events} motion events across videos")
    return total_events

if __name__ == "__main__":
    print(detect_motion())
