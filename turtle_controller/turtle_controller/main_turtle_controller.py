#!/usr/bin/env python3
import cmd

import rclpy
import math
from rclpy.node import Node
from robot_interfaces.msg import FoodStateArray
from turtlesim.msg import Pose as TurtlePose
from turtlesim.srv import Kill
from geometry_msgs.msg import Twist
from std_msgs.msg import String


class MainTurtleControllerNode(Node):
    def __init__(self):
        super().__init__("main_turtle_controller")

        self.main_pose = None
        self.food_positions = {}
        self.catch_threshold = 0.2
        self.k_angular = 4.0
        self.k_linear = 1.5
        self.max_linear = 2.5
        self.max_angular = 5.0

        self.killed_foods = set()
        self.pending_kills = set()

        self.food_subscriber = self.create_subscription(
            FoodStateArray,
            "/food_turtle_poses",
            self.food_callback,
            10,
        )
        self.main_turtle_subscriber = self.create_subscription(
            TurtlePose,
            "/turtle1/pose",
            self.main_turtle_callback,
            10,
        )

        self.cmd_publisher = self.create_publisher(
            Twist,
            "/turtle1/cmd_vel",
            10
        )
        self.killed_foods_publisher = self.create_publisher(
            String,
            "/killed_foods",
            10
        )

        self.kill_client = self.create_client(Kill, "/kill")
        while not self.kill_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Waiting for /kill service...")

        self.control_timer = self.create_timer(0.1, self.control_loop)

    def food_callback(self, msg: FoodStateArray):
        self.food_positions = {}
        for food in msg.foods:
            self.food_positions[food.name] = (
                food.pose.position.x,
                food.pose.position.y
            )    
    
    def main_turtle_callback(self, msg: TurtlePose):
        self.main_pose = msg

    
    def get_nearest_food(self):
        if self.main_pose is None:
            return None

        if not self.food_positions:
            return None

        x = self.main_pose.x
        y = self.main_pose.y

        nearest_name = None
        nearest_dist = float("inf")
        nearest_xy = None

        for name, (fx, fy) in self.food_positions.items():
            if name in self.killed_foods or name in self.pending_kills:
                continue

            dist = math.hypot(fx - x, fy - y)

            if dist < nearest_dist:
                nearest_dist = dist
                nearest_name = name
                nearest_xy = (fx, fy)

        if nearest_name is None:
            return None

        return nearest_name, nearest_xy, nearest_dist
    
    def control_loop(self):
        cmd = Twist()
        nearest = self.get_nearest_food()

        if nearest is None:
            self.cmd_publisher.publish(cmd)
            return

        name, (target_x, target_y), distance = nearest

        x = self.main_pose.x
        y = self.main_pose.y
        theta = self.main_pose.theta

        dx = target_x - x
        dy = target_y - y

        target_theta = math.atan2(dy, dx)

        angle_error = self.normalize_angle(target_theta - theta)

        cmd.angular.z = max(-self.max_angular, min(self.max_angular, self.k_angular * angle_error))

        cmd.linear.x = max(0.0, min(self.max_linear, self.k_linear * distance))

        # Eğer çok yaklaştıysa dur
        if distance < self.catch_threshold:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            self.request_kill(name)

        self.cmd_publisher.publish(cmd)

    def request_kill(self, name: str):
        if name in self.killed_foods or name in self.pending_kills:
            return

        req = Kill.Request()
        req.name = name
        future = self.kill_client.call_async(req)
        self.pending_kills.add(name)

        def _done_callback(future):
            self.pending_kills.discard(name)
            try:
                future.result()
                self.killed_foods.add(name)
                self.food_positions.pop(name, None)

                msg = String()
                msg.data = name
                self.killed_foods_publisher.publish(msg)

                self.get_logger().info(f"Killed food turtle: {name}")
                
            except Exception as e:
                self.get_logger().warn(f"Failed to kill {name}: {e}")

        future.add_done_callback(_done_callback)

    @staticmethod
    def normalize_angle(angle):
        return math.atan2(math.sin(angle), math.cos(angle))
            

def main(args=None):
    rclpy.init(args=args)
    node = MainTurtleControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
