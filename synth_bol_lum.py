import h5py
import numpy as np
import matplotlib.pyplot as plt
from unyt import Msun, yr, Angstrom

from synthesizer.blackhole_emission_models import UnifiedAGN
from synthesizer.particle import BlackHoles
from synthesizer.particle import Gas
from synthesizer import galaxy


# Get the particle ID of the most massive black hole at the last snapshot
hdf = h5py.File(f"eagle_{tag}.hdf5", "r")
masses = hdf["PartType5"]["SubgridMasses"][:]
part_id = hdf["PartType5"]["ParticleIDs"][np.argmax(masses)]
hdf.close()

# Define lists for plotting
luminosities = []
acc_rates = []
redshifts = []

# Loop over snapshots
for i in range(0, 764):
    tag = str(i).zfill(4)

    # Read the snapshot data
    hdf = h5py.File(f"eagle_{tag}.hdf5", "r")
    redshift = hdf["Header"].attrs["Redshift"]
    masses = hdf["PartType5"]["SubgridMasses"][:] * 10**10 * Msun
    coordinates = hdf["PartType5"]["Coordinates"][:]
    accretion_rates = hdf["PartType5"]["AccretionRates"][:]
    metallicities = hdf["PartType5"]["BirthMetallicities"][:]
    part_ids = hdf["PartType5"]["ParticleIDs"][:]
    hdf.close()

    print(f"Snapshot {i}: Redshift {redshift}")

    if masses.shape[0] == 0:
        continue

    # Find the most massive black hole
    massive_bh = np.where(part_ids == part_id)[0]

    if len(massive_bh) == 0:
        continue

    print(f"Most massive black hole: {bh.masses[massive_bh]} Msun")

    # And get the black holes object
    bh = BlackHoles(
        masses=masses,
        coordinates=coordinates,
        accretion_rates=accretion_rates,
        metallicities=metallicities,
    )

    bh.calculate_random_inclination()

    # Define the emission model
    grid_dir = (
        "/Users/willroper/Research/Synthesizer/synthesizer/tests/test_grid/"
    )
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
    acc_rates.append(accretion_rates[massive_bh])


fig, ax = plt.subplots()
ax2 = ax.twinx()

ax.plot(redshifts, luminosities, "k-")
ax2.plot(redshifts, acc_rates, "r-")

ax.set_xlabel("$z$")
ax.set_ylabel("$L_\mathrm{bol}$ / [erg / s]")
ax2.set_ylabel("$\dot{M}$ / [M$_\odot$ / yr]")

plt.show()
