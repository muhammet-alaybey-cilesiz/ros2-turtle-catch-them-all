#!/usr/bin/env python3
import rclpy
import random
from rclpy.node import Node
from turtlesim.srv import Spawn
from turtlesim.msg import Pose
from robot_interfaces.msg import FoodState, FoodStateArray
from std_msgs.msg import String


class FoodTurtleSpawnerNode(Node): 
    def __init__(self):
        super().__init__("food_turtle_spawner")

        self.food_counter = 0        # unique isim üretmek için
        self.active_foods = {}       # ekrandaki food turtle'lar # key: food_name, value: Pose
        self.max_food = 10           # opsiyonel limit
        self.spawn_interval = 2.0    # saniye cinsinden

        self.food_turtle_pose_publisher = self.create_publisher(
            FoodStateArray,
            "/food_turtle_poses",
            10
        )
        self.killed_foods_subscriber = self.create_subscription(
            String,
            "/killed_foods",
            self.killed_foods_callback,
            10
        )

        self.spawn_client = self.create_client(Spawn, "spawn")
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Waiting for spawn service...")  

        self.create_timer(self.spawn_interval, self.spawn_food_timer_callback)

    def killed_foods_callback(self, msg: String):
        name = msg.data
        if name in self.active_foods:
            self.active_foods.pop(name, None)
            self.publish_food_states() 
            
    def food_pose_callback(self, msg, name):
        self.active_foods[name] = msg
        self.publish_food_states()

    def publish_food_states(self):
        msg = FoodStateArray()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "world"

        for name, food_pose in self.active_foods.items():
            if food_pose is None:
                continue

            food_state = FoodState()
            food_state.name = name

            food_state.pose.position.x = food_pose.x
            food_state.pose.position.y = food_pose.y
            food_state.pose.position.z = 0.0

            food_state.pose.orientation.w = 1.0

            msg.foods.append(food_state)

        self.food_turtle_pose_publisher.publish(msg)


    def spawn_food_timer_callback(self):
        if len(self.active_foods) < self.max_food:
            x = self.get_random_coordinate(0.5, 10.5)  # turtlesim sınırları içinde
            y = self.get_random_coordinate(0.5, 10.5 ) # turtlesim sınırları içinde
            theta = 0.0
            name = f"food_{self.food_counter}"
            self.spawn_food_turtle(x, y, theta, name)

    def get_random_coordinate(self, min_val, max_val):
        return round(random.uniform(min_val, max_val), 2)

    def spawn_food_turtle(self, x, y, theta, name):
        if len(self.active_foods) >= self.max_food:
            self.get_logger().warn("Max food limit reached. Cannot spawn more.")
            return

        req = Spawn.Request()
        req.x = x
        req.y = y
        req.theta = theta
        req.name = name
        
        future = self.spawn_client.call_async(req)

        def spawn_response_callback(future):
            try:
                response = future.result()
                self.get_logger().info(f"Spawned food turtle: {response.name} at ({x}, {y})")
                self.active_foods[response.name] = None
                self.create_subscription(Pose,f"/{response.name}/pose",
                                         lambda msg, name=response.name:
                                        self.food_pose_callback(msg, name),10)
                self.food_counter += 1

            except Exception as e:
                self.get_logger().error(f"Failed to spawn food turtle: {e}")

        future.add_done_callback(spawn_response_callback)


def main(args=None):
    rclpy.init(args=args)
    node = FoodTurtleSpawnerNode() 
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()