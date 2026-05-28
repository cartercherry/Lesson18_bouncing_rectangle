# Rotate a rectangle and have it bounce off walls of container.  


import cv2
import numpy as np

# Window/frame size
W, H = 800, 600
RIGHT = W - 1
BOTTOM = H - 1

# Window name
window_name = "Rotating bouncing rectangle"

# Rectangle center position
cx, cy = 400.0, 300.0

# Linear velocity
vx, vy = 3.0, 2.0

# Rectangle size
rect_w, rect_h = 160, 80

# Rotation
angle = 0.0
angular_velocity = 3.0   # degrees per frame

# Create the named window
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, W, H)

# Raspberry Pi OS Bookworm workaround:
# Do not move the empty named window immediately.
# Move it after the first frame has actually been shown.
window_moved = False

try:
    while True:
        frame = np.zeros((H, W, 3), dtype=np.uint8)

        # Update position and rotation
        cx += vx
        cy += vy
        angle = (angle + angular_velocity) % 360

        # Get rotated rectangle corner points
        box = cv2.boxPoints(((cx, cy), (rect_w, rect_h), angle))

        # Find the rectangle's actual rotated boundaries
        min_x = box[:, 0].min()
        max_x = box[:, 0].max()
        min_y = box[:, 1].min()
        max_y = box[:, 1].max()

        # Collision correction: left wall
        if min_x < 0:
            cx += -min_x
            vx = abs(vx)

        # Collision correction: right wall
        if max_x > RIGHT:
            cx -= max_x - RIGHT
            vx = -abs(vx)

        # Collision correction: top wall
        if min_y < 0:
            cy += -min_y
            vy = abs(vy)

        # Collision correction: bottom wall
        if max_y > BOTTOM:
            cy -= max_y - BOTTOM
            vy = -abs(vy)

        # Recompute box after possible collision correction
        box = cv2.boxPoints(((cx, cy), (rect_w, rect_h), angle))
        box_int = np.intp(box)

        # Draw rotated rectangle
        cv2.polylines(frame, [box_int], isClosed=True, color=(0, 255, 0), thickness=3)

        # Draw center point
        cv2.circle(frame, (int(cx), int(cy)), 4, (0, 0, 255), -1)

        # Show frame
        cv2.imshow(window_name, frame)

        # Process GUI events and keyboard input
        key = cv2.waitKey(16) & 0xFF

        # Move window after it has actually appeared
        if not window_moved:
            cv2.moveWindow(window_name, 0, 50)
            window_moved = True

        # Quit with q
        if key == ord("q"):
            break
except KeyboardInterrupt:
    print('\n terminating...')

finally:
    cv2.destroyAllWindows()
