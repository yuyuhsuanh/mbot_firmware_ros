import argparse
import rclpy
import time
from rclpy.node import Node
from geometry_msgs.msg import Twist

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--speed_factor', type=float, default=1.0,
                        help='Scale factor for linear and angular speeds (1.0-3.0)')
    args = parser.parse_args()
    sf = max(1.0, min(3.0, args.speed_factor))

    rclpy.init()
    node = Node('simple_step_cmd')
    pub = node.create_publisher(Twist, '/cmd_vel', 10)

    def move(linear_x, angular_z, duration):
        msg = Twist()
        msg.linear.x = float(linear_x)
        msg.angular.z = float(angular_z)
        
        # Publish for the specified duration
        start_time = time.time()
        while time.time() - start_time < duration:
            pub.publish(msg)
            time.sleep(0.05)

    import math
    turn_180_secs = math.pi / (1.0 * sf)

    print(f"Starting sequence (speed_factor={sf}, 180° turn={turn_180_secs:.2f}s)...")

    # 1. Drive forward
    move(0.5 * sf, 0.0, 4.0)
    move(0.0, 0.0, 1.0)

    # 2. CW rotation 4s
    move(0.0, -1.0 * sf, 4.0)
    move(0.0, 0.0, 1.0)

    # 3. CCW rotation 4s (back to original heading)
    move(0.0, 1.0 * sf, 4.0)
    move(0.0, 0.0, 1.0)

    # 4. Rotate 180° to face back toward start
    move(0.0, 1.0 * sf, turn_180_secs)
    move(0.0, 0.0, 1.0)

    # 5. Drive forward (same duration) — returns to start
    move(0.5 * sf, 0.0, 4.0)

    # Stop and cleanup
    pub.publish(Twist())
    print("Done.")
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()