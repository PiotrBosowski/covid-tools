import numpy as np

pixels = np.array([0, 0, 0, 0, 0])
window_top = np.max(pixels)
window_bot = 0
mean = 0

pixels = pixels.astype(np.float64)
# clipping the image would be OK as well
pixels[(pixels > window_top) | (pixels < window_bot)] = mean
pixels -= window_bot
window_top -= window_bot
# DANGER: performing this step makes image human-readable, but is also
# introduces some irregularities in the image histogram (trying to extend
# (0, n) range to cover whole (0, 255) will result in histogram-holes if
# n < 255). TODO: think about giving up on it -> float processing framework
try:
    pixels *= (255.0 / float(window_top))
except ZeroDivisionError:
    pixels = np.zeros_like(pixels)
print(np.around(pixels))