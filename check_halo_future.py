import sys
import numpy as np
import h5py

from unyt import c, h, nJy, erg, s, Hz, pc, angstrom, eV, Msun, yr


# Define the path to the data
halo_path = "/cosma8/data/dp004/dc-brig2/L0400N3008_DMO_no4x/haloes/halo_%s"
snap_path = "/cosma8/data/dp004/dc-brig2/L0400N3008_DMO_no4x/snapshots/snapshot_%s.hdf5"

# Define snapshot information
proto_snap = "0005"
snap = "0015"

# How many halos should we test?
ntest = int(sys.argv[1])

# Open HDF5 files
proto_hdf = h5py.File(snap_path % proto_snap, "r")
hdf = h5py.File(snap_path % snap, "r")
proto_hdf = h5py.File(snap_path % proto_snap, "r")
hdf = h5py.File(snap_path % snap, "r")

# Get some metadata
print(proto_hdf["Header"].attrs.keys())
proto_z = proto_hdf["Header"].attrs["Redshift"]
z = hdf["Header"].attrs["Redshift"]
boxsize = hdf["Header"].attrs["BoxSize"]

# Load halo data
proto_data = h5py.File(halo_path % proto_snap + ".properties.0", "r")
halo_data = h5py.File(halo_path % snap + ".properties.0", "r")
proto_groups = h5py.File(halo_path % proto_snap + ".catalog_groups.0", "r")
halo_groups = h5py.File(halo_path % snap + ".catalog_groups.0", "r")
proto_parts = h5py.File(halo_path % proto_snap + ".catalog_particles.0", "r")
halo_parts = h5py.File(halo_path % snap + ".catalog_particles.0", "r")


print(halo_data.keys())
print(halo_groups.keys())
print(halo_parts.keys())

# Get the halo masses
proto_masses = proto_data["Mvir"]
masses = halo_data["Mvir"]

# Gets the indices of the most massive halos
proto_sinds = np.argsort(proto_masses)[::-1]
sinds = np.argsort(masses)[::-1]

print("Getting halo %d particles" % sinds[i])

# # Loop until we've tested all the halos we wanted to
# i = 0
# while i < ntest:

#     print("Getting halo %d particles" % sinds[i])

#     # Get this protocluster's particles
#     particles, unbound_particles = proto_groups.extract_halo(
#         halo_index=sinds[i])

#     # Get the mask into the SWIFT files
#     data, mask = to_swiftsimio_dataset(
#         particles,
#         snap_path % proto_snap,
#         generate_extra_mask=True
#     )

#     # Get particle IDs of the protocluser
#     print(dir(data))
#     print(dir(data.dark_matter))
    


#     i += 1

