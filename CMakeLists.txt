cmake_minimum_required(VERSION 3.0.2)
project(cmeresearch_bringup)

## Compile as C++11, supported in ROS Kinetic and newer
# add_compile_options(-std=c++11)

## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS xyz)
## is used, also find other catkin packages
find_package(catkin REQUIRED)

## System dependencies are found with CMake's conventions
# find_package(Boost REQUIRED COMPONENTS system)


## Uncomment this if the package has a setup.py. This macro ensures
## modules and global scripts declared therein get installed
## See http://ros.org/doc/api/catkin/html/user_guide/setup_dot_py.html
# catkin_python_setup()

################################################
## Declare ROS messages, services and actions ##
################################################

## To declare and build messages, services or actions from within this
## package, follow these steps:
## * Let MSG_DEP_SET be the set of packages whose message types you use in
##   your messages/services/actions (e.g. std_msgs, actionlib_msgs, ...).
## * In the file package.xml:
##   * add a build_depend tag for "message_generation"
##   * add a build_depend and a exec_depend tag for each package in MSG_DEP_SET
##   * If MSG_DEP_SET isn't empty the following dependency has been pulled in
##     but can be declared for certainty nonetheless:
##     * add a exec_depend tag for "message_runtime"
## * In this file (CMakeLists.txt):
##   * add "message_generation" and every package in MSG_DEP_SET to
##     find_package(catkin REQUIRED COMPONENTS ...)
##   * add "message_runtime" and every package in MSG_DEP_SET to
##     catkin_package(CATKIN_DEPENDS ...)
##   * uncomment the add_*_files sections below as needed
##     and list every .msg/.srv/.action file to be processed
##   * uncomment the generate_messages entry below
##   * add every package in MSG_DEP_SET to generate_messages(DEPENDENCIES ...)

## Generate messages in the 'msg' folder
# add_message_files(
#   FILES
#   Message1.msg
#   Message2.msg
# )

## Generate services in the 'srv' folder
# add_service_files(
#   FILES
#   Service1.srv
#   Service2.srv
# )

## Generate actions in the 'action' folder
# add_action_files(
#   FILES
#   Action1.action
#   Action2.action
# )

## Generate added messages and services with any dependencies listed here
# generate_messages(
#   DEPENDENCIES
#   std_msgs  # Or other packages containing msgs
# )

################################################
## Declare ROS dynamic reconfigure parameters ##
################################################

## To declare and build dynamic reconfigure parameters within this
## package, follow these steps:
## * In the file package.xml:
##   * add a build_depend and a exec_depend tag for "dynamic_reconfigure"
## * In this file (CMakeLists.txt):
##   * add "dynamic_reconfigure" to
##     find_package(catkin REQUIRED COMPONENTS ...)
##   * uncomment the "generate_dynamic_reconfigure_options" section below
##     and list every .cfg file to be processed

## Generate dynamic reconfigure parameters in the 'cfg' folder
# generate_dynamic_reconfigure_options(
#   cfg/DynReconf1.cfg
#   cfg/DynReconf2.cfg
# )

###################################
## catkin specific configuration ##
###################################
## The catkin_package macro generates cmake config files for your package
## Declare things to be passed to dependent projects
## INCLUDE_DIRS: uncomment this if your package contains header files
## LIBRARIES: libraries you create in this project that dependent projects also need
## CATKIN_DEPENDS: catkin_packages dependent projects also need
## DEPENDS: system dependencies of this project that dependent projects also need
catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES unico_bringup
#  CATKIN_DEPENDS other_catkin_pkg
#  DEPENDS system_lib
)

###########
## Build ##
###########

## Specify additional locations of header files
## Your package locations should be listed before other locations
include_directories(
# include
# ${catkin_INCLUDE_DIRS}
)

## Declare a C++ library
# add_library(${PROJECT_NAME}
#   src/${PROJECT_NAME}/unico_bringup.cpp
# )

## Add cmake target dependencies of the library
## as an example, code may need to be generated before libraries
## either from message generation or dynamic reconfigure
# add_dependencies(${PROJECT_NAME} ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})

## Declare a C++ executable
## With catkin_make all packages are built within a single CMake context
## The recommended prefix ensures that target names across packages don't collide
# add_executable(${PROJECT_NAME}_node src/unico_bringup_node.cpp)

## Rename C++ executable without prefix
## The above recommended prefix causes long target names, the following renames the
## target back to the shorter version for ease of user use
## e.g. "rosrun someones_pkg node" instead of "rosrun someones_pkg someones_pkg_node"
# set_target_properties(${PROJECT_NAME}_node PROPERTIES OUTPUT_NAME node PREFIX "")

## Add cmake target dependencies of the executable
## same as for the library above
# add_dependencies(${PROJECT_NAME}_node ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})

## Specify libraries to link a library or executable target against
# target_link_libraries(${PROJECT_NAME}_node
#   ${catkin_LIBRARIES}
# )

#############
## Install ##
#############

# all install targets should use catkin DESTINATION variables
# See http://ros.org/doc/api/catkin/html/adv_user_guide/variables.html

## Mark executable scripts (Python etc.) for installation
## in contrast to setup.py, you can choose the destination
# catkin_install_python(PROGRAMS
#   scripts/my_python_script
#   DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
# )

## Mark executables for installation
## See http://docs.ros.org/melodic/api/catkin/html/howto/format1/building_executables.html
# install(TARGETS ${PROJECT_NAME}_node
#   RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
# )

## Mark libraries for installation
## See http://docs.ros.org/melodic/api/catkin/html/howto/format1/building_libraries.html
# install(TARGETS ${PROJECT_NAME}
#   ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
#   LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
#   RUNTIME DESTINATION ${CATKIN_GLOBAL_BIN_DESTINATION}
# )

## Mark cpp header files for installation
# install(DIRECTORY include/${PROJECT_NAME}/
#   DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}
#   FILES_MATCHING PATTERN "*.h"
#   PATTERN ".svn" EXCLUDE
# )

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
 DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/config/ash/
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
 DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/config/unicomini/
)
install(FILES
 config/cmexa/twist_mux.yaml
 config/cmexa/joy.yaml
 config/cmexa/logi_teleop.yaml
 config/cmexa/stage_navigation.rviz
 config/cmexa/mqtt_bridge_params.yaml
 config/cmexa/base_local_planner_params.yaml
 config/cmexa/costmap_common_params.yaml
 config/cmexa/global_costmap_params.yaml
 config/cmexa/local_costmap_params.yaml
 config/cmexa/slam_toolbox_localization.yaml
 config/cmexa/slam_toolbox_mapping.yaml
 DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/config/cmexa/
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
 DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/config/cmexaiii/
)

install(FILES
 install/autostart/env.bash
 DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/install
) 
install(FILES
 launch/robot.launch
 launch/unico_mini.launch
 driver/cam_web_video.launch
 simulation/sim_robot_only_mqtt.launch
 simulation/sim_robot_headless_mqtt.launch
 simulation/sim_robot_controller_mqtt.launch
 simulation/sim_cmexa_full_localization.launch
 simulation/sim_cmexa_full_mapping.launch
 DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch
)

#############
## Testing ##
#############

## Add gtest based cpp test target and link libraries
# catkin_add_gtest(${PROJECT_NAME}-test test/test_unico_bringup.cpp)
# if(TARGET ${PROJECT_NAME}-test)
#   target_link_libraries(${PROJECT_NAME}-test ${PROJECT_NAME})
# endif()

## Add folders to be run by python nosetests
# catkin_add_nosetests(test)
