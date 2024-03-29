import argparse
import h5py
import numpy as np
import matplotlib.pyplot as plt
from unyt import Msun, yr, Angstrom, g, s

from synthesizer.blackhole_emission_models import UnifiedAGN
from synthesizer.particle import BlackHoles
from synthesizer.particle import Gas
from synthesizer import galaxy

# Define the command line arguments
parser = argparse.ArgumentParser(
    description="Calculate the bolometric luminosity of the most "
    "massive black hole in the EAGLE simulation."
)
parser.add_argument(
    "--input-dir",
    type=str,
    help="The directory containing the EAGLE HDF5 files.",
    default="",
)

# Parse the args
args = parser.parse_args()
input_dir = args.input_dir

grid_dir = "."


# Get the particle ID of the most massive black hole at the last snapshot
hdf = h5py.File(f"{input_dir}/eagle_0763.hdf5", "r")
masses = hdf["PartType5"]["SubgridMasses"][:]
part_id = hdf["PartType5"]["ParticleIDs"][np.argmax(masses)]
print(hdf["PartType5"]["MetalMasses"].attrs["Description"])
hdf.close()

# Define lists for plotting
luminosities = []
acc_rates = []
redshifts = []

# Loop over snapshots
for i in range(0, 764):
    tag = str(i).zfill(4)

    # Read the snapshot data
    hdf = h5py.File(f"{input_dir}/eagle_{tag}.hdf5", "r")
    redshift = hdf["Header"].attrs["Redshift"]
    masses = hdf["PartType5"]["SubgridMasses"][:] * 10**10 * Msun
    coordinates = hdf["PartType5"]["Coordinates"][:]
    accretion_rates = hdf["PartType5"]["AccretionRates"][:]
    eddington = hdf["PartType5"]["EddingtonFractions"][:]
    metallicities = hdf["PartType5"]["BirthMetallicities"][:]
    part_ids = hdf["PartType5"]["ParticleIDs"][:]
    hdf.close()

    print(f"Snapshot {i}: Redshift {redshift}")

    if masses.shape[0] < 2:
        continue

    # Define the accretion rate conversion
    conv = (6.444 * 10**23 * g / s).to(Msun / yr)

    # Apply accreation units
    accretion_rates = accretion_rates * conv

    # Find the most massive black hole
    massive_bh = np.where(part_ids == part_id)[0]

    if len(massive_bh) == 0:
        continue

    # And get the black holes object
    bh = BlackHoles(
        masses=masses,
        coordinates=coordinates,
        accretion_rates=accretion_rates,
        metallicities=metallicities,
    )

    print(f"Most massive black hole: {bh.masses[massive_bh]}")

    bh.calculate_random_inclination()

    # Define the emission model
    emission_model = UnifiedAGN(
        disc_model="test_grid_agn", photoionisation_model="", grid_dir=grid_dir
    )

    # Generate the particle spectra
    spectra = bh.get_particle_spectra_intrinsic(
        emission_model, verbose=True, grid_assignment_method="cic"
    )["intrinsic"]

    # Get the boloemetric luminosity
    bol_lum = spectra.measure_bolometric_luminosity(method="trapz")
    print("Bolometric luminosity of MMBH:", bol_lum[massive_bh])

    # Append to the lists
    luminosities.append(bol_lum[massive_bh])
    redshifts.append(redshift)
    acc_rates.append(eddington[massive_bh])


fig, ax = plt.subplots()
ax.semilogy()
ax2 = ax.twinx()
ax2.semilogy()
ax.grid(True)

ax.plot(redshifts, luminosities, "k-", label="Bolometric Luminosity")
ax2.plot(redshifts, acc_rates, "r:", label="Accretion Rate")

ax.set_xlabel("$z$")
ax.set_ylabel(r"$L_\mathrm{bol}$ / [erg / s]")
ax2.set_ylabel(r"$\dot{M}_{edd}$")

ax.legend()

fig.savefig("bol_lum_time_series.png", dpi=100, bbox_inches="tight")
