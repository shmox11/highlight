# shield_break_event.py

import cv2


def detect_shield_break_event(frame, templates, threshold):
    center_roi_gray = cv2.cvtColor(frame[440:730, 900:1140], cv2.COLOR_BGR2GRAY)

    for template in templates['shield_break']:
        result = cv2.matchTemplate(center_roi_gray, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val > threshold:
            return 'shield_break', max_loc

    return None, None