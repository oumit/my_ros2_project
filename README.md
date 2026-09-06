[ros2_6dof_bastan_sona_temiz_kurulum_rehberi.md](https://github.com/user-attachments/files/31886107/ros2_6dof_bastan_sona_temiz_kurulum_rehberi.md)
# my_ros2_project# ROS 2 Jazzy ile 6-DOF Endüstriyel Robot Simülasyonu

## Baştan Sona Temiz Kurulum Rehberi

**Sistem:** Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic / Gazebo Sim 8  
**Workspace:** `~/ros2_jazzy_ws`  
**Paket:** `six_dof_arm_description`

Bu rehber; 6-DOF robot kolu, iki parmaklı gripper, Gazebo, `ros2_control`, controller'lar ve RViz görüntülemesini sıfırdan kurmak için izlenecek temiz akıştır. Komutlar sırayla çalıştırılmalıdır. Karşılaşılan hata çıktıları ve hata çözüm dalları özellikle dahil edilmemiştir.

## 1. ROS 2 ortamını doğrulama

ROS 2 Jazzy kurulumunu kontrol edin:

```bash
test -f /opt/ros/jazzy/setup.bash && echo "ROS 2 Jazzy hazır."
```

Her yeni terminalde ROS 2 ortamını etkinleştirin:

```bash
source /opt/ros/jazzy/setup.bash
echo "ROS_DISTRO=$ROS_DISTRO"
```

## 2. Workspace oluşturma

```bash
mkdir -p ~/ros2_jazzy_ws/src
ls -la ~/ros2_jazzy_ws
```

Bu komut eski projelere dokunmadan yeni workspace ve `src` klasörünü oluşturur.

## 3. Description paketini oluşturma

```bash
source /opt/ros/jazzy/setup.bash

ros2 pkg create --build-type ament_cmake \
  --destination-directory ~/ros2_jazzy_ws/src \
  six_dof_arm_description
```

Robot dosyaları için klasörleri oluşturun:

```bash
mkdir -p ~/ros2_jazzy_ws/src/six_dof_arm_description/{urdf,meshes,rviz,config,launch}
```

## 4. package.xml bağımlılıkları

```bash
nano ~/ros2_jazzy_ws/src/six_dof_arm_description/package.xml
```

Paket açıklaması, lisans ve aşağıdaki çalışma bağımlılıkları bulunmalıdır:

```xml
<description>6-DOF industrial robot arm description and simulation package</description>
<license>Apache-2.0</license>

<exec_depend>xacro</exec_depend>
<exec_depend>robot_state_publisher</exec_depend>
<exec_depend>joint_state_publisher_gui</exec_depend>
<exec_depend>rviz2</exec_depend>
<exec_depend>launch</exec_depend>
<exec_depend>launch_ros</exec_depend>
<exec_depend>ros_gz_sim</exec_depend>
<exec_depend>ros_gz_bridge</exec_depend>
<exec_depend>gz_ros2_control</exec_depend>
<exec_depend>controller_manager</exec_depend>
<exec_depend>joint_state_broadcaster</exec_depend>
<exec_depend>joint_trajectory_controller</exec_depend>
```

Kontrol:

```bash
grep -E "description|license|exec_depend" \
  ~/ros2_jazzy_ws/src/six_dof_arm_description/package.xml
```

## 5. CMakeLists.txt kurulum kuralı

```bash
nano ~/ros2_jazzy_ws/src/six_dof_arm_description/CMakeLists.txt
```

Şu kuralı ekleyin:

```cmake
install(
  DIRECTORY urdf meshes rviz config launch
  DESTINATION share/${PROJECT_NAME}
)
```

Bu kural kaynak klasörlerini paketin `install` alanına aktarır.

## 6. İlk derleme

```bash
cd ~/ros2_jazzy_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source ~/ros2_jazzy_ws/install/setup.bash
ros2 pkg prefix six_dof_arm_description
```

Her yeni terminalde proje paketlerini kullanmadan önce:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_jazzy_ws/install/setup.bash
```

## 7. Xacro robot modeli

```bash
nano ~/ros2_jazzy_ws/src/six_dof_arm_description/urdf/six_dof_arm.urdf.xacro
```

Modelde şu yapı bulunmalıdır:

- `base_link`
- `link_1`–`link_6`
- `joint_1`–`joint_6`: revolute
- `tool0` ve `tool0_fixed_joint`
- `gripper_base` ve `gripper_mount_joint`
- `gripper_left_finger` ve `gripper_right_finger`
- İki prismatic gripper joint'i
- Her fiziksel linkte `visual`, `collision` ve `inertial`
- Revolute ve prismatic joint'lerde `parent`, `child`, `origin`, `axis` ve `limit`

Temel Xacro çerçevesi:

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro"
       name="six_dof_arm">

  <!-- Link ve joint tanımları -->

</robot>
```

Her önemli düzenlemeden sonra doğrulayın:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_jazzy_ws/install/setup.bash

xacro ~/ros2_jazzy_ws/src/six_dof_arm_description/urdf/six_dof_arm.urdf.xacro \
  > /tmp/six_dof_arm_test.urdf
```

Link ve joint sayıları:

```bash
echo -n "Link sayısı: "
grep -c '<link name=' /tmp/six_dof_arm_test.urdf
echo -n "Joint sayısı: "
grep -c '<joint name=' /tmp/six_dof_arm_test.urdf
```

Gripper eklenmeden önce temel kol ve `tool0` 8 link, 7 joint; gripper eklendikten sonra 11 link, 10 joint içeriyordu. Daha sonra `world` ve `world_fixed_joint` eklenince sayılar birer artar.

## 8. İlk RViz modelleme testi

`display.launch.py`; Xacro'yu işler, `robot_state_publisher`, `joint_state_publisher_gui` ve RViz'i başlatır. Bu launch yalnızca Gazebo kullanılmayan modelleme aşamasında kullanılmalıdır.

```bash
nano ~/ros2_jazzy_ws/src/six_dof_arm_description/launch/display.launch.py

python3 -m py_compile \
  ~/ros2_jazzy_ws/src/six_dof_arm_description/launch/display.launch.py
```

Derleme ve RViz:

```bash
cd ~/ros2_jazzy_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select six_dof_arm_description
source ~/ros2_jazzy_ws/install/setup.bash
ros2 launch six_dof_arm_description display.launch.py
```

Modelleme aşamasında RViz `Fixed Frame` değeri `base_link` olabilir.

## 9. Gazebo ve kontrol paketlerini doğrulama

```bash
source /opt/ros/jazzy/setup.bash

ros2 pkg prefix ros_gz_sim
ros2 pkg prefix ros_gz_bridge
gz sim --version

ros2 pkg prefix ros2_control
ros2 pkg prefix controller_manager
ros2 pkg prefix ros2_controllers
ros2 pkg prefix gz_ros2_control
ros2 pkg prefix joint_state_broadcaster
ros2 pkg prefix joint_trajectory_controller
```

## 10. Gazebo öncesi fizik kontrolü ve yedek

```bash
MODEL=~/ros2_jazzy_ws/src/six_dof_arm_description/urdf/six_dof_arm.urdf.xacro

echo "inertial sayısı: $(grep -c '<inertial' "$MODEL")"
echo "collision sayısı: $(grep -c '<collision' "$MODEL")"
echo "gazebo etiketi: $(grep -c '<gazebo' "$MODEL")"
echo "ros2_control etiketi: $(grep -c '<ros2_control' "$MODEL")"
```

Yedek:

```bash
cp ~/ros2_jazzy_ws/src/six_dof_arm_description/urdf/six_dof_arm.urdf.xacro \
   ~/ros2_jazzy_ws/src/six_dof_arm_description/urdf/six_dof_arm.urdf.xacro.backup_before_gazebo
```

## 11. Gazebo model ayarları

İlk sahne yükleme testinde:

```xml
<gazebo>
  <static>true</static>
  <self_collide>false</self_collide>
</gazebo>
```

Kontrollü hareket aşamasında modeli dinamik yapıp tabanı dünyaya sabitleyin:

```xml
<gazebo>
  <static>false</static>
  <self_collide>false</self_collide>
</gazebo>

<link name="world"/>

<joint name="world_fixed_joint" type="fixed">
  <parent link="world"/>
  <child link="base_link"/>
  <origin xyz="0 0 0" rpy="0 0 0"/>
</joint>
```

Bu yapı robot tabanını sabit tutarken kol eklemlerinin dinamik hareketine izin verir.

## 12. Controller yapılandırması

`config/controllers.yaml`:

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100
    use_sim_time: true

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    arm_controller:
      type: joint_trajectory_controller/JointTrajectoryController

arm_controller:
  ros__parameters:
    joints:
      - joint_1
      - joint_2
      - joint_3
      - joint_4
      - joint_5
      - joint_6
    command_interfaces:
      - position
    state_interfaces:
      - position
      - velocity
    state_publish_rate: 50.0
    action_monitor_rate: 20.0
    allow_partial_joints_goal: false
```

## 13. Xacro ros2_control tanımı

Ana Xacro dosyasında `</robot>` öncesinde:

```xml
<ros2_control name="GazeboSystem" type="system">
  <hardware>
    <plugin>gz_ros2_control/GazeboSimSystem</plugin>
  </hardware>

  <joint name="joint_1">
    <command_interface name="position"/>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
  </joint>

  <!-- Aynı blok joint_2–joint_6 için tekrarlanır. -->
</ros2_control>

<gazebo>
  <plugin filename="gz_ros2_control-system"
          name="gz_ros2_control::GazeboSimROS2ControlPlugin">
    <parameters>$(find six_dof_arm_description)/config/controllers.yaml</parameters>
  </plugin>
</gazebo>
```

## 14. Birleşik Gazebo launch dosyası

`launch/gazebo.launch.py` şu işleri yapar:

- Gazebo `empty.sdf` dünyasını başlatır.
- `/clock` köprüsünü başlatır.
- `robot_state_publisher` çalıştırır.
- Robotu `/robot_description` üzerinden spawn eder.
- `joint_state_broadcaster` ve `arm_controller`ı otomatik başlatır.

```python
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
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')

    xacro_file = os.path.join(
        package_share, 'urdf', 'six_dof_arm.urdf.xacro'
    )
    gazebo_launch_file = os.path.join(
        ros_gz_sim_share, 'launch', 'gz_sim.launch.py'
    )

    robot_description = {
        'robot_description': Command(['xacro ', xacro_file])
    }

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch_file),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='clock_bridge',
        output='screen',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock']
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )

    spawn_robot = TimerAction(
        period=3.0,
        actions=[Node(
            package='ros_gz_sim',
            executable='create',
            name='spawn_six_dof_arm',
            output='screen',
            arguments=[
                '-topic', 'robot_description',
                '-name', 'six_dof_arm'
            ]
        )]
    )

    spawn_joint_state_broadcaster = TimerAction(
        period=6.0,
        actions=[Node(
            package='controller_manager',
            executable='spawner',
            name='spawner_joint_state_broadcaster',
            output='screen',
            arguments=[
                'joint_state_broadcaster',
                '--controller-manager', '/controller_manager'
            ]
        )]
    )

    spawn_arm_controller = TimerAction(
        period=8.0,
        actions=[Node(
            package='controller_manager',
            executable='spawner',
            name='spawner_arm_controller',
            output='screen',
            arguments=[
                'arm_controller',
                '--controller-manager', '/controller_manager'
            ]
        )]
    )

    return LaunchDescription([
        gazebo,
        clock_bridge,
        robot_state_publisher,
        spawn_robot,
        spawn_joint_state_broadcaster,
        spawn_arm_controller
    ])
```

Sözdizimi kontrolü:

```bash
python3 -m py_compile \
  ~/ros2_jazzy_ws/src/six_dof_arm_description/launch/gazebo.launch.py
```

## 15. Her değişiklikten sonra derleme

```bash
cd ~/ros2_jazzy_ws
source /opt/ros/jazzy/setup.bash

colcon build --symlink-install \
  --packages-select six_dof_arm_description

source ~/ros2_jazzy_ws/install/setup.bash
```

## 16. Gazebo ve controller'ları başlatma

Birinci terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_jazzy_ws/install/setup.bash

ros2 launch six_dof_arm_description gazebo.launch.py
```

Başka terminalden controller durumu:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_jazzy_ws/install/setup.bash

ros2 control list_controllers
ros2 topic echo /clock --once
ros2 topic echo /joint_states --once
```

## 17. RViz'i Gazebo ile görüntüleme

RViz yapılandırmasını kaydedin:

```text
~/ros2_jazzy_ws/src/six_dof_arm_description/rviz/six_dof_arm.rviz
```

Gazebo launch çalışırken ikinci terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_jazzy_ws/install/setup.bash

rviz2 -d ~/ros2_jazzy_ws/src/six_dof_arm_description/rviz/six_dof_arm.rviz
```

RViz ayarları:

- `Fixed Frame`: `world`
- RobotModel açıklama topic'i: `/robot_description`
- Gazebo kullanılırken `joint_state_publisher_gui` başlatılmaz.
- Gerçek eklem durumlarını `joint_state_broadcaster` yayınlar.

## 18. Güvenli hareket komutları

Yalnızca `joint_1`:

```bash
ros2 action send_goal \
  /arm_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  "{trajectory: {joint_names: [joint_1, joint_2, joint_3, joint_4, joint_5, joint_6], points: [{positions: [0.20, 0.0, 0.0, 0.0, 0.0, 0.0], time_from_start: {sec: 4, nanosec: 0}}]}}"
```

Altı eklemi küçük açılarda birlikte hareket ettirme:

```bash
ros2 action send_goal \
  /arm_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  "{trajectory: {joint_names: [joint_1, joint_2, joint_3, joint_4, joint_5, joint_6], points: [{positions: [0.15, -0.12, 0.10, 0.08, -0.10, 0.12], time_from_start: {sec: 5, nanosec: 0}}]}}"
```

Nötr pozisyona dönüş:

```bash
ros2 action send_goal \
  /arm_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  "{trajectory: {joint_names: [joint_1, joint_2, joint_3, joint_4, joint_5, joint_6], points: [{positions: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], time_from_start: {sec: 5, nanosec: 0}}]}}"
```

## 19. Projeyi kapatma

Önce RViz terminalinde, ardından Gazebo launch terminalinde `Ctrl+C` kullanın. Bu işlem dosyaları etkilemez; yalnızca çalışan ROS 2 süreçlerini kapatır.

## 20. Yeni proje kontrol listesi

- Ayrı workspace ve `src` klasörü oluştur.
- `ament_cmake` description paketi oluştur.
- `urdf`, `meshes`, `rviz`, `config` ve `launch` klasörlerini oluştur.
- `package.xml` bağımlılıklarını ekle.
- CMake kurulum kuralını ekle.
- Her linke `visual`, `collision` ve `inertial` tanımla.
- Her joint'e `parent`, `child`, `origin`, `axis` ve `limit` tanımla.
- Xacro'yu her aşamada geçici URDF'e dönüştür.
- Önce RViz ile kinematik modeli doğrula.
- Gazebo ve kontrol paketlerini doğrula.
- Tabanı `world_fixed_joint` ile sabitle.
- `ros2_control` joint arayüzlerini ekle.
- Controller YAML dosyasını oluştur.
- `gz_ros2_control` plugin'ini ekle.
- `/clock` köprüsünü başlat.
- Controller'ları otomatik spawn et.
- Gazebo ve RViz'i aynı `robot_description` ve `/joint_states` ile çalıştır.
- İlk hareketleri küçük açılar ve uzun sürelerle yap.
- Gripper joint'lerini ayrıca `ros2_control` ve gripper controller'a ekle.

## Mevcut projenin ulaştığı aşama

- 6-DOF kol Gazebo'da otomatik spawn oluyor.
- Robot tabanı `world` linkine sabit.
- Gazebo dinamik fizik kullanıyor.
- `gz_ros2_control` çalışıyor.
- `joint_state_broadcaster` otomatik aktif oluyor.
- `arm_controller` otomatik aktif oluyor.
- `/clock` ROS 2'ye aktarılıyor.
- Altı kol eklemi action komutuyla hareket ediyor.
- Hareket Gazebo ve RViz'de eş zamanlı görülüyor.
- Gripper geometrisi mevcut; gripper controller yapılandırması sıradaki adımdır.
# my_ros2_project
