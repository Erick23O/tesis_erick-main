import numpy as np


path = "procesamiento de imagenes/calibrate_camera"

calib_data_path = "/calibration.npz"

calib_data = np.load(f"{path}{calib_data_path}")
# print(calib_data.files)
cam_mat = calib_data["mtx"]
dist_coef = calib_data["dist"]
r_vectors = calib_data["rvecs"]
t_vectors = calib_data["tvecs"]
errors = calib_data["mean_error"]
print(cam_mat)
print(dist_coef)
print(r_vectors)
print(t_vectors)
print(errors)
