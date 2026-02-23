# 🐢 ROS 2 Turtle Catch Them All

This project is an autonomous "hunter-gatherer" turtle simulation developed using the ROS 2 framework. Running alongside the turtlesim node, the system detects randomly spawning targets (food turtles), calculates its trajectory using a proportional controller (P-Controller), and hunts the targets one by one.

![Screencastfrom2026-02-2316-31-54-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/a7bd9645-c6f5-4f20-bce7-c7c27e8f99ae)

## ⚙️ System Architecture & Features

The project has a modular structure and consists of 4 main packages:

* **`robot_interfaces`**: Contains custom message types (`FoodState` and `FoodStateArray`) specifically designed to carry the name and position data of the targets.
* **`turtle_spawner`**: Spawns new targets (food) into the scene at regular intervals. It publishes the current positions and names of the active targets on the screen via the `/food_turtle_poses` topic.
* **`turtle_controller`**: The brain of the main turtle. It dynamically calculates the nearest target and sends velocity commands (Twist) over `/turtle1/cmd_vel` based on the angular error and distance to the target. Once the target is reached, it calls turtlesim's `kill` service to remove the target from the scene.
* **`robot_bringup`**: Contains the launch files required to start the entire system and all nodes with a single command.

## 🛠️ Installation

To run this project in your own ROS 2 workspace, follow the steps below:

```bash
# Navigate to the src directory of your workspace
cd ~/ros2_ws/src

# Clone the repository
git clone [https://github.com/muhammet-alaybey-cilesiz/ros2-turtle-catch-them-all.git](https://github.com/muhammet-alaybey-cilesiz/ros2-turtle-catch-them-all.git)

# Build the workspace
cd ~/ros2_ws
colcon build

# Source the environment
source install/setup.bash

🚀 Usage
#To launch the entire system along with the simulation in one go, run the following command:
ros2 launch robot_bringup turtle_catch_them_all_launch.xml

