import sys
import numpy as np

from swiftsimio import load as simload
from velociraptor import load
from velociraptor.swift.swift import to_swiftsimio_dataset
from velociraptor.particles import load_groups
from swiftgalaxy import SWIFTGalaxy, Velociraptor
from schwimmbad import MultiPool
from unyt import c, h, nJy, erg, s, Hz, pc, angstrom, eV, Msun, yr


# Define the path to the data
halo_path = "/cosma8/data/dp004/dc-brig2/L0400N3008_DMO_no4x/haloes/halo_%s"
snap_path = "/cosma8/data/dp004/dc-brig2/L0400N3008_DMO_no4x/snapshots/snapshot_%s.hdf5"

# Define snapshot information
proto_snap = "0005"
snap = "0015"

# How many halos should we test?
ntest = int(sys.argv[1])

# Load swiftsimio dataset to get volume and redshift
proto_sim_data = simload(snap_path % proto_snap)
proto_z = proto_sim_data.metadata.redshift
sim_data = simload(snap_path % snap)
z = sim_data.metadata.redshift
boxsize = sim_data.metadata.boxsize

# Load halos
proto_data = load(halo_path % proto_snap + ".properties.0")
proto_groups = load_groups(
    halo_path % snap + ".catalog_groups.0",
    catalogue=proto_data
)
halo_data = load(halo_path % proto_snap + ".properties.0")
groups = load_groups(
    halo_path % snap + ".catalog_groups.0",
    catalogue=halo_data
)

# Get the halo masses
print(dir(halo_data))
print(dir(halo_data.masses))
proto_data.masses.mass_dark_matter.convert_to_units("msun")
proto_masses = proto_data.masses.mass_dark_matter
halo_data.masses.mass_dark_matter.convert_to_units("msun")
masses = halo_data.masses.mass_dark_matter

# Gets the indices of the most massive halos
proto_sinds = np.argsort(proto_masses)[::-1]
sinds = np.argsort(masses)[::-1]

# Loop until we've tested all the halos we wanted to
i = 0
while i < ntest:

    # Get this protocluster's particles
    particles, unbound_particles = groups.extract_halo(halo_index=sinds[i])

    # Get the mask into the SWIFT files
    data, mask = to_swiftsimio_dataset(
        particles,
        snap_path % proto_snap,
        generate_extra_mask=True
    )

    # Get particle IDs of the protocluser
    print(dir(data))
    print(dir(data.dark_matter))
    


    i += 1

