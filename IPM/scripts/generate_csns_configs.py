#!/usr/bin/env python3
"""Write Virtual-IPM XML configs for the CSNS RCS IPM space-charge study."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "configs" / "csns_rcs_ipm"
BSCAN_OUT = OUT / "bscan"
BSCAN5_OUT = OUT / "bscan5"
SIG10_OUT = OUT / "sig10"
POWER_BSCAN_OUT = OUT / "bscan5_power"
IONSIZE_OUT = OUT / "ionsize"
EMODE_OUT = OUT / "emode"

# Parameters from NIMA 1092 (2026) 171809 and the cited CSNS RCS IPM papers.
# See configs/csns_rcs_ipm/PARAMETERS.md.
GAP_M = 231e-3
V_CAGE = 25e3
E_Y = V_CAGE / GAP_M  # ~108 kV/m; paper quotes ~110 kV/m
B_Y_DESIGN = 0.1  # PAC’09 cage design, 1000 G
N_PER_BUNCH_100KW = 1.56e13 / 2.0
GS_TO_T = 1.0e-4  # 1 G = 1e-4 T
B_SCAN_GS = (0, 50, 100, 200, 250)
B_SCAN5_GS = tuple(range(0, 251, 5))  # e-mode fine scan
POWERS_KW = (100, 200, 300, 400, 500)
SIZE_MM = tuple(range(3, 21))  # ion-mode and e-mode σ_x scan
ASPECT_YX = 0.8  # σ_y / σ_x (25:20 painted beam)
# E-mode replan. All blocks use ROUND beams (σ_y = σ_x); the earlier elliptical
# runs (25×20, 10×8) are therefore not reused here.
# Block A: full B grid 0–300 G / 5 G for the three reference beams at every
# power. Block B: σ_x = 3–20 mm size scan at checkpoint fields taken from the
# same grid, plus the 0.1 T design field.
EMODE_BSCAN_GS = tuple(range(0, 301, 5))
EMODE_SIZE_B_GS = (0, 100, 200, 300, 1000)
# (beam stage, σ in mm) reference beams for Block A: 25×25 inj., 10×10 ext., 10×10 inj.
EMODE_REF_BEAMS = (("injection", 25), ("extraction", 10), ("injection", 10))
# Block C: cage-voltage scan on the round 10×10 mm injection beam (25 kV included).
EMODE_VOLTAGES_KV = tuple(range(5, 31, 5))
EMODE_VOLT_B_GS = tuple(range(0, 301, 25)) + (1000,)
EMODE_CHECK_POWERS_KW = (100, 500)
# Block D: beam-offset check, (dx, dy) in mm; +y is away from the electron detector.
EMODE_OFFSETS_MM = ((5, 0), (10, 0), (0, 5), (0, -5))
EMODE_OFFSET_B_GS = (0, 100, 200, 300, 1000)
EMODE_OFFSET_BEAMS = (("injection", 10), ("extraction", 10))
# Fine C/D. Print with --emode-fine-cd-matrix; write with --emode-fine-cd.
# Do not mix into --emode-replan. 25 kV / 5 G is Block A (same physics as C
# at design voltage); Δy = 0 is Block A (centred 10×10 mm). Δx is not
# refined: coarse D showed translation invariance in x for a Gaussian bunch
# in a uniform cage.
EMODE_FINE_VOLTAGES_KV = tuple(range(5, 31, 1))
EMODE_FINE_DIAG_B_GS = (0, 25, 50, 75, 100, 125, 150, 200, 250, 300, 1000)
EMODE_FINE_VOLT_BFINE_KV = (10, 12, 15, 18, 20)
EMODE_FINE_B_GS = tuple(range(0, 301, 5)) + (1000,)
EMODE_FINE_DY_MM = tuple(range(-10, 11, 1))
EMODE_FINE_OFFSET_BFINE_DY = (-5, 5)
# Figure-dense add-on (Figs. 7b / 10b). 10 G fills voltages that never got a
# 5 G C2 scan; Δx = 1–10 mm at the 300 G operating point. 100 kW only.
EMODE_FINE_C3_VOLTAGES_KV = tuple(
    v for v in EMODE_FINE_VOLTAGES_KV if v not in EMODE_FINE_VOLT_BFINE_KV and v != 25
)
EMODE_FINE_C3_B_GS = tuple(range(0, 301, 10))
EMODE_FINE_DX_MM = tuple(range(1, 11, 1))
# Ion-mode 1 kV / 1 mm figure grid (Figs. 4, 9, 11). B = 0, 100 kW only.
# Existing Block C 5 kV and Block D 5 mm points are skipped at run time.
IMODE_FINE_VOLTAGES_KV = tuple(range(5, 31, 1))
IMODE_FINE_DY_MM = tuple(range(-5, 6, 1))
IMODE_FINE_DX_MM = tuple(range(0, 11, 1))
# Ion-mode parameter-scan matrix (parallel to e-mode A–D). Round beams;
# elliptical ionsize / bscan runs are not reused. No B-scan grid: only
# B ∈ {0, 200, 1000} G (no guide / mid checkpoint / design 0.1 T) in every
# block — closed ion scans are flat vs B. Species = H₂⁺, H₂O⁺, N₂⁺. SC-off
# is mass-independent without bunch fields → only H₂⁺ SC-off at 100 kW is
# written and shared.
IMODE_OUT = OUT / "imode"
# Single B set for every ion-mode block: no guide, mid checkpoint, design field.
# A dense / sparse B-scan is not useful — closed ion scans are flat vs B.
IMODE_B_GS = (0, 200, 1000)
IMODE_BSCAN_GS = IMODE_B_GS  # Block A
IMODE_SIZE_B_GS = IMODE_B_GS  # Block B
IMODE_REF_BEAMS = EMODE_REF_BEAMS  # 25×25 inj., 10×10 ext., 10×10 inj.
IMODE_VOLTAGES_KV = EMODE_VOLTAGES_KV  # Block C: 5–30 kV / 5 kV
IMODE_VOLT_B_GS = IMODE_B_GS
IMODE_OFFSETS_MM = EMODE_OFFSETS_MM
IMODE_OFFSET_B_GS = IMODE_B_GS
IMODE_OFFSET_BEAMS = EMODE_OFFSET_BEAMS
IMODE_CHECK_POWERS_KW = EMODE_CHECK_POWERS_KW
# Injection σ_x = 10 mm; σ_y = 8 mm keeps the 25:20 painted-beam aspect ratio.
INJ_SIG10_XY = "[ 10000, 8000 ]"

PROTON = "%(proton mass energy equivalent in MeV)"
H2_REST_ENERGY = f"2 * {PROTON}"
H2O_REST_ENERGY = f"18 * {PROTON}"
N2_REST_ENERGY = f"28 * {PROTON}"
# slug infix used in filenames: {beam}_{slug}_s{N}mm_p{P}kw
ION_SPECIES = (
    ("ions", H2_REST_ENERGY, "H₂⁺"),
    ("h2o_ions", H2O_REST_ENERGY, "H₂O⁺"),
    ("n2_ions", N2_REST_ENERGY, "N₂⁺"),
)

# Injection / extraction beam (NIMA Table 1 + IBIC notes). RF: 1.0241 → 2.444 MHz (h = 2).
BEAMS = {
    "injection": {
        "energy": "80",
        "energy_unit": "MeV",
        "sigma_t_ns": 120.0,
        "sigma_xy_um": "[ 25000, 20000 ]",
        "spacing_ns": 980.0,
        "offset_ns": -480.0,
        "e_sim_time": "1100",
        "e_sim_unit": "ns",
    },
    "extraction": {
        "energy": "1.6",
        "energy_unit": "GeV",
        "sigma_t_ns": 20.0,
        "sigma_xy_um": "[ 10000, 8000 ]",
        "spacing_ns": 409.2,  # 1 / 2.444 MHz
        "offset_ns": -204.6,
        "e_sim_time": "220",
        "e_sim_unit": "ns",
    },
}


def beam_xml(
    *,
    energy: str,
    energy_unit: str,
    sigma_t_ns: float,
    sigma_xy_um: str,
    n_bunch: float,
    e_off: bool,
    b_off: bool,
    train: str,
    offset_mm: tuple[float, float] | None = None,
) -> str:
    off_e = "true" if e_off else "false"
    off_b = "true" if b_off else "false"
    if offset_mm is not None and any(offset_mm):
        train += (
            f"\n                <TransverseOffset unit=\"mm\">"
            f"[ {offset_mm[0]:g}, {offset_mm[1]:g} ]</TransverseOffset>"
        )
    return f"""        <Beam>
            <Parameters>
                <Energy unit="{energy_unit}">{energy}</Energy>
                <BunchPopulation>{n_bunch:.3e}</BunchPopulation>
                <ParticleType>
                    <ChargeNumber>1</ChargeNumber>
                    <RestEnergy unit="MeV">%(proton mass energy equivalent in MeV)</RestEnergy>
                </ParticleType>
                <ElectricFieldOFF>{off_e}</ElectricFieldOFF>
                <MagneticFieldOFF>{off_b}</MagneticFieldOFF>
            </Parameters>
            <BunchShape>
                <Parameters>
                    <LongitudinalSigmaLabFrame unit="ns">{sigma_t_ns}</LongitudinalSigmaLabFrame>
                    <TransverseSigma unit="um">{sigma_xy_um}</TransverseSigma>
                </Parameters>
                <Model>Gaussian</Model>
            </BunchShape>
            <BunchElectricField>
                <Model>Gaussian</Model>
            </BunchElectricField>
            <BunchTrain>
{train}
            </BunchTrain>
        </Beam>"""


def single_bunch_train() -> str:
    return "                <Type>SingleBunch</Type>"


def circular_train(n_bunches: int, spacing_ns: float, offset_ns: float) -> str:
    return f"""                <NumberOfBunches>{n_bunches}</NumberOfBunches>
                <BunchSpacing unit="ns">{spacing_ns}</BunchSpacing>
                <LongitudinalOffset unit="ns">{offset_ns}</LongitudinalOffset>
                <Type>CircularBunchTrain</Type>"""


def _fmt_b(b_y: float) -> str:
    if abs(b_y) < 1e-18:
        return "0"
    return f"{b_y:.8g}"


def device_and_fields(*, e_y: float, b_y: float) -> str:
    half_x = 220e-3 / 2 * 1e3  # mm
    half_y = GAP_M / 2 * 1e3
    return f"""    <Device>
        <Parameters>
            <XBoundaries unit="mm">[ -{half_x:g}, {half_x:g} ]</XBoundaries>
            <YBoundaries unit="mm">[ -{half_y:g}, {half_y:g} ]</YBoundaries>
        </Parameters>
        <Model>InterpolatingIPM</Model>
    </Device>
    <GuidingFields>
        <Electric>
            <Parameters>
                <ElectricField unit="V/m">[ 0, {e_y:.6e}, 0 ]</ElectricField>
            </Parameters>
            <Model>UniformElectricField</Model>
        </Electric>
        <Magnetic>
            <Parameters>
                <MagneticField unit="T">[ 0, {_fmt_b(b_y)}, 0 ]</MagneticField>
            </Parameters>
            <Model>UniformMagneticField</Model>
        </Magnetic>
    </GuidingFields>"""


def electron_generation() -> str:
    return """    <ParticleGeneration>
        <Parameters>
            <ZPosition unit="m">0</ZPosition>
            <Ionization>
                <Parameters>
                    <GasType>Hydrogen</GasType>
                    <ScatteringAngleBins>120</ScatteringAngleBins>
                    <ScatteringAngleBoundaries unit="rad">[ 0.0, %(pi) ]</ScatteringAngleBoundaries>
                    <EnergyBoundaries unit="eV">[ 0.001, 300.0 ]</EnergyBoundaries>
                    <EnergyBins>400</EnergyBins>
                </Parameters>
            </Ionization>
        </Parameters>
        <Model>VoitkivDDCS</Model>
    </ParticleGeneration>
    <ParticleTracking>
        <Model>Boris</Model>
    </ParticleTracking>"""


def ion_generation() -> str:
    return """    <ParticleGeneration>
        <Parameters>
            <BeamId>0</BeamId>
            <ZPosition unit="m">0</ZPosition>
        </Parameters>
        <Model>ZeroMomentum</Model>
    </ParticleGeneration>
    <ParticleTracking>
        <Model>Boris</Model>
    </ParticleTracking>"""


def simulation(
    *,
    n_particles: int,
    sim_time: str,
    sim_unit: str,
    n_steps: int,
    charge: int,
    rest_energy: str,
    filename: str,
) -> str:
    return f"""    <Simulation>
        <RNGSeed>1234</RNGSeed>
        <NumberOfParticles>{n_particles}</NumberOfParticles>
        <TimeRange>
            <SimulationTime unit="{sim_unit}">{sim_time}</SimulationTime>
            <NumberOfTimeSteps>{n_steps}</NumberOfTimeSteps>
        </TimeRange>
        <ParticleType>
            <ChargeNumber>{charge}</ChargeNumber>
            <RestEnergy unit="MeV">{rest_energy}</RestEnergy>
        </ParticleType>
        <Output>
            <Parameters>
                <Filename>{filename}</Filename>
            </Parameters>
            <Recorder>BasicRecorder</Recorder>
        </Output>
    </Simulation>"""


def wrap(body: str) -> str:
    return '<?xml version="1.0" ?>\n<Virtual-IPM>\n' + body + "\n</Virtual-IPM>\n"


def write(path: Path, xml: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(xml)
    print(f"wrote {path}")


def _stem(name: str, sc_on: bool, b_tag: str | None) -> str:
    tag = "sc_on" if sc_on else "sc_off"
    if b_tag:
        return f"{name}_{b_tag}_{tag}"
    return f"{name}_{tag}"


def electron_case(
    name: str,
    *,
    energy: str,
    energy_unit: str,
    sigma_t_ns: float,
    sigma_xy_um: str,
    sim_time: str,
    sim_unit: str,
    n_steps: int,
    sc_on: bool,
    n_particles: int = 100000,
    b_y: float = B_Y_DESIGN,
    b_tag: str | None = None,
    config_dir: Path = OUT,
    csv_dir: str = "output",
    n_bunch: float | None = None,
    e_y: float = E_Y,
    offset_mm: tuple[float, float] | None = None,
) -> Path:
    stem = _stem(name, sc_on, b_tag)
    csv = f"{csv_dir}/csns_{stem}.csv"
    beam = beam_xml(
        energy=energy,
        energy_unit=energy_unit,
        sigma_t_ns=sigma_t_ns,
        sigma_xy_um=sigma_xy_um,
        n_bunch=N_PER_BUNCH_100KW if n_bunch is None else n_bunch,
        e_off=not sc_on,
        b_off=not sc_on,
        train=single_bunch_train(),
        offset_mm=offset_mm,
    )
    xml = wrap(
        "    <Beams>\n"
        + beam
        + "\n    </Beams>\n"
        + device_and_fields(e_y=e_y, b_y=b_y)
        + "\n"
        + electron_generation()
        + "\n"
        + simulation(
            n_particles=n_particles,
            sim_time=sim_time,
            sim_unit=sim_unit,
            n_steps=n_steps,
            charge=-1,
            rest_energy="%(electron mass energy equivalent in MeV)",
            filename=csv,
        )
    )
    path = config_dir / f"{stem}.xml"
    write(path, xml)
    return path


def ion_case(
    slug: str,
    *,
    rest_energy: str,
    sc_on: bool,
    beam_key: str,
    n_particles: int = 100000,
    b_y: float = B_Y_DESIGN,
    b_tag: str | None = None,
    config_dir: Path = OUT,
    csv_dir: str = "output",
    sigma_xy_um: str | None = None,
    n_bunch: float | None = None,
    e_y: float | None = None,
    offset_mm: tuple[float, float] | None = None,
) -> Path:
    spec = BEAMS[beam_key]
    sigma = sigma_xy_um if sigma_xy_um is not None else spec["sigma_xy_um"]
    pop = N_PER_BUNCH_100KW if n_bunch is None else n_bunch
    # Ions are collected at the lower y-boundary, so E_y is reversed vs electron mode.
    cage_e_y = -E_Y if e_y is None else e_y
    stem = _stem(slug, sc_on, b_tag)
    csv = f"{csv_dir}/csns_{stem}.csv"
    # Generation-only bunch (fields off) so ions are created from a single passage.
    gen = beam_xml(
        energy=spec["energy"],
        energy_unit=spec["energy_unit"],
        sigma_t_ns=spec["sigma_t_ns"],
        sigma_xy_um=sigma,
        n_bunch=pop,
        e_off=True,
        b_off=True,
        train=single_bunch_train(),
        offset_mm=offset_mm,
    )
    # Tracking bunch train: ions see several subsequent bunches.
    track = beam_xml(
        energy=spec["energy"],
        energy_unit=spec["energy_unit"],
        sigma_t_ns=spec["sigma_t_ns"],
        sigma_xy_um=sigma,
        n_bunch=pop,
        e_off=not sc_on,
        b_off=not sc_on,
        train=circular_train(3, spec["spacing_ns"], spec["offset_ns"]),
        offset_mm=offset_mm,
    )
    xml = wrap(
        "    <Beams>\n"
        + gen
        + "\n"
        + track
        + "\n    </Beams>\n"
        + device_and_fields(e_y=cage_e_y, b_y=b_y)
        + "\n"
        + ion_generation()
        + "\n"
        + simulation(
            n_particles=n_particles,
            sim_time="12",
            sim_unit="us",
            n_steps=8000,
            charge=1,
            rest_energy=rest_energy,
            filename=csv,
        )
    )
    path = config_dir / f"{stem}.xml"
    write(path, xml)
    return path


def ion_injection_case(
    *,
    slug: str,
    rest_energy: str,
    sc_on: bool,
    n_particles: int = 100000,
) -> Path:
    return ion_case(
        slug,
        rest_energy=rest_energy,
        sc_on=sc_on,
        beam_key="injection",
        n_particles=n_particles,
        b_y=B_Y_DESIGN,
    )


def write_design_b_configs() -> None:
    """Original 0.1 T residual-gas study (H₂, H₂O, N₂ ions + electrons)."""
    OUT.mkdir(parents=True, exist_ok=True)
    for beam_key, slug in (
        ("injection", "injection_electrons"),
        ("extraction", "extraction_electrons"),
    ):
        spec = BEAMS[beam_key]
        for sc_on in (True, False):
            electron_case(
                slug,
                energy=spec["energy"],
                energy_unit=spec["energy_unit"],
                sigma_t_ns=spec["sigma_t_ns"],
                sigma_xy_um=spec["sigma_xy_um"],
                sim_time=spec["e_sim_time"],
                sim_unit=spec["e_sim_unit"],
                n_steps=8000,
                sc_on=sc_on,
                b_y=B_Y_DESIGN,
            )
    for sc_on in (True, False):
        ion_injection_case(
            slug="injection_ions",
            rest_energy=H2_REST_ENERGY,
            sc_on=sc_on,
        )
        ion_injection_case(
            slug="injection_h2o_ions",
            rest_energy=f"18 * {PROTON}",
            sc_on=sc_on,
        )
        ion_injection_case(
            slug="injection_n2_ions",
            rest_energy=f"28 * {PROTON}",
            sc_on=sc_on,
        )


def b_tag(b_gs: int) -> str:
    return f"b{b_gs}G"


def n_bunch_at_power(power_kw: float) -> float:
    return N_PER_BUNCH_100KW * (power_kw / 100.0)


def sigma_xy_um(sigma_x_mm: float) -> str:
    """Elliptical beam (ion-mode legacy scans): σ_y = 0.8 σ_x."""
    sx = sigma_x_mm * 1e3
    sy = sigma_x_mm * ASPECT_YX * 1e3
    return f"[ {sx:.0f}, {sy:.0f} ]"


def round_sigma_xy_um(sigma_mm: float) -> str:
    """Round beam (e-mode replan): σ_y = σ_x."""
    s = sigma_mm * 1e3
    return f"[ {s:.0f}, {s:.0f} ]"


def write_bscan_configs() -> list[Path]:
    """B-field scan: 0, 50, 100, 200 G; injection/extraction; e-mode and H₂⁺ ion-mode."""
    BSCAN_OUT.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for b_gs in B_SCAN_GS:
        b_y = b_gs * GS_TO_T
        tag = b_tag(b_gs)
        for beam_key in ("injection", "extraction"):
            spec = BEAMS[beam_key]
            for sc_on in (True, False):
                paths.append(
                    electron_case(
                        f"{beam_key}_electrons",
                        energy=spec["energy"],
                        energy_unit=spec["energy_unit"],
                        sigma_t_ns=spec["sigma_t_ns"],
                        sigma_xy_um=spec["sigma_xy_um"],
                        sim_time=spec["e_sim_time"],
                        sim_unit=spec["e_sim_unit"],
                        n_steps=8000,
                        sc_on=sc_on,
                        b_y=b_y,
                        b_tag=tag,
                        config_dir=BSCAN_OUT,
                        csv_dir="output/bscan",
                    )
                )
                paths.append(
                    ion_case(
                        f"{beam_key}_ions",
                        rest_energy=H2_REST_ENERGY,
                        sc_on=sc_on,
                        beam_key=beam_key,
                        b_y=b_y,
                        b_tag=tag,
                        config_dir=BSCAN_OUT,
                        csv_dir="output/bscan",
                    )
                )
    return paths


def _electron_from_beam(
    slug: str,
    beam_key: str,
    *,
    sc_on: bool,
    b_y: float,
    b_tag: str | None,
    config_dir: Path,
    csv_dir: str,
    sigma_xy_um: str | None = None,
    n_bunch: float | None = None,
    e_y: float = E_Y,
    offset_mm: tuple[float, float] | None = None,
    n_particles: int = 100000,
) -> Path:
    spec = BEAMS[beam_key]
    return electron_case(
        slug,
        energy=spec["energy"],
        energy_unit=spec["energy_unit"],
        sigma_t_ns=spec["sigma_t_ns"],
        sigma_xy_um=sigma_xy_um if sigma_xy_um is not None else spec["sigma_xy_um"],
        sim_time=spec["e_sim_time"],
        sim_unit=spec["e_sim_unit"],
        n_steps=8000,
        sc_on=sc_on,
        b_y=b_y,
        b_tag=b_tag,
        config_dir=config_dir,
        csv_dir=csv_dir,
        n_bunch=n_bunch,
        e_y=e_y,
        offset_mm=offset_mm,
        n_particles=n_particles,
    )


def write_sig10_design_configs() -> list[Path]:
    """0.1 T residual-gas study with injection σ_x = 10 mm (σ_y = 8 mm)."""
    SIG10_OUT.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for sc_on in (True, False):
        paths.append(
            _electron_from_beam(
                "injection_electrons_sig10",
                "injection",
                sc_on=sc_on,
                b_y=B_Y_DESIGN,
                b_tag=None,
                config_dir=SIG10_OUT,
                csv_dir="output",
                sigma_xy_um=INJ_SIG10_XY,
            )
        )
        for slug, rest in (
            ("injection_ions_sig10", H2_REST_ENERGY),
            ("injection_h2o_ions_sig10", f"18 * {PROTON}"),
            ("injection_n2_ions_sig10", f"28 * {PROTON}"),
        ):
            paths.append(
                ion_case(
                    slug,
                    rest_energy=rest,
                    sc_on=sc_on,
                    beam_key="injection",
                    b_y=B_Y_DESIGN,
                    config_dir=SIG10_OUT,
                    csv_dir="output",
                    sigma_xy_um=INJ_SIG10_XY,
                )
            )
    return paths


def write_fine_emode_bscan() -> list[Path]:
    """E-mode B scan: 0–250 G step 5 G; painted and 10 mm injection; extraction."""
    BSCAN5_OUT.mkdir(parents=True, exist_ok=True)
    families = (
        ("injection", "injection_electrons", None),
        ("extraction", "extraction_electrons", None),
        ("injection", "injection_electrons_sig10", INJ_SIG10_XY),
    )
    paths: list[Path] = []
    for b_gs in B_SCAN5_GS:
        tag = b_tag(b_gs)
        b_y = b_gs * GS_TO_T
        for beam_key, slug, sigma in families:
            for sc_on in (True, False):
                paths.append(
                    _electron_from_beam(
                        slug,
                        beam_key,
                        sc_on=sc_on,
                        b_y=b_y,
                        b_tag=tag,
                        config_dir=BSCAN5_OUT,
                        csv_dir="output/bscan5",
                        sigma_xy_um=sigma,
                    )
                )
    return paths


def write_emode_power_bscan() -> list[Path]:
    """E-mode 0–250 G / 5 G at 200–500 kW (SC on). SC-off reused from 100 kW."""
    POWER_BSCAN_OUT.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for power_kw in POWERS_KW:
        if power_kw == 100:
            continue
        pop = n_bunch_at_power(power_kw)
        for b_gs in B_SCAN5_GS:
            tag = b_tag(b_gs)
            b_y = b_gs * GS_TO_T
            for beam_key in ("injection", "extraction"):
                paths.append(
                    _electron_from_beam(
                        f"{beam_key}_electrons_p{power_kw}kW",
                        beam_key,
                        sc_on=True,
                        b_y=b_y,
                        b_tag=tag,
                        config_dir=POWER_BSCAN_OUT,
                        csv_dir="output/bscan5_power",
                        n_bunch=pop,
                    )
                )
    return paths


def write_ion_size_scan() -> list[Path]:
    """Ion-mode H₂⁺/H₂O⁺/N₂⁺: σ_x = 3–20 mm, injection and extraction, 100–500 kW."""
    IONSIZE_OUT.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for slug, rest, _label in ION_SPECIES:
        for sigma_mm in SIZE_MM:
            xy = sigma_xy_um(sigma_mm)
            for beam_key in ("injection", "extraction"):
                for power_kw in POWERS_KW:
                    pop = n_bunch_at_power(power_kw)
                    # SC-off is mass-independent (no bunch field); only H₂⁺ needs it.
                    if slug == "ions":
                        sc_flags = (True, False) if power_kw == 100 else (True,)
                    else:
                        sc_flags = (True,)
                    for sc_on in sc_flags:
                        paths.append(
                            ion_case(
                                f"{beam_key}_{slug}_s{sigma_mm}mm_p{power_kw}kw",
                                rest_energy=rest,
                                sc_on=sc_on,
                                beam_key=beam_key,
                                b_y=B_Y_DESIGN,
                                config_dir=IONSIZE_OUT,
                                csv_dir="output/ionsize",
                                sigma_xy_um=xy,
                                n_bunch=pop,
                            )
                        )
    return paths


def emode_slug(beam_key: str, sigma_mm: int, power_kw: int) -> str:
    return f"{beam_key}_electrons_s{sigma_mm}x{sigma_mm}mm_p{power_kw}kw"


def emode_csv_name(
    beam_key: str, sigma_mm: int, power_kw: int, b_gs: int, sc_on: bool
) -> str:
    tag = "sc_on" if sc_on else "sc_off"
    return f"csns_{emode_slug(beam_key, sigma_mm, power_kw)}_{b_tag(b_gs)}_{tag}.csv"


EmodePoint = tuple[str, int, int, int, bool]  # (beam, σ_x mm, power kW, B G, SC on)


def emode_points() -> list[EmodePoint]:
    """Every (beam, σ_x, P, B, SC) point of the replanned e-mode matrix, deduplicated.

    SC-off trajectories do not depend on bunch population, so SC-off runs exist
    only at 100 kW and are shared by the other powers.
    """
    pts: dict[EmodePoint, None] = {}

    def add(beam: str, sigma_mm: int, b_gs: int) -> None:
        for power_kw in POWERS_KW:
            pts[(beam, sigma_mm, power_kw, b_gs, True)] = None
        pts[(beam, sigma_mm, 100, b_gs, False)] = None

    # Block A: full 0–300 G / 5 G grid for the three reference beams.
    for beam, sigma_mm in EMODE_REF_BEAMS:
        for b_gs in EMODE_BSCAN_GS:
            add(beam, sigma_mm, b_gs)
    # Block B: σ_x = 3–20 mm at checkpoint fields (and 0.1 T), both stages.
    for sigma_mm in SIZE_MM:
        for b_gs in EMODE_SIZE_B_GS:
            for beam in ("injection", "extraction"):
                add(beam, sigma_mm, b_gs)
    return list(pts)


VoltPoint = tuple[int, int, int, bool]  # (V kV, power kW, B G, SC on)
OffsetPoint = tuple[str, int, int, int, int, bool]  # (beam, dx, dy, power kW, B G, SC on)


def emode_voltage_points() -> list[VoltPoint]:
    """Block C: cage voltage × B × {100, 500 kW} on the 10 mm injection beam."""
    pts: list[VoltPoint] = []
    for v_kv in EMODE_VOLTAGES_KV:
        for b_gs in EMODE_VOLT_B_GS:
            for power_kw in EMODE_CHECK_POWERS_KW:
                pts.append((v_kv, power_kw, b_gs, True))
            pts.append((v_kv, 100, b_gs, False))
    return pts


def emode_offset_points() -> list[OffsetPoint]:
    """Block D: transverse beam offset × B × {100, 500 kW}, 10 mm inj. and ext."""
    pts: list[OffsetPoint] = []
    for beam, _sigma in EMODE_OFFSET_BEAMS:
        for dx, dy in EMODE_OFFSETS_MM:
            for b_gs in EMODE_OFFSET_B_GS:
                for power_kw in EMODE_CHECK_POWERS_KW:
                    pts.append((beam, dx, dy, power_kw, b_gs, True))
                pts.append((beam, dx, dy, 100, b_gs, False))
    return pts


def _sc_power_pts() -> list[tuple[int, bool]]:
    """SC on at 100 and 500 kW; SC off once at 100 kW."""
    return [(p, True) for p in EMODE_CHECK_POWERS_KW] + [(100, False)]


def emode_fine_c1_voltage_points() -> list[VoltPoint]:
    """C1: 1 kV voltage grid at diagnostic B (inj. 10×10 mm)."""
    pts: list[VoltPoint] = []
    for v_kv in EMODE_FINE_VOLTAGES_KV:
        for b_gs in EMODE_FINE_DIAG_B_GS:
            for power_kw, sc_on in _sc_power_pts():
                pts.append((v_kv, power_kw, b_gs, sc_on))
    return pts


def emode_fine_c2_voltage_points() -> list[VoltPoint]:
    """C2: 5 G B-scan at voltages that straddle the B=0 sign-flip / oscillation."""
    pts: list[VoltPoint] = []
    for v_kv in EMODE_FINE_VOLT_BFINE_KV:
        for b_gs in EMODE_FINE_B_GS:
            for power_kw, sc_on in _sc_power_pts():
                pts.append((v_kv, power_kw, b_gs, sc_on))
    return pts


def emode_fine_c3_voltage_points() -> list[VoltPoint]:
    """C3: 10 G B-scan at 1 kV voltages that lack a 5 G C2/Block-A scan.

    Diagnostic-B files from C1 already exist at 100 k particles and are
    omitted so those CSVs are never rewritten.
    """
    keep_b = set(EMODE_FINE_DIAG_B_GS)
    pts: list[VoltPoint] = []
    for v_kv in EMODE_FINE_C3_VOLTAGES_KV:
        for b_gs in EMODE_FINE_C3_B_GS:
            if b_gs in keep_b:
                continue
            pts.append((v_kv, 100, b_gs, True))
            pts.append((v_kv, 100, b_gs, False))
    return pts


def emode_fine_voltage_points() -> list[VoltPoint]:
    """Union of C1, C2 and C3, first-seen order. 25 kV / 5 G stays Block A."""
    seen: dict[VoltPoint, None] = {}
    for pt in (
        emode_fine_c1_voltage_points()
        + emode_fine_c2_voltage_points()
        + emode_fine_c3_voltage_points()
    ):
        seen.setdefault(pt, None)
    return list(seen)


def emode_fine_d1_offset_points() -> list[OffsetPoint]:
    """D1: 1 mm Δy scan at diagnostic B. Δy=0 is Block A, not emitted."""
    pts: list[OffsetPoint] = []
    for beam, _sigma in EMODE_OFFSET_BEAMS:
        for dy in EMODE_FINE_DY_MM:
            if dy == 0:
                continue
            for b_gs in EMODE_FINE_DIAG_B_GS:
                for power_kw, sc_on in _sc_power_pts():
                    pts.append((beam, 0, dy, power_kw, b_gs, sc_on))
    return pts


def emode_fine_d2_offset_points() -> list[OffsetPoint]:
    """D2: 5 G B-scan at Δy = ±5 mm (the offsets that already differed)."""
    pts: list[OffsetPoint] = []
    for beam, _sigma in EMODE_OFFSET_BEAMS:
        for dy in EMODE_FINE_OFFSET_BFINE_DY:
            for b_gs in EMODE_FINE_B_GS:
                for power_kw, sc_on in _sc_power_pts():
                    pts.append((beam, 0, dy, power_kw, b_gs, sc_on))
    return pts


def emode_fine_d3_offset_points() -> list[OffsetPoint]:
    """D3: 1 mm Δx scan at 300 G, 100 kW, both 10 mm beams (Fig. 10b)."""
    pts: list[OffsetPoint] = []
    for beam, _sigma in EMODE_OFFSET_BEAMS:
        for dx in EMODE_FINE_DX_MM:
            pts.append((beam, dx, 0, 100, 300, True))
            pts.append((beam, dx, 0, 100, 300, False))
    return pts


def emode_fine_offset_points() -> list[OffsetPoint]:
    """Union of D1, D2 and D3."""
    seen: dict[OffsetPoint, None] = {}
    for pt in (
        emode_fine_d1_offset_points()
        + emode_fine_d2_offset_points()
        + emode_fine_d3_offset_points()
    ):
        seen.setdefault(pt, None)
    return list(seen)


def volt_slug(v_kv: int, power_kw: int) -> str:
    return f"injection_electrons_s10x10mm_v{v_kv}kv_p{power_kw}kw"


def volt_csv_name(v_kv: int, power_kw: int, b_gs: int, sc_on: bool) -> str:
    tag = "sc_on" if sc_on else "sc_off"
    return f"csns_{volt_slug(v_kv, power_kw)}_{b_tag(b_gs)}_{tag}.csv"


def _signed(v: int) -> str:
    return f"m{-v}" if v < 0 else f"{v}"


def offset_slug(beam: str, dx: int, dy: int, power_kw: int) -> str:
    return f"{beam}_electrons_s10x10mm_dx{_signed(dx)}mm_dy{_signed(dy)}mm_p{power_kw}kw"


def offset_csv_name(beam: str, dx: int, dy: int, power_kw: int, b_gs: int, sc_on: bool) -> str:
    tag = "sc_on" if sc_on else "sc_off"
    return f"csns_{offset_slug(beam, dx, dy, power_kw)}_{b_tag(b_gs)}_{tag}.csv"


def volt_xml_path(v_kv: int, power_kw: int, b_gs: int, sc_on: bool) -> Path:
    return EMODE_OUT / f"{_stem(volt_slug(v_kv, power_kw), sc_on, b_tag(b_gs))}.xml"


def offset_xml_path(
    beam: str, dx: int, dy: int, power_kw: int, b_gs: int, sc_on: bool
) -> Path:
    return EMODE_OUT / f"{_stem(offset_slug(beam, dx, dy, power_kw), sc_on, b_tag(b_gs))}.xml"


def write_emode_replan() -> list[Path]:
    """Write the replanned e-mode matrix (Blocks A–D)."""
    EMODE_OUT.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for beam, sigma_mm, power_kw, b_gs, sc_on in emode_points():
        paths.append(
            _electron_from_beam(
                emode_slug(beam, sigma_mm, power_kw),
                beam,
                sc_on=sc_on,
                b_y=b_gs * GS_TO_T,
                b_tag=b_tag(b_gs),
                config_dir=EMODE_OUT,
                csv_dir="output/emode",
                sigma_xy_um=round_sigma_xy_um(sigma_mm),
                n_bunch=n_bunch_at_power(power_kw),
            )
        )
    for v_kv, power_kw, b_gs, sc_on in emode_voltage_points():
        paths.append(
            _electron_from_beam(
                volt_slug(v_kv, power_kw),
                "injection",
                sc_on=sc_on,
                b_y=b_gs * GS_TO_T,
                b_tag=b_tag(b_gs),
                config_dir=EMODE_OUT,
                csv_dir="output/emode",
                sigma_xy_um=round_sigma_xy_um(10),
                n_bunch=n_bunch_at_power(power_kw),
                e_y=v_kv * 1e3 / GAP_M,
            )
        )
    for beam, dx, dy, power_kw, b_gs, sc_on in emode_offset_points():
        paths.append(
            _electron_from_beam(
                offset_slug(beam, dx, dy, power_kw),
                beam,
                sc_on=sc_on,
                b_y=b_gs * GS_TO_T,
                b_tag=b_tag(b_gs),
                config_dir=EMODE_OUT,
                csv_dir="output/emode",
                sigma_xy_um=round_sigma_xy_um(10),
                n_bunch=n_bunch_at_power(power_kw),
                offset_mm=(dx, dy),
            )
        )
    return paths


def write_emode_fine_cd() -> list[Path]:
    """Write fine C/D XMLs in run order C1, C2, D1, D2 (duplicates skipped)."""
    EMODE_OUT.mkdir(parents=True, exist_ok=True)
    seen: set[Path] = set()
    paths: list[Path] = []

    def add_volt(v_kv: int, power_kw: int, b_gs: int, sc_on: bool) -> None:
        dest = volt_xml_path(v_kv, power_kw, b_gs, sc_on)
        if dest in seen:
            return
        seen.add(dest)
        paths.append(
            _electron_from_beam(
                volt_slug(v_kv, power_kw),
                "injection",
                sc_on=sc_on,
                b_y=b_gs * GS_TO_T,
                b_tag=b_tag(b_gs),
                config_dir=EMODE_OUT,
                csv_dir="output/emode",
                sigma_xy_um=round_sigma_xy_um(10),
                n_bunch=n_bunch_at_power(power_kw),
                e_y=v_kv * 1e3 / GAP_M,
            )
        )

    def add_offset(
        beam: str, dx: int, dy: int, power_kw: int, b_gs: int, sc_on: bool
    ) -> None:
        dest = offset_xml_path(beam, dx, dy, power_kw, b_gs, sc_on)
        if dest in seen:
            return
        seen.add(dest)
        paths.append(
            _electron_from_beam(
                offset_slug(beam, dx, dy, power_kw),
                beam,
                sc_on=sc_on,
                b_y=b_gs * GS_TO_T,
                b_tag=b_tag(b_gs),
                config_dir=EMODE_OUT,
                csv_dir="output/emode",
                sigma_xy_um=round_sigma_xy_um(10),
                n_bunch=n_bunch_at_power(power_kw),
                offset_mm=(dx, dy),
            )
        )

    for v_kv, power_kw, b_gs, sc_on in emode_fine_c1_voltage_points():
        add_volt(v_kv, power_kw, b_gs, sc_on)
    for v_kv, power_kw, b_gs, sc_on in emode_fine_c2_voltage_points():
        add_volt(v_kv, power_kw, b_gs, sc_on)
    for beam, dx, dy, power_kw, b_gs, sc_on in emode_fine_d1_offset_points():
        add_offset(beam, dx, dy, power_kw, b_gs, sc_on)
    for beam, dx, dy, power_kw, b_gs, sc_on in emode_fine_d2_offset_points():
        add_offset(beam, dx, dy, power_kw, b_gs, sc_on)
    return paths


def write_figure_dense_emode() -> list[Path]:
    """Write C3 (1 kV / 10 G) and D3 (Δx / 1 mm at 300 G) XMLs only."""
    EMODE_OUT.mkdir(parents=True, exist_ok=True)
    seen: set[Path] = set()
    paths: list[Path] = []

    def add_volt(v_kv: int, power_kw: int, b_gs: int, sc_on: bool) -> None:
        dest = volt_xml_path(v_kv, power_kw, b_gs, sc_on)
        if dest in seen:
            return
        seen.add(dest)
        paths.append(
            _electron_from_beam(
                volt_slug(v_kv, power_kw),
                "injection",
                sc_on=sc_on,
                b_y=b_gs * GS_TO_T,
                b_tag=b_tag(b_gs),
                config_dir=EMODE_OUT,
                csv_dir="output/emode",
                sigma_xy_um=round_sigma_xy_um(10),
                n_bunch=n_bunch_at_power(power_kw),
                e_y=v_kv * 1e3 / GAP_M,
            )
        )

    def add_offset(
        beam: str, dx: int, dy: int, power_kw: int, b_gs: int, sc_on: bool
    ) -> None:
        dest = offset_xml_path(beam, dx, dy, power_kw, b_gs, sc_on)
        if dest in seen:
            return
        seen.add(dest)
        paths.append(
            _electron_from_beam(
                offset_slug(beam, dx, dy, power_kw),
                beam,
                sc_on=sc_on,
                b_y=b_gs * GS_TO_T,
                b_tag=b_tag(b_gs),
                config_dir=EMODE_OUT,
                csv_dir="output/emode",
                sigma_xy_um=round_sigma_xy_um(10),
                n_bunch=n_bunch_at_power(power_kw),
                offset_mm=(dx, dy),
            )
        )

    for pt in emode_fine_c3_voltage_points():
        add_volt(*pt)
    for pt in emode_fine_d3_offset_points():
        add_offset(*pt)
    return paths


def emode_fine_cd_xml_relpaths() -> list[str]:
    """Relative XML paths in run order C1, C2, D1, D2 (duplicates skipped)."""
    seen: set[str] = set()
    rels: list[str] = []

    def add(path: Path) -> None:
        rel = str(path.relative_to(ROOT)) if path.is_absolute() else str(path)
        if rel in seen:
            return
        seen.add(rel)
        rels.append(rel)

    for pt in emode_fine_c1_voltage_points():
        add(volt_xml_path(*pt))
    for pt in emode_fine_c2_voltage_points():
        add(volt_xml_path(*pt))
    for pt in emode_fine_d1_offset_points():
        add(offset_xml_path(*pt))
    for pt in emode_fine_d2_offset_points():
        add(offset_xml_path(*pt))
    return rels


def emode_matrix_report(emode_dir: Path | None = None) -> str:
    """Human-readable matrix of the replan with done / to-run counts."""
    dest_dir = emode_dir if emode_dir is not None else (ROOT / "output" / "emode")

    def done_file(name: str) -> bool:
        f = dest_dir / name
        return f.is_file() and f.stat().st_size > 0

    def done(pt: EmodePoint) -> bool:
        return done_file(emode_csv_name(*pt))

    pts = emode_points()
    lines: list[str] = []
    lines.append("All blocks: ROUND beams, σ_y = σ_x (no reuse of the elliptical 25×20 / 10×8 runs)")
    lines.append(
        f"A/B  B grid: {EMODE_BSCAN_GS[0]}–{EMODE_BSCAN_GS[-1]} G step "
        f"{EMODE_BSCAN_GS[1] - EMODE_BSCAN_GS[0]} G ({len(EMODE_BSCAN_GS)} values); "
        f"size-scan fields: {', '.join(str(b) for b in EMODE_SIZE_B_GS)} G; "
        f"powers: {', '.join(str(p) for p in POWERS_KW)} kW; "
        f"sizes: {SIZE_MM[0]}–{SIZE_MM[-1]} mm step 1 mm; ref. beams 25×25 inj., 10×10 ext., 10×10 inj."
    )
    lines.append(
        f"C    cage voltage: {EMODE_VOLTAGES_KV[0]}–{EMODE_VOLTAGES_KV[-1]} kV step "
        f"{EMODE_VOLTAGES_KV[1] - EMODE_VOLTAGES_KV[0]} kV ({len(EMODE_VOLTAGES_KV)} values); "
        f"B: {EMODE_VOLT_B_GS[0]}–{EMODE_VOLT_B_GS[-2]} G step {EMODE_VOLT_B_GS[1]} G + 1000 G; "
        f"inj. 10×10 mm; {', '.join(str(p) for p in EMODE_CHECK_POWERS_KW)} kW"
    )
    lines.append(
        "D    beam offset (dx, dy) mm: "
        + ", ".join(f"({dx:+d}, {dy:+d})" for dx, dy in EMODE_OFFSETS_MM)
        + f"; B: {', '.join(str(b) for b in EMODE_OFFSET_B_GS)} G; inj. and ext. 10×10 mm; "
        f"{', '.join(str(p) for p in EMODE_CHECK_POWERS_KW)} kW"
    )
    lines.append("")
    header = f"{'Block / family':<48}{'runs':>6}{'done':>6}{'to run':>8}"
    lines.append(header)
    lines.append("-" * len(header))
    total = total_done = 0

    def row_counts(label: str, n: int, d: int) -> None:
        nonlocal total, total_done
        total += n
        total_done += d
        lines.append(f"{label:<48}{n:>6}{d:>6}{n - d:>8}")

    def row(label: str, subset: list[EmodePoint]) -> None:
        row_counts(label, len(subset), sum(done(p) for p in subset))

    seen: set[EmodePoint] = set()
    for beam, sigma_mm in EMODE_REF_BEAMS:
        subset = [
            p for p in pts if p[0] == beam and p[1] == sigma_mm and p[3] in EMODE_BSCAN_GS
        ]
        seen.update(subset)
        stage = "inj." if beam == "injection" else "ext."
        row(f"A  B-scan {stage} e− σx={sigma_mm} mm, 100–500 kW", subset)
    for beam in ("injection", "extraction"):
        subset = [
            p
            for p in pts
            if p[0] == beam and p[3] in EMODE_SIZE_B_GS and p not in seen
        ]
        seen.update(subset)
        stage = "inj." if beam == "injection" else "ext."
        row(f"B  size scan {stage} e− 3–20 mm (new points only)", subset)
    vpts = emode_voltage_points()
    row_counts(
        "C  cage voltage 5–30 kV, inj. e− 10×10 mm",
        len(vpts),
        sum(done_file(volt_csv_name(*p)) for p in vpts),
    )
    for beam, _sigma in EMODE_OFFSET_BEAMS:
        opts = [p for p in emode_offset_points() if p[0] == beam]
        stage = "inj." if beam == "injection" else "ext."
        row_counts(
            f"D  beam offset {stage} e− 10 mm, 4 offsets",
            len(opts),
            sum(done_file(offset_csv_name(*p)) for p in opts),
        )
    lines.append("-" * len(header))
    lines.append(f"{'Total':<48}{total:>6}{total_done:>6}{total - total_done:>8}")
    return "\n".join(lines)


def emode_fine_cd_matrix_report(emode_dir: Path | None = None) -> str:
    """Print the planned fine C/D matrix with reuse / new counts. Does not write XMLs."""
    dest_dir = emode_dir if emode_dir is not None else (ROOT / "output" / "emode")

    def done_file(name: str) -> bool:
        f = dest_dir / name
        return f.is_file() and f.stat().st_size > 0

    def v_done(pt: VoltPoint) -> bool:
        return done_file(volt_csv_name(*pt))

    def o_done(pt: OffsetPoint) -> bool:
        return done_file(offset_csv_name(*pt))

    c1 = emode_fine_c1_voltage_points()
    c2 = emode_fine_c2_voltage_points()
    c_union = emode_fine_voltage_points()
    d1 = emode_fine_d1_offset_points()
    d2 = emode_fine_d2_offset_points()
    d_union = emode_fine_offset_points()
    coarse_v = set(emode_voltage_points())
    coarse_o = set(emode_offset_points())
    full_c = [
        (v, p, b, sc)
        for v in EMODE_FINE_VOLTAGES_KV
        for b in EMODE_FINE_B_GS
        for p, sc in _sc_power_pts()
    ]

    lines: list[str] = []
    lines.append("Fine C/D — PLAN ONLY (this flag does not write XMLs or run Virtual-IPM)")
    lines.append(
        "Held fixed: 100000 e−, Voitkiv H₂, round 10×10 mm, SC-off at 100 kW shared, "
        f"P = {', '.join(str(p) for p in EMODE_CHECK_POWERS_KW)} kW"
    )
    lines.append(
        f"C1  V = {EMODE_FINE_VOLTAGES_KV[0]}–{EMODE_FINE_VOLTAGES_KV[-1]} kV step 1 kV "
        f"({len(EMODE_FINE_VOLTAGES_KV)} values); diagnostic B = "
        + ", ".join(str(b) for b in EMODE_FINE_DIAG_B_GS)
        + " G; inj. 10×10 mm"
    )
    lines.append(
        "C2  5 G B-scan at V = "
        + ", ".join(str(v) for v in EMODE_FINE_VOLT_BFINE_KV)
        + f" kV; B = {EMODE_FINE_B_GS[0]}–300 G step 5 G + 1000 G "
        f"({len(EMODE_FINE_B_GS)} values). 25 kV / 5 G is Block A, not repeated."
    )
    lines.append(
        f"D1  Δy = {EMODE_FINE_DY_MM[0]}–{EMODE_FINE_DY_MM[-1]} mm step 1 mm, Δx = 0 "
        f"({len(EMODE_FINE_DY_MM)} values, Δy=0 omitted → Block A); diagnostic B; "
        "inj. and ext. 10×10 mm"
    )
    lines.append(
        "D2  5 G B-scan at Δy = "
        + ", ".join(f"{dy:+d}" for dy in EMODE_FINE_OFFSET_BFINE_DY)
        + " mm, Δx = 0; inj. and ext. No Δx refinement."
    )
    lines.append(
        f"Rejected full C cartesian: {len(EMODE_FINE_VOLTAGES_KV)} V × "
        f"{len(EMODE_FINE_B_GS)} B × {len(_sc_power_pts())} SC = {len(full_c)} "
        f"({len(full_c) - len(coarse_v)} new after coarse C)"
    )
    lines.append("")
    header = f"{'Block / slice':<56}{'runs':>6}{'reuse':>7}{'new':>7}"
    lines.append(header)
    lines.append("-" * len(header))

    def row(label: str, pts: list, done_fn, extra_reuse: int = 0) -> None:
        n = len(pts)
        reuse = sum(done_fn(p) for p in pts) + extra_reuse
        lines.append(f"{label:<56}{n:>6}{reuse:>7}{n - reuse:>7}")

    # Δy=0 at diagnostic B is Block A (not in d1 file list).
    dy0_reuse = (
        len(EMODE_FINE_DIAG_B_GS) * len(EMODE_OFFSET_BEAMS) * len(_sc_power_pts())
    )
    row("C1  1 kV × diagnostic B", c1, v_done)
    c2_only = [p for p in c2 if p not in set(c1)]
    row("C2  5 G B-scan (points not in C1)", c2_only, v_done)
    row("C   union (C1 ∪ C2)", c_union, v_done)
    row("D1  1 mm Δy × diagnostic B (Δy≠0 files)", d1, o_done)
    d2_only = [p for p in d2 if p not in set(d1)]
    row("D2  5 G B-scan at Δy=±5 (points not in D1)", d2_only, o_done)
    row("D   union (D1 ∪ D2 files)", d_union, o_done)
    lines.append(
        f"{'D   Δy=0 diagnostic B (Block A, not generated)':<56}"
        f"{dy0_reuse:>6}{dy0_reuse:>7}{0:>7}"
    )
    lines.append("-" * len(header))
    c_new = len(c_union) - sum(v_done(p) for p in c_union)
    d_new = len(d_union) - sum(o_done(p) for p in d_union)
    lines.append(
        f"{'Fine C+D new files (after existing CSVs)':<56}"
        f"{len(c_union) + len(d_union):>6}"
        f"{len(c_union) + len(d_union) - c_new - d_new:>7}"
        f"{c_new + d_new:>7}"
    )
    lines.append("")
    lines.append(
        f"Coarse C already on disk: {sum(v_done(p) for p in emode_voltage_points())}"
        f" / {len(coarse_v)}. Coarse D: "
        f"{sum(o_done(p) for p in emode_offset_points())} / {len(coarse_o)}."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Ion-mode parameter-scan matrix (Blocks A–D), parallel to e-mode replan.
# ---------------------------------------------------------------------------

# (species_slug, beam, σ_mm, power_kW, B_G, SC_on)
ImodePoint = tuple[str, str, int, int, int, bool]
# (species_slug, V_kV, power_kW, B_G, SC_on)
ImodeVoltPoint = tuple[str, int, int, int, bool]
# (species_slug, beam, dx, dy, power_kW, B_G, SC_on)
ImodeOffsetPoint = tuple[str, str, int, int, int, int, bool]

_SPECIES_REST = {slug: rest for slug, rest, _label in ION_SPECIES}


def _imode_sc_flags(species_slug: str, power_kw: int) -> tuple[bool, ...]:
    """SC-off is mass-independent; only H₂⁺ writes it, at 100 kW."""
    if species_slug == "ions":
        return (True, False) if power_kw == 100 else (True,)
    return (True,)


def imode_slug(species: str, beam_key: str, sigma_mm: int, power_kw: int) -> str:
    return f"{beam_key}_{species}_s{sigma_mm}x{sigma_mm}mm_p{power_kw}kw"


def imode_csv_name(
    species: str, beam_key: str, sigma_mm: int, power_kw: int, b_gs: int, sc_on: bool
) -> str:
    tag = "sc_on" if sc_on else "sc_off"
    return f"csns_{imode_slug(species, beam_key, sigma_mm, power_kw)}_{b_tag(b_gs)}_{tag}.csv"


def imode_volt_slug(species: str, v_kv: int, power_kw: int) -> str:
    return f"injection_{species}_s10x10mm_v{v_kv}kv_p{power_kw}kw"


def imode_volt_csv_name(
    species: str, v_kv: int, power_kw: int, b_gs: int, sc_on: bool
) -> str:
    tag = "sc_on" if sc_on else "sc_off"
    return f"csns_{imode_volt_slug(species, v_kv, power_kw)}_{b_tag(b_gs)}_{tag}.csv"


def imode_offset_slug(
    species: str, beam: str, dx: int, dy: int, power_kw: int
) -> str:
    return (
        f"{beam}_{species}_s10x10mm_dx{_signed(dx)}mm_dy{_signed(dy)}mm_p{power_kw}kw"
    )


def imode_offset_csv_name(
    species: str, beam: str, dx: int, dy: int, power_kw: int, b_gs: int, sc_on: bool
) -> str:
    tag = "sc_on" if sc_on else "sc_off"
    return (
        f"csns_{imode_offset_slug(species, beam, dx, dy, power_kw)}"
        f"_{b_tag(b_gs)}_{tag}.csv"
    )


def imode_volt_xml_path(
    species: str, v_kv: int, power_kw: int, b_gs: int, sc_on: bool
) -> Path:
    return IMODE_OUT / f"{_stem(imode_volt_slug(species, v_kv, power_kw), sc_on, b_tag(b_gs))}.xml"


def imode_offset_xml_path(
    species: str, beam: str, dx: int, dy: int, power_kw: int, b_gs: int, sc_on: bool
) -> Path:
    return IMODE_OUT / (
        f"{_stem(imode_offset_slug(species, beam, dx, dy, power_kw), sc_on, b_tag(b_gs))}.xml"
    )


def imode_points() -> list[ImodePoint]:
    """Every (species, beam, σ, P, B, SC) point of Blocks A+B, deduplicated."""
    pts: dict[ImodePoint, None] = {}

    def add(species: str, beam: str, sigma_mm: int, b_gs: int) -> None:
        for power_kw in POWERS_KW:
            for sc_on in _imode_sc_flags(species, power_kw):
                pts[(species, beam, sigma_mm, power_kw, b_gs, sc_on)] = None

    # Block A: sparse B grid for the three reference beams × three species.
    for beam, sigma_mm in IMODE_REF_BEAMS:
        for b_gs in IMODE_BSCAN_GS:
            for species, _rest, _label in ION_SPECIES:
                add(species, beam, sigma_mm, b_gs)
    # Block B: σ = 3–20 mm at checkpoint fields, both stages × three species.
    for sigma_mm in SIZE_MM:
        for b_gs in IMODE_SIZE_B_GS:
            for beam in ("injection", "extraction"):
                for species, _rest, _label in ION_SPECIES:
                    add(species, beam, sigma_mm, b_gs)
    return list(pts)


def imode_voltage_points() -> list[ImodeVoltPoint]:
    """Block C: cage voltage × B × {100, 500 kW} × species on inj. 10×10 mm."""
    pts: list[ImodeVoltPoint] = []
    for species, _rest, _label in ION_SPECIES:
        for v_kv in IMODE_VOLTAGES_KV:
            for b_gs in IMODE_VOLT_B_GS:
                for power_kw in IMODE_CHECK_POWERS_KW:
                    for sc_on in _imode_sc_flags(species, power_kw):
                        pts.append((species, v_kv, power_kw, b_gs, sc_on))
    return pts


def imode_offset_points() -> list[ImodeOffsetPoint]:
    """Block D: beam offset × B × {100, 500 kW} × species, 10×10 mm inj./ext."""
    pts: list[ImodeOffsetPoint] = []
    for species, _rest, _label in ION_SPECIES:
        for beam, _sigma in IMODE_OFFSET_BEAMS:
            for dx, dy in IMODE_OFFSETS_MM:
                for b_gs in IMODE_OFFSET_B_GS:
                    for power_kw in IMODE_CHECK_POWERS_KW:
                        for sc_on in _imode_sc_flags(species, power_kw):
                            pts.append((species, beam, dx, dy, power_kw, b_gs, sc_on))
    return pts


def imode_fine_voltage_points() -> list[ImodeVoltPoint]:
    """Fig. 9: 1 kV cage-voltage grid at B = 0, 100 kW, injection 10 mm."""
    pts: list[ImodeVoltPoint] = []
    for species, _rest, _label in ION_SPECIES:
        for v_kv in IMODE_FINE_VOLTAGES_KV:
            for sc_on in _imode_sc_flags(species, 100):
                pts.append((species, v_kv, 100, 0, sc_on))
    return pts


def imode_fine_offset_points() -> list[ImodeOffsetPoint]:
    """Fig. 11: 1 mm Δy (−5…+5) and Δx (0…10) at B = 0, 100 kW, 25 kV."""
    pts: list[ImodeOffsetPoint] = []
    for species, _rest, _label in ION_SPECIES:
        for beam, _sigma in IMODE_OFFSET_BEAMS:
            seen: set[tuple[int, int]] = set()
            for dy in IMODE_FINE_DY_MM:
                seen.add((0, dy))
            for dx in IMODE_FINE_DX_MM:
                seen.add((dx, 0))
            for dx, dy in sorted(seen):
                if (dx, dy) == (0, 0):
                    continue
                for sc_on in _imode_sc_flags(species, 100):
                    pts.append((species, beam, dx, dy, 100, 0, sc_on))
    return pts


def write_figure_dense_imode() -> list[Path]:
    """Write ion-mode 1 kV / 1 mm figure XMLs (injection; extraction is v2)."""
    IMODE_OUT.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for species, v_kv, power_kw, b_gs, sc_on in imode_fine_voltage_points():
        paths.append(
            ion_case(
                imode_volt_slug(species, v_kv, power_kw),
                rest_energy=_SPECIES_REST[species],
                sc_on=sc_on,
                beam_key="injection",
                b_y=b_gs * GS_TO_T,
                b_tag=b_tag(b_gs),
                config_dir=IMODE_OUT,
                csv_dir="output/imode",
                sigma_xy_um=round_sigma_xy_um(10),
                n_bunch=n_bunch_at_power(power_kw),
                e_y=-(v_kv * 1e3 / GAP_M),
            )
        )
    for species, beam, dx, dy, power_kw, b_gs, sc_on in imode_fine_offset_points():
        if beam != "injection":
            continue
        paths.append(
            ion_case(
                imode_offset_slug(species, beam, dx, dy, power_kw),
                rest_energy=_SPECIES_REST[species],
                sc_on=sc_on,
                beam_key=beam,
                b_y=b_gs * GS_TO_T,
                b_tag=b_tag(b_gs),
                config_dir=IMODE_OUT,
                csv_dir="output/imode",
                sigma_xy_um=round_sigma_xy_um(10),
                n_bunch=n_bunch_at_power(power_kw),
                offset_mm=(float(dx), float(dy)),
            )
        )
    return paths


def write_imode_replan() -> list[Path]:
    """Write the ion-mode matrix (Blocks A–D). Round beams; three ToF species."""
    IMODE_OUT.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for species, beam, sigma_mm, power_kw, b_gs, sc_on in imode_points():
        paths.append(
            ion_case(
                imode_slug(species, beam, sigma_mm, power_kw),
                rest_energy=_SPECIES_REST[species],
                sc_on=sc_on,
                beam_key=beam,
                b_y=b_gs * GS_TO_T,
                b_tag=b_tag(b_gs),
                config_dir=IMODE_OUT,
                csv_dir="output/imode",
                sigma_xy_um=round_sigma_xy_um(sigma_mm),
                n_bunch=n_bunch_at_power(power_kw),
            )
        )
    for species, v_kv, power_kw, b_gs, sc_on in imode_voltage_points():
        paths.append(
            ion_case(
                imode_volt_slug(species, v_kv, power_kw),
                rest_energy=_SPECIES_REST[species],
                sc_on=sc_on,
                beam_key="injection",
                b_y=b_gs * GS_TO_T,
                b_tag=b_tag(b_gs),
                config_dir=IMODE_OUT,
                csv_dir="output/imode",
                sigma_xy_um=round_sigma_xy_um(10),
                n_bunch=n_bunch_at_power(power_kw),
                e_y=-(v_kv * 1e3 / GAP_M),
            )
        )
    for species, beam, dx, dy, power_kw, b_gs, sc_on in imode_offset_points():
        paths.append(
            ion_case(
                imode_offset_slug(species, beam, dx, dy, power_kw),
                rest_energy=_SPECIES_REST[species],
                sc_on=sc_on,
                beam_key=beam,
                b_y=b_gs * GS_TO_T,
                b_tag=b_tag(b_gs),
                config_dir=IMODE_OUT,
                csv_dir="output/imode",
                sigma_xy_um=round_sigma_xy_um(10),
                n_bunch=n_bunch_at_power(power_kw),
                offset_mm=(float(dx), float(dy)),
            )
        )
    return paths


def imode_replan_xml_relpaths() -> list[str]:
    """XML paths in run order: C, D, A reference beams, then B sizes."""
    rels: list[str] = []
    seen: set[str] = set()

    def add(path: Path) -> None:
        rel = str(path.relative_to(ROOT))
        if rel not in seen:
            seen.add(rel)
            rels.append(rel)

    for pt in imode_voltage_points():
        add(imode_volt_xml_path(*pt))
    for pt in imode_offset_points():
        add(imode_offset_xml_path(*pt))
    # Block A reference beams before the rest of A∪B.
    a_keys = {(beam, sigma) for beam, sigma in IMODE_REF_BEAMS}
    for species, beam, sigma_mm, power_kw, b_gs, sc_on in imode_points():
        if (beam, sigma_mm) in a_keys and b_gs in IMODE_BSCAN_GS:
            dest = IMODE_OUT / (
                f"{_stem(imode_slug(species, beam, sigma_mm, power_kw), sc_on, b_tag(b_gs))}.xml"
            )
            add(dest)
    for species, beam, sigma_mm, power_kw, b_gs, sc_on in imode_points():
        dest = IMODE_OUT / (
            f"{_stem(imode_slug(species, beam, sigma_mm, power_kw), sc_on, b_tag(b_gs))}.xml"
        )
        add(dest)
    return rels


def imode_matrix_report(imode_dir: Path | None = None) -> str:
    """Human-readable ion-mode matrix with done / to-run counts. Plan-ready."""
    dest_dir = imode_dir if imode_dir is not None else (ROOT / "output" / "imode")

    def done_file(name: str) -> bool:
        f = dest_dir / name
        return f.is_file() and f.stat().st_size > 0

    def done(pt: ImodePoint) -> bool:
        return done_file(imode_csv_name(*pt))

    pts = imode_points()
    lines: list[str] = []
    lines.append(
        "Ion-mode matrix — ROUND beams, σ_y = σ_x; three ToF species "
        "(H₂⁺, H₂O⁺, N₂⁺). No reuse of elliptical ionsize / bscan runs."
    )
    lines.append(
        "SC-off: H₂⁺ at 100 kW only (mass-independent without bunch fields); "
        "shared across species and powers."
    )
    lines.append(
        f"All blocks share B = {', '.join(str(b) for b in IMODE_B_GS)} G "
        f"(no guide / mid checkpoint / design 0.1 T). No ion B-scan grid — "
        f"expansion is flat vs B. Ref. beams 25×25 inj., 10×10 ext., 10×10 inj.; "
        f"powers {', '.join(str(p) for p in POWERS_KW)} kW"
    )
    lines.append(
        f"B    size scan: {SIZE_MM[0]}–{SIZE_MM[-1]} mm step 1 mm; same B; inj. + ext."
    )
    lines.append(
        f"C    cage voltage: {IMODE_VOLTAGES_KV[0]}–{IMODE_VOLTAGES_KV[-1]} kV step "
        f"{IMODE_VOLTAGES_KV[1] - IMODE_VOLTAGES_KV[0]} kV; same B; inj. 10×10 mm; "
        f"{', '.join(str(p) for p in IMODE_CHECK_POWERS_KW)} kW"
    )
    lines.append(
        "D    beam offset (dx, dy) mm: "
        + ", ".join(f"({dx:+d}, {dy:+d})" for dx, dy in IMODE_OFFSETS_MM)
        + f"; same B; inj. and ext. 10×10 mm; "
        f"{', '.join(str(p) for p in IMODE_CHECK_POWERS_KW)} kW"
    )
    lines.append(
        "vs e-mode: same round beams / V / offset axes; B only at 0/200/1000 G "
        "(e-mode used dense B grids); ×3 species. Plan only until --imode-replan is run."
    )
    lines.append("")
    header = f"{'Block / family':<56}{'runs':>6}{'done':>6}{'to run':>8}"
    lines.append(header)
    lines.append("-" * len(header))
    total = total_done = 0

    def row_counts(label: str, n: int, d: int) -> None:
        nonlocal total, total_done
        total += n
        total_done += d
        lines.append(f"{label:<56}{n:>6}{d:>6}{n - d:>8}")

    def row(label: str, subset: list[ImodePoint]) -> None:
        row_counts(label, len(subset), sum(done(p) for p in subset))

    seen: set[ImodePoint] = set()
    for beam, sigma_mm in IMODE_REF_BEAMS:
        subset = [
            p
            for p in pts
            if p[1] == beam and p[2] == sigma_mm and p[4] in IMODE_BSCAN_GS
        ]
        seen.update(subset)
        stage = "inj." if beam == "injection" else "ext."
        row(
            f"A  ref. beams {stage} σ={sigma_mm} mm × 3 spp, 100–500 kW",
            subset,
        )
    for beam in ("injection", "extraction"):
        subset = [
            p
            for p in pts
            if p[1] == beam and p[4] in IMODE_SIZE_B_GS and p not in seen
        ]
        seen.update(subset)
        stage = "inj." if beam == "injection" else "ext."
        row(f"B  size scan {stage} 3–20 mm × 3 spp (new points)", subset)
    vpts = imode_voltage_points()
    row_counts(
        "C  cage voltage 5–30 kV, inj. 10×10 mm × 3 spp",
        len(vpts),
        sum(done_file(imode_volt_csv_name(*p)) for p in vpts),
    )
    for beam, _sigma in IMODE_OFFSET_BEAMS:
        opts = [p for p in imode_offset_points() if p[1] == beam]
        stage = "inj." if beam == "injection" else "ext."
        row_counts(
            f"D  beam offset {stage} 10 mm, 4 offsets × 3 spp",
            len(opts),
            sum(done_file(imode_offset_csv_name(*p)) for p in opts),
        )
    lines.append("-" * len(header))
    lines.append(f"{'Total':<56}{total:>6}{total_done:>6}{total - total_done:>8}")
    lines.append("")
    # Sanity breakdown by species for A∪B.
    for species, _rest, label in ION_SPECIES:
        n_sp = sum(1 for p in pts if p[0] == species)
        lines.append(f"  A∪B files for {label}: {n_sp}")
    lines.append(f"  C files: {len(vpts)}; D files: {len(imode_offset_points())}")
    return "\n".join(lines)


def write_sig10_ion_bscan() -> list[Path]:
    """Repeat the 0/50/100/200 G ion-mode scan at injection σ = 10×8 mm."""
    BSCAN_OUT.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for b_gs in B_SCAN_GS:
        for sc_on in (True, False):
            paths.append(
                ion_case(
                    "injection_ions_sig10",
                    rest_energy=H2_REST_ENERGY,
                    sc_on=sc_on,
                    beam_key="injection",
                    b_y=b_gs * GS_TO_T,
                    b_tag=b_tag(b_gs),
                    config_dir=BSCAN_OUT,
                    csv_dir="output/bscan",
                    sigma_xy_um=INJ_SIG10_XY,
                )
            )
    return paths


def main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fine-bscan",
        action="store_true",
        help="Also write e-mode 0–250 G / 5 G configs.",
    )
    parser.add_argument(
        "--extended",
        action="store_true",
        help="Write e-mode power B-scans (200–500 kW) and ion size scans.",
    )
    parser.add_argument(
        "--emode-replan",
        action="store_true",
        help="Write the replanned e-mode matrix (0–300 G / 5 G B-scans + size scan).",
    )
    parser.add_argument(
        "--emode-matrix",
        action="store_true",
        help="Print the replanned e-mode matrix with done / to-run counts and exit.",
    )
    parser.add_argument(
        "--emode-fine-cd-matrix",
        action="store_true",
        help="Print the fine C/D matrix with reuse / new counts and exit.",
    )
    parser.add_argument(
        "--emode-fine-cd",
        action="store_true",
        help="Write fine C/D XMLs (C1, C2, D1, D2). Does not mix into --emode-replan.",
    )
    parser.add_argument(
        "--emode-fine-cd-list",
        action="store_true",
        help="Print fine C/D XML paths in run order and exit.",
    )
    parser.add_argument(
        "--imode-matrix",
        action="store_true",
        help="Print the ion-mode A–D matrix with done / to-run counts and exit.",
    )
    parser.add_argument(
        "--imode-replan",
        action="store_true",
        help="Write the ion-mode matrix XMLs (Blocks A–D). Round beams; three species.",
    )
    parser.add_argument(
        "--imode-list",
        action="store_true",
        help="Print ion-mode XML paths in run order (C, D, A, B) and exit.",
    )
    parser.add_argument(
        "--figure-dense",
        action="store_true",
        help="Write 1 kV / 1 mm figure-dense XMLs (e-mode C3+D3, ion injection).",
    )
    args = parser.parse_args(argv)
    if args.emode_matrix:
        print(emode_matrix_report())
        return
    if args.emode_fine_cd_matrix:
        print(emode_fine_cd_matrix_report())
        return
    if args.emode_fine_cd_list:
        print("\n".join(emode_fine_cd_xml_relpaths()))
        return
    if args.imode_matrix:
        print(imode_matrix_report())
        return
    if args.imode_list:
        print("\n".join(imode_replan_xml_relpaths()))
        return
    write_design_b_configs()
    write_bscan_configs()
    write_sig10_design_configs()
    write_sig10_ion_bscan()
    if args.fine_bscan:
        write_fine_emode_bscan()
    if args.extended:
        write_emode_power_bscan()
        write_ion_size_scan()
    if args.emode_replan:
        write_emode_replan()
    if args.emode_fine_cd:
        write_emode_fine_cd()
    if args.imode_replan:
        write_imode_replan()
    if args.figure_dense:
        write_figure_dense_emode()
        write_figure_dense_imode()


if __name__ == "__main__":
    main()
