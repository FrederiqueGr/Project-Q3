import numpy as np

def number_of_fasteners(D, w, mat):
    """
    Calculates the maximal number of fasteners in one column based on the diameter, width, and material.
    """
    c = 2.5 if mat == "metal" else 4.5  # Safety factor
    return np.floor((w - 3 * D) / (c * D)) + 1


def cg_position(fasteners):
    """
    Calculates the center of gravity (CG) of the fasteners.
    Each fastener is represented as [[x, y, z], d], where d is the diameter.
    """
    positions = np.array([f[0] for f in fasteners])  # Extract positions [[x, y, z]]
    diameters = np.array([f[1] for f in fasteners])  # Extract diameters
    areas = np.pi * (diameters / 2) ** 2  # Area of each fastener
    total_area = areas.sum()
    cg = (positions.T @ areas) / total_area  # Weighted average
    return cg  # Return as [x, y, z]


def position_matrix(z_spacing, x_spacing, cols, c, D, H, n):
    """
    Generates a position matrix for the fasteners in 3D space.
    """
    z_spacing = max(z_spacing, c * D)
    x_spacing = max(x_spacing, c * D)

    length = (n - 1) * z_spacing
    z_coords = np.linspace(-length / 2, length / 2, n)

    x_start = -(H / 2 - 1.5 * D)
    x_coords = np.concatenate([
        np.linspace(x_start, x_start + (cols / 2 - 1) * x_spacing, cols // 2),
        np.linspace(-x_start - (cols / 2 - 1) * x_spacing, -x_start, cols // 2)
    ])
    
    z_grid = np.tile(z_coords, 2)  # Duplicate z-coordinates for both sides
    x_grid = np.concatenate([x_coords, x_coords[::-1]])  # Symmetry

    positions = np.column_stack((x_grid, np.zeros_like(x_grid), z_grid))  # [[x, y, z]]
    diameters = np.full(positions.shape[0], D)  # Set the same diameter for all fasteners

    return [[list(pos), d] for pos, d in zip(positions, diameters)]


def get_areas(fasteners):
    """
    Returns the cross-sectional areas of the fasteners.
    """
    diameters = np.array([f[1] for f in fasteners])  # Extract diameters
    return np.pi * (diameters / 2) ** 2


def get_vector_distances(fasteners):
    """
    Returns the vector distances of the fasteners from the origin.
    """
    return np.array([f[0] for f in fasteners])  # [[x, y, z]]


def get_scalar_distances(distances):
    """
    Returns the scalar distances (magnitudes) of vectors.
    """
    return np.linalg.norm(distances, axis=1)


def get_in_plane_forces_per_fastener(fasteners, F, r_force, M):
    """
    Calculates the force in each fastener to counteract in-plane forces and moments in 3D space.
    
    Parameters:
        fasteners: Array of fasteners, each in the form [[x, y, z], d].
        F: Applied force vector [Fx, Fy, Fz].
        r_force: Location vector of the applied force.
        M: Moment vector [Mx, My, Mz].
    
    Returns:
        Array of forces per fastener in the form [[Fx, Fy, Fz], ...].
    """
    fasteners_positions = np.array([f[0] for f in fasteners])
    areas = get_areas(fasteners)
    cg = cg_position(fasteners)

    rel_distances = fasteners_positions - cg
    scalar_distances = get_scalar_distances(rel_distances)

    # Reaction forces to counteract the applied force
    F_react_force_1 = (F * areas[:, None]) / areas.sum()

    # Moment due to the applied force
    r_force_rel_cg = np.array(r_force) - cg
    Moment = np.cross(r_force_rel_cg, F) + M  # Moment is now a 3D vector: Mx, My, Mz

    # Forces to counteract the moment
    print(np.cross(rel_distances, np.array([1, 0, 0])))
    F_react_force_M = (
        areas[:, None] 
        * np.cross(rel_distances, Moment)  # Cross product with the position relative to CG
    ) / (areas * scalar_distances**2).sum()
    return F_react_force_1 + F_react_force_M


# Example Usage
fasteners = [
    [[1, 0, 1], 2],
    [[-1, 0, -1], 1]
]

F = np.array([1000, 1000, 1000])  # Force vector in 3D [Fx, Fy, Fz]
r_force = [0, 0, 0]  # Applied force location
M = np.array([100,1000, 1000])  # Moment vector [Mx, My, Mz]

print(get_in_plane_forces_per_fastener(fasteners, F, r_force, M))
