from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import Command
import os
def generate_launch_description():
    package_share = get_package_share_directory(
        'six_dof_arm_description'
    )
    ros_gz_sim_share = get_package_share_directory(
        'ros_gz_sim'
    )
    xacro_file = os.path.join(
        package_share,
        'urdf',
        'six_dof_arm.urdf.xacro'
    )
    gazebo_launch_file = os.path.join(
        ros_gz_sim_share,
        'launch',
        'gz_sim.launch.py'
    )
    robot_description = {
        'robot_description': Command([
            'xacro ',
            xacro_file
        ])
    }
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch_file),
        launch_arguments={
            'gz_args': '-r empty.sdf'
        }.items()
    )
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            robot_description,
            {'use_sim_time': True}
        ]
    )
    spawn_robot = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                name='spawn_six_dof_arm',
                output='screen',
                arguments=[
                    '-topic',
                    'robot_description',
                    '-name',
                    'six_dof_arm'
                ]
            )
        ]
    )
    # clock_bridge_and_controller_spawners
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='clock_bridge',
        output='screen',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ]
    )

    spawn_joint_state_broadcaster = TimerAction(
        period=6.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                name='spawner_joint_state_broadcaster',
                output='screen',
                arguments=[
                    'joint_state_broadcaster',
                    '--controller-manager',
                    '/controller_manager'
                ]
            )
        ]
    )

    spawn_arm_controller = TimerAction(
        period=8.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                name='spawner_arm_controller',
                output='screen',
                arguments=[
                    'arm_controller',
                    '--controller-manager',
                    '/controller_manager'
                ]
            )
        ]
    )

    return LaunchDescription([
        gazebo,
        clock_bridge,
        robot_state_publisher,
        spawn_robot,
        spawn_joint_state_broadcaster,
        spawn_arm_controller
    ])
