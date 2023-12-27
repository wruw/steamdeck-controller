import cv2
from pyartnet import ArtNetNode
import asyncio

async def change():
    node = ArtNetNode('IP', 6454)
    universe = node.add_universe(0)
    row1pixels = []
    for i in range(0, 24):
        row1pixels.append(universe.add_channel(start=i*3, range=3))
    row2pixels = []
    for i in range(24, 48):
        row2pixels.append(universe.add_channel(start=i*3, range=3))
    vid = cv2.VideoCapture(0)
    while(True):
        ret, frame = vid.read()
        for i in range(0, 24):
            part = frame[360-40:360+40, i*80:(i+1)*80]
            b, g, r = cv2.split(part)
            row1pixels[i].set_levels(r, g, b)
        for i in range(24, 48):
            part = frame[720-40:720+40, i*80:(i+1)*80]
            b, g, r = cv2.split(part)
            row2pixels[i-24].set_levels(r, g, b)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

asyncio.run(change())