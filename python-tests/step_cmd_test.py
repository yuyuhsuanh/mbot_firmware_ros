import argparse
import rclpy
import time
from math import pi
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import Trigger

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--speed-factor', type=int, default=1, choices=range(1, 5),
                        metavar='1-4', help='Speed scale factor (1–4)')
    args = parser.parse_args()
    factor = args.speed_factor

    rclpy.init()
    node = Node('simple_step_cmd')
    pub = node.create_publisher(Twist, '/cmd_vel', 10)

    # Reset odometry before starting
    reset_client = node.create_client(Trigger, '/reset_odometry')
    reset_client.wait_for_service(timeout_sec=5.0)
    reset_client.call_async(Trigger.Request())
    rclpy.spin_once(node, timeout_sec=0.5)
    print("Odometry reset.")

    def move(linear_x, angular_z, duration):
        msg = Twist()
        msg.linear.x = float(linear_x)
        msg.angular.z = float(angular_z)

        # Publish for the specified duration
        start_time = time.time()
        while time.time() - start_time < duration:
            pub.publish(msg)
            time.sleep(0.05)

    print(f"Starting sequence (factor={factor})...")

    # 1. Drive forward 0.5 m/s for 4s
    move(0.2 * factor, 0.0, 4.0)

    # 2. Wait 1s
    move(0.0, 0.0, 1.0)

    # 3. Rotate CW (negative) for 4s
    move(0.0, -0.25 * pi * factor, 4.0)

    # 4. Wait 1s
    move(0.0, 0.0, 1.0)

    # 5. Rotate CCW (positive) for 4s
    move(0.0, 0.25 * pi * factor, 4.0)

    # Stop and cleanup
    pub.publish(Twist())
    print("Done.")
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
