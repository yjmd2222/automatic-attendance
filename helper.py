'''
Helper methods
'''

import os

import pyautogui

def get_file_path(filename, sub=None):
    'return full file path'
    if sub:
        return os.path.join(os.getcwd(), sub, filename)
    return os.path.join(os.getcwd(), filename)


def get_last_match(image):
    'For checking distinct elements. Nothing found if (0,0,0,0) returned'
    positions = [(0,0,0,0)]
    threshhold = 8

    all_locations = list(pyautogui.locateAllOnScreen(image, confidence=0.7))
    for idx, pos in enumerate(all_locations):
        if idx == len(all_locations) - 1:
            break
        else:
            if abs(all_locations[idx][0] - positions[-1][0]) +\
                abs(all_locations[idx][1] - positions[-1][1]) > threshhold:
                positions.append(pos)

    return positions[-1]