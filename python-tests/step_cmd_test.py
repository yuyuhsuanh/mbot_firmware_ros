import argparse
import rclpy
import time
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import Trigger

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--speed_factor', type=float, default=1.0,
                        help='Scale factor for linear and angular speeds (e.g. 0.4=slow, 1.6=fast)')
    args = parser.parse_args()
    sf = args.speed_factor

    rclpy.init()
    node = Node('simple_step_cmd')
    pub = node.create_publisher(Twist, '/cmd_vel', 10)
    reset_client = node.create_client(Trigger, 'reset_odometry')

    def reset_odom():
        if not reset_client.wait_for_service(timeout_sec=3.0):
            print("reset_odometry service not available, skipping reset")
            return
        future = reset_client.call_async(Trigger.Request())
        rclpy.spin_until_future_complete(node, future, timeout_sec=3.0)
        if future.result() and future.result().success:
            print("Odometry (wheel + gyro) reset")
        else:
            print("Reset call failed or timed out")

    def move(linear_x, angular_z, duration):
        msg = Twist()
        msg.linear.x = float(linear_x)
        msg.angular.z = float(angular_z)

        start_time = time.time()
        while time.time() - start_time < duration:
            pub.publish(msg)
            time.sleep(0.05)

    reset_odom()
    print(f"Starting sequence (speed_factor={sf})...")

    # 1. Drive forward 0.5*sf m/s for 4s
    move(0.5 * sf, 0.0, 4.0)

    # 2. Wait 1s
    move(0.0, 0.0, 1.0)

    # 3. Rotate CW for 4s
    move(0.0, -1.0 * sf, 4.0)

    # 4. Wait 1s
    move(0.0, 0.0, 1.0)

    # 5. Rotate CCW for 4s
    move(0.0, 1.0 * sf, 4.0)

    # Stop and cleanup
    pub.publish(Twist())
    print("Done.")
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
