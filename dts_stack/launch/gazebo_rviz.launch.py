import os

from ament_index_python import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    
    dts_dir = get_package_share_directory('dts_stack')
    
    # args that can be set from the command line
    model = LaunchConfiguration('model')
    rviz_config = LaunchConfiguration('rviz_config')
    use_sim_time = LaunchConfiguration('use_sim_time')
    frame_prefix = LaunchConfiguration('frame_prefix')
    
    # args that can be set from the command line or a default will be used
    robot_state_publisher_la = DeclareLaunchArgument(
        'model', default_value=os.path.join(dts_dir, 'urdf/ackermannRobot/robot.urdf.xacro'),
        description='Full path to robot urdf file')
    rviz_la = DeclareLaunchArgument(
        'rviz_config', default_value=os.path.join(dts_dir, 'rviz/rviz_display_config.rviz'),
        description='Full path to rviz display config file')
    use_sim_time_la = DeclareLaunchArgument(
        'use_sim_time', default_value='False',
        description='Use simulation/Gazebo clock')
        
    # start nodes and use args to set parameters
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{
            'robot_description': Command(['xacro ', model]),
            'use_sim_time': use_sim_time,
            'frame_prefix': frame_prefix,
        }]
    )
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=[
            '-d', rviz_config],
        parameters=[{
            'use_sim_time': use_sim_time,
        }]
    )

    # include launch files
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_ign_gazebo'), 'launch', 'ign_gazebo.launch.py')]),
        launch_arguments={
            'gz_args': '-r ' +  os.path.join(dts_dir, 'worlds/car_world.sdf')}.items()
    )

    spawn_entity = Node(package='ros_ign_gazebo', executable='create',
        arguments=['-topic', 'robot_description'],
        output='screen')
    
    # create launch description
    ld = LaunchDescription()
    
    # declare launch args
    ld.add_action(robot_state_publisher_la)
    ld.add_action(rviz_la)
    ld.add_action(use_sim_time_la)
    
    # start nodes
    ld.add_action(robot_state_publisher_node)
    ld.add_action(rviz_node)

    # run another launch file
    ld.add_action(gazebo) 

    # spawn robot in gazebo
    ld.add_action(spawn_entity)

    return ld
