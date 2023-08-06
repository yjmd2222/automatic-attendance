import atomacos
from AppKit import NSScreen
a, b = NSScreen.mainScreen().frame().size
print(a, b)
z = atomacos.getAppRefByBundleId('us.zoom.xos')

from ApplicationServices import AXValueCreate, kAXValueCGPointType
import Quartz.CoreGraphics as CG

x, y = 0, 0
point = CG.CGPoint(x=x, y=y)
# pointsize = CG.CGPoint(0, 25, 1980, 970)
c = z.findFirst(AXTitle='Zoom 회의')
c.AXPosition = AXValueCreate(kAXValueCGPointType, point)
c.AXFrame = AXValueCreate(kAXValueCGPointType, point)

from AppKit import NSScreen

def get_desktop_size():
    screen = NSScreen.mainScreen()
    frame = screen.visibleFrame()
    width = frame.size.width
    height = frame.size.height
    print(frame)
    return int(width), int(height)

if __name__ == "__main__":
    desktop_width, desktop_height = get_desktop_size()
    print(f"Desktop size: {desktop_width}x{desktop_height} pixels")
