from launch import LaunchDescription
from launch_ros.actions import SetParameter
from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_move_group_launch


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder(
        "six_dof_arm",
        package_name="six_dof_arm_moveit_config",
    ).to_moveit_configs()

    generated_launch = generate_move_group_launch(moveit_config)

    return LaunchDescription([
        SetParameter(name="use_sim_time", value=True),
        SetParameter(name="ompl.start_state_max_bounds_error", value=0.001),
        SetParameter(name="ompl.fix_start_state", value=True),
        *generated_launch.entities,
    ])
