cmake_minimum_required(VERSION 3.8)
project(cmeresearch_bringup)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
find_package(rosidl_default_generators REQUIRED)

if(BUILD_TESTING)
    find_package(ament_lint_auto REQUIRED)
    # the following line skips the linter which checks for copyrights
    # comment the line when a copyright and license is added to all source files
    set(ament_cmake_copyright_FOUND TRUE)
    # the following line skips cpplint (only works in a git repo)
    # comment the line when this package is in a git repo and when
    # a copyright and license is added to all source files
    set(ament_cmake_cpplint_FOUND TRUE)
    ament_lint_auto_find_test_dependencies()
endif()

## Mark other files for installation (e.g. launch and bag files, etc.)
install(FILES
 config/ash/control.yaml
 config/ash/logi_teleop.yaml
 config/ash/twist_mux.yaml
 config/ash/joy.yaml
 config/ash/robot_localization.yaml
 config/ash/watchdog.yaml
 config/ash/usb_cam.yml
 config/ash/web_video_server.yml
 config/ash/stage_navigation.rviz
 config/ash/mqtt_bridge_params.yaml
 config/ash/mqtt_bridge_for_sim_ctrl.yaml
 DESTINATION share/${PROJECT_NAME}/config/ash/
)
install(FILES
 config/unicomini/control.yaml
 config/unicomini/logi_teleop.yaml
 config/unicomini/twist_mux.yaml
 config/unicomini/joy.yaml
 config/unicomini/robot_localization.yaml
 config/unicomini/watchdog.yaml
 config/unicomini/usb_cam.yml
 config/unicomini/web_video_server.yml
 config/unicomini/stage_navigation.rviz
 config/unicomini/mqtt_bridge_params.yaml
 DESTINATION share/${PROJECT_NAME}/config/unicomini/
)
install(FILES
 config/cmexa/twist_mux.yaml
 config/cmexa/joy.yaml
 config/cmexa/cmexa_base_mecanum_controllers.yaml
 config/cmexa/pdp.config.yaml
 config/cmexa/stage_navigation.rviz
 config/cmexa/mqtt_bridge_params.yaml
 config/cmexa/mqtt_client_params.yaml
 config/cmexa/base_local_planner_params.yaml
 config/cmexa/costmap_common_params.yaml
 config/cmexa/global_costmap_params.yaml
 config/cmexa/local_costmap_params.yaml
 config/cmexa/slam_toolbox_localization.yaml
 config/cmexa/slam_toolbox_mapping.yaml
 config/cmexa/xbox.config.yaml
 config/cmexa/joy2twist_ugv.yaml
 config/cmexa/twist_mux_topics.yaml
 config/cmexa/twist_mux_locks.yaml
 DESTINATION share/${PROJECT_NAME}/config/cmexa/
)

install(FILES
 config/cmexamini/twist_mux.yaml
 config/cmexamini/joy.yaml
 config/cmexamini/cmexamini_base_diff_controllers.yaml
 config/cmexamini/diffbot_controllers.yaml
 config/cmexamini/stage_navigation.rviz
 config/cmexamini/base_local_planner_params.yaml
 config/cmexamini/costmap_common_params.yaml
 config/cmexamini/global_costmap_params.yaml
 config/cmexamini/local_costmap_params.yaml
 config/cmexamini/slam_toolbox_localization.yaml
 config/cmexamini/slam_toolbox_mapping.yaml
 config/cmexamini/joy2twist_ugv.yaml
 config/cmexamini/twist_mux_topics.yaml
 config/cmexamini/twist_mux_locks.yaml
 DESTINATION share/${PROJECT_NAME}/config/cmexamini/
)



install(FILES
 config/cmexaiii/twist_mux.yaml
 config/cmexaiii/joy.yaml
 config/cmexaiii/logi_teleop.yaml
 config/cmexaiii/stage_navigation.rviz
 config/cmexaiii/mqtt_bridge_params.yaml
 config/cmexaiii/base_local_planner_params.yaml
 config/cmexaiii/costmap_common_params.yaml
 config/cmexaiii/global_costmap_params.yaml
 config/cmexaiii/local_costmap_params.yaml
 config/cmexaiii/slam_toolbox_localization.yaml
 config/cmexaiii/slam_toolbox_mapping.yaml
 DESTINATION share/${PROJECT_NAME}/config/cmexaiii/
)

install(FILES
 install/autostart/env.bash
 DESTINATION share/${PROJECT_NAME}/install
)

install(FILES
 driver/teleop.launch.py
 driver/twist_mux.launch.py
 DESTINATION share/${PROJECT_NAME}/driver
)

install(FILES
 launch/robot.launch
 launch/unico_mini.launch
 launch/cmexa_omni.launch.py
 launch/cmexamini_diff.launch.py
 launch/cmexa_omni_navi_mapping.launch.py

 simulation/sim_robot_only_mqtt.launch
 simulation/sim_robot_headless_mqtt.launch
 simulation/sim_robot_controller_mqtt.launch
 simulation/sim_cmexa_full_localization.launch
 simulation/sim_cmexa_full_mapping.launch
 DESTINATION share/${PROJECT_NAME}/launch
)

install(FILES
    driver/teleop_twist_joy.launch.py
    driver/joy2twist.launch.py
    driver/teleop_xinput.launch.py
    DESTINATION share/${PROJECT_NAME}/launch
)

#ROS2
install(FILES
    config/unicomini/ros2/joy.yaml
    config/unicomini/ros2/pdp.config.yaml
    config/unicomini/ros2/unico_base_controllers.yaml
    DESTINATION share/${PROJECT_NAME}/config/unicomini/
)

ament_package()
