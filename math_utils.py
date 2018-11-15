import numpy as np
from scipy.stats import norm


def quaternion_multiply(q1, q2):
    """Multiplies two quaternions and returns the result

    Args:
        q1 (numpy ndarray): a right-handed quaternion (4x1) with the scalar part as the last entry
        q2 (numpy ndarray): a right-handed quaternion (4x1) with the scalar part as the last entry

    Returns:
        numpy ndarray: the quaternion product of the quaternion multiplication
    """

    q3 = np.empty((4, ))
    q3[0:3] = q1[3] * q2[0:3] + q2[3] * q1[0:3] - np.cross(q1[0:3], q2[0:3])
    q3[3] = q1[3] * q2[3] - np.dot(q1[0:3], q2[0:3])
    return q3


def quaternion_to_dcm(q):
    """Converts a quaternion to a Direction Cosine Matrix (DCM)

    Args:
        q (numpy ndarray): a right-handed quaternion (4x1) with the scalar part as the last entry

    Returns:
        numpy ndarray: the equivalent (3x3) Direction Cosine Matrix for the attitude parameterized by the input quaternion
    """

    q1, q2, q3, q4 = q
    dcm = np.array([[
        q1**2 - q2**2 - q3**2 + q4**2, 2 * (q1 * q2 + q3 * q4),
        2 * (q1 * q3 - q2 * q4)
    ], [
        2 * (q1 * q2 - q3 * q4), -q1**2 + q2**2 - q3**2 + q4**2,
        2 * (q2 * q3 + q1 * q4)
    ], [
        2 * (q1 * q3 + q2 * q4), 2 * (q2 * q3 - q1 * q4),
        -q1**2 - q2**2 + q3**2 + q4**2
    ]])
    return dcm


def dcm_to_quaternion(dcm):
    """Converts a Direction Cosine Matrix (DCM) to a quaternion
    
    Args:
        dcm (numpy ndarray): a 3x3 transformation matrix that parameterizes the attitude of a satellite
    
    Returns:
        numpy ndarray: the equivalent right-handed quaternion (4x1) with the scalar part as the last entry
    """

    K = np.array([[
        dcm[0, 0] - dcm[1, 1] - dcm[2, 2], dcm[1, 0] + dcm[0, 1],
        dcm[2, 0] + dcm[0, 2], dcm[1, 2] - dcm[2, 1]
    ], [
        dcm[1, 0] + dcm[0, 1], dcm[1, 1] - dcm[0, 0] - dcm[2, 2],
        dcm[2, 1] + dcm[1, 2], dcm[2, 0] - dcm[0, 2]
    ], [
        dcm[2, 0] + dcm[0, 2], dcm[2, 1] + dcm[1, 2],
        dcm[2, 2] - dcm[0, 0] - dcm[1, 1], dcm[0, 1] - dcm[1, 0]
    ], [
        dcm[1, 2] - dcm[2, 1], dcm[2, 0] - dcm[0, 2], dcm[0, 1] - dcm[1, 0],
        dcm[0, 0] + dcm[1, 1] + dcm[2, 2]
    ]]) * 1 / 3
    w, v = np.linalg.eig(K)
    i = np.argmax(w)
    return v[:, i]


def t1_matrix(angle):
    """Returns the transformation matrix of a rotation about the 1-axis for a given angle
    
    Args:
        angle (float): the angle of rotation about the axis (in radians)
    
    Returns:
        numpy ndarray: the transformation matrix for the rotation
    """
    return np.array([[1, 0, 0], [0, np.cos(angle), np.sin(angle)], [0, -np.sin(angle), np.cos(angle)]])


def t2_matrix(angle):
    """Returns the transformation matrix of a rotation about the 2-axis for a given angle
    
    Args:
        angle (float): the angle of rotation about the axis (in radians)
    
    Returns:
        numpy ndarray: the transformation matrix for the rotation
    """
    return np.array([[np.cos(angle), 0, -np.sin(angle)], [0, 1, 0], [np.sin(angle), 0, np.cos(angle)]])


def t3_matrix(angle):
    """Returns the transformation matrix of a rotation about the 3-axis for a given angle
    
    Args:
        angle (float): the angle of rotation about the axis (in radians)
    
    Returns:
        numpy ndarray: the transformation matrix for the rotation
    """
    return np.array([[np.cos(angle), np.sin(angle), 0], [-np.sin(angle), np.cos(angle), 0], [0, 0, 1]])


def normalize(vector):
    """Normalizes a vector so that its magnitude is 1
    
    Args:
        vector (numpy ndarray): an Nx1 vector of arbitrary magnitude
    
    Returns:
        numpy ndarray: the normalized vector
    """
    return vector / np.linalg.norm(vector)

# TODO: figure out what the stddev value should be for a given sensor/actuator
def apply_noise(value, stddev_frac=0.01):
    mean = value
    stddev = mean * stddev_frac
    distribution_func = norm(loc=value, scale=stddev)
    return distribution_func.rvs(size=1)