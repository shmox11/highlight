import cv2
import os
from ...event_detection.regions.center_roi import get_center_roi
import logging

logging.basicConfig(level=logging.INFO)

def get_shield_break_templates():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, 'thumbnail', 'shield_break')
    
    templates = [cv2.imread(os.path.join(template_dir, f)) for f in os.listdir(template_dir) if f.endswith('.png')]
    
    # Debugging: Check Template Loading
    print(f"Loaded {len(templates)} shield break templates.")
    
    return templates

def detect_shield_break_event(frame, threshold=0.8):
    roi, top_left, bottom_right = get_center_roi(frame)
    roi = frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
    
    templates = get_shield_break_templates()
    
    best_match_val = -1
    best_match_loc = None
    
    scales = [i for i in range(25, 200, 10)]
    
    for scale in scales:
        for template in templates:
            resized_template = cv2.resize(template, (int(template.shape[1] * scale / 100), int(template.shape[0] * scale / 100)))
            
            if roi.shape[0] < resized_template.shape[0] or roi.shape[1] < resized_template.shape[1]:
                continue

            result = cv2.matchTemplate(roi, resized_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            # Debugging: Visualize Template Matching
            cv2.imshow(f"Matching for scale {scale}", result)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            # Debugging: Print Matching Values
            print(f"Matching value for scale {scale}: {max_val:.3f}")

            if max_val > best_match_val:
                best_match_val = max_val
                best_match_loc = (max_loc[0] + top_left[0], max_loc[1] + top_left[1])

    if best_match_val > threshold:
        print(f"***Shield_break detected at location: {best_match_loc}")
        print(f"Match confidence: {best_match_val*100:.2f}%")
        return True, best_match_loc
    else:
        print("Shield_break event not detected.")
        return False, None
