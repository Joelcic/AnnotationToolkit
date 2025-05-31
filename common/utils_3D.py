import open3d as o3d
import imageio


def create_gif_from_3D(file_path, gif_output_path="pointcloud_rotation.gif",
                       start_angle=0, end_angle=360,
                       frame_step=4, point_size=0.5,
                       ping_pong=True):
    """
    Creates a rotating GIF of a 3D point cloud from a .pcd file using Open3D.
    Rotation goes from start_angle to end_angle, and optionally back (ping-pong).

    Parameters:
    - file_path: str or o3d.geometry.PointCloud, path to the .pcd file or a point cloud object
    - gif_output_path: str, output path for the GIF
    - start_angle: int, starting angle of rotation (degrees)
    - end_angle: int, ending angle of rotation (degrees)
    - frame_step: int, step in degrees between frames
    - point_size: float, Open3D point size for visualization
    - ping_pong: bool, if True, rotate back from end_angle to start_angle (ping-pong effect)
    """

    if isinstance(file_path, str):
        pcd = o3d.io.read_point_cloud(file_path)
        if not pcd.has_points():
            raise ValueError("Point cloud has no points. Check file format or content.")
    elif isinstance(file_path, o3d.geometry.PointCloud):
        pcd = file_path
    else:
        raise ValueError("Input variable 'file_path' must be a string path or an Open3D PointCloud.")

    # Apply optional orientation adjustment
    R_z = pcd.get_rotation_matrix_from_axis_angle([0, 0, np.pi / 2])
    R_y = pcd.get_rotation_matrix_from_axis_angle([0, np.pi, 0])
    R_x = pcd.get_rotation_matrix_from_axis_angle([np.deg2rad(10), 0, 0])
    R_y2 = pcd.get_rotation_matrix_from_axis_angle([0, -np.deg2rad(35), 0])
    pcd.rotate(R_z, center=(0, 0, 0))
    pcd.rotate(R_y, center=(0, 0, 0))
    pcd.rotate(R_x, center=(0, 0, 0))
    pcd.rotate(R_y2, center=(0, 0, 0))

    vis = o3d.visualization.Visualizer()
    vis.create_window(visible=False)
    vis.add_geometry(pcd)
    opt = vis.get_render_option()
    opt.point_size = point_size

    ctr = vis.get_view_control()
    # Rotate view to start_angle
    ctr.rotate(start_angle * 6, 0.0)

    images = []

    # Create forward angles list
    forward_angles = list(range(start_angle, end_angle + 1, frame_step))
    if ping_pong:
        # Create backward angles list (excluding the last frame to avoid duplication)
        backward_angles = list(range(end_angle - frame_step, start_angle - 1, -frame_step))
        angles = forward_angles + backward_angles
    else:
        angles = forward_angles

    for i in range(len(angles) - 1):
        angle_diff = angles[i + 1] - angles[i]
        ctr.rotate(angle_diff * 6, 0.0)  # rotate horizontally by difference * 6 pixels per degree
        vis.poll_events()
        vis.update_renderer()
        img = vis.capture_screen_float_buffer(False)
        img = (np.asarray(img)[:, :, :3] * 255).astype(np.uint8)
        images.append(img)

    vis.destroy_window()

    imageio.mimsave(gif_output_path, images, duration=120, loop=0)
    print(f"GIF saved to {gif_output_path}")