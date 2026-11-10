import argparse
import rclpy
import time
from rclpy.node import Node
from geometry_msgs.msg import Twist

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--speed_factor', type=float, default=1.0,
                        help='Speed scale 1.0=slow(~0.2m/s,pi/4rad/s) to 4.0=fast(~0.8m/s,pirad/s)')
    args = parser.parse_args()
    sf = max(1.0, min(4.0, args.speed_factor))

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
    # Base speeds: slow=1.0 (0.2m/s, pi/4 rad/s), fast=4.0 (0.8m/s, pi rad/s)
    lin_spd = 0.2 * sf
    ang_spd = (math.pi / 4) * sf
    # Invert duration so physical path (0.8m fwd, pi rad turn) stays constant
    dur = 4.0 / sf

    print(f"Starting sequence (speed_factor={sf:.1f}, lin={lin_spd:.2f}m/s, "
          f"ang={ang_spd:.2f}rad/s, dur={dur:.2f}s)...")

    # 1. Drive forward ~0.8 m
    move(lin_spd, 0.0, dur)
    move(0.0, 0.0, 1.0)

    # 2. Right turn ~pi rad
    move(0.0, -ang_spd, dur)
    move(0.0, 0.0, 1.0)

    # 3. Left turn ~pi rad (back to original heading)
    move(0.0, ang_spd, dur)
    move(0.0, 0.0, 1.0)

    # Stop and cleanup
    pub.publish(Twist())
    print("Done.")
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()