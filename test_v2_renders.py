#!/usr/bin/env python3
import os
import math
from PIL import Image, ImageDraw, ImageFont

# Let us verify font loading
FONT_SANS_BOLD = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
FONT_MONO_BOLD = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf"
if not os.path.exists(FONT_SANS_BOLD):
    FONT_SANS_BOLD = "/system/fonts/Roboto-Regular.ttf"
if not os.path.exists(FONT_MONO_BOLD):
    FONT_MONO_BOLD = FONT_SANS_BOLD

print("Fonts available:", FONT_SANS_BOLD, FONT_MONO_BOLD)
