from src.network_acquisition.station_source_factory import get_station_source
from src.pnt_engine.tdoa import estimate_position_tdoa
from src.pnt_engine.tdoa import tdoa_residuals

config = {
    "network_source": {
        "type": "mock",
        "station_coords": [[0, 0], [100, 0], [50, 100], [0, 100]]
    }
}

station_source = get_station_source(config)
station_coords, _ = station_source.get_measurements()

# Realistic test: simulate a target actually located near (30, 40),
# and compute what the time differences WOULD be from that true position,
# then check if estimate_position_tdoa can recover it.
import numpy as np
SPEED_OF_LIGHT = 299_792_458

true_position = np.array([30, 40])
station_coords_arr = np.array(station_coords)
ref_distance = np.linalg.norm(true_position - station_coords_arr[0])

true_time_diffs = []
for coord in station_coords_arr[1:]:
    distance = np.linalg.norm(true_position - coord)
    true_time_diffs.append((distance - ref_distance) / SPEED_OF_LIGHT)


# Diagnostic: check residuals AT the true position - should be ~0 if the math is correct
residuals_at_true = tdoa_residuals(np.array([30.0, 40.0]), station_coords_arr, true_time_diffs)
print("Residuals at TRUE position (should be ~0):", residuals_at_true)

estimated_position = estimate_position_tdoa(station_coords, true_time_diffs)

print(f"True position:      {true_position}")
print(f"Estimated position:  {estimated_position}")


error = np.linalg.norm(true_position - estimated_position)
print(f"Error: {error:.4f} meters")

assert error < 1.0, f"TDOA estimation error too large: {error}"
print("pnt_engine math verified: estimate_position_tdoa correctly recovers a known position")