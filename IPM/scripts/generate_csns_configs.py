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
# E-mode replan. Block A: full B grid 0–300 G / 5 G for the three reference
# beams at every power. Block B: σ_x = 3–20 mm size scan at checkpoint fields
# taken from the same grid, plus the 0.1 T design field.
EMODE_BSCAN_GS = tuple(range(0, 301, 5))
EMODE_SIZE_B_GS = (0, 100, 200, 300, 1000)
# (beam stage, σ_x in mm) reference beams for Block A; 25 mm = painted 25×20.
EMODE_REF_BEAMS = (("injection", 25), ("extraction", 10), ("injection", 10))
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
) -> str:
    off_e = "true" if e_off else "false"
    off_b = "true" if b_off else "false"
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
    )
    xml = wrap(
        "    <Beams>\n"
        + beam
        + "\n    </Beams>\n"
        + device_and_fields(e_y=E_Y, b_y=b_y)
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
) -> Path:
    spec = BEAMS[beam_key]
    sigma = sigma_xy_um if sigma_xy_um is not None else spec["sigma_xy_um"]
    pop = N_PER_BUNCH_100KW if n_bunch is None else n_bunch
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
    )
    xml = wrap(
        "    <Beams>\n"
        + gen
        + "\n"
        + track
        + "\n    </Beams>\n"
        # Ions are collected at the lower y-boundary, so E_y is reversed vs electron mode.
        + device_and_fields(e_y=-E_Y, b_y=b_y)
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
    sx = sigma_x_mm * 1e3
    sy = sigma_x_mm * ASPECT_YX * 1e3
    return f"[ {sx:.0f}, {sy:.0f} ]"


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
    return f"{beam_key}_electrons_s{sigma_mm}mm_p{power_kw}kw"


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


def write_emode_replan() -> list[Path]:
    """Write the replanned e-mode matrix (see `emode_points`)."""
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
                sigma_xy_um=sigma_xy_um(sigma_mm),
                n_bunch=n_bunch_at_power(power_kw),
            )
        )
    return paths


def existing_emode_source(
    beam: str, sigma_mm: int, power_kw: int, b_gs: int, sc_on: bool
) -> Path | None:
    """Locate a CSV from the closed scans that has identical parameters."""
    tag = "sc_on" if sc_on else "sc_off"
    if (beam, sigma_mm) == ("injection", 25):
        family, sig_suffix = "injection_electrons", ""
    elif (beam, sigma_mm) == ("extraction", 10):
        family, sig_suffix = "extraction_electrons", ""
    elif (beam, sigma_mm) == ("injection", 10):
        family, sig_suffix = "injection_electrons", "_sig10"
    else:
        return None
    if b_gs == 1000 and power_kw == 100:
        return ROOT / "output" / f"csns_{family}{sig_suffix}_{tag}.csv"
    if b_gs in B_SCAN5_GS:
        if power_kw == 100:
            return ROOT / "output" / "bscan5" / f"csns_{family}{sig_suffix}_b{b_gs}G_{tag}.csv"
        if sc_on and not sig_suffix:
            return (
                ROOT
                / "output"
                / "bscan5_power"
                / f"csns_{family}_p{power_kw}kW_b{b_gs}G_sc_on.csv"
            )
    return None


def link_existing_emode_outputs(emode_dir: Path | None = None, verbose: bool = True) -> int:
    """Hard-link already-run e-mode CSVs into output/emode/ (same parameters)."""
    dest_dir = emode_dir if emode_dir is not None else (ROOT / "output" / "emode")
    dest_dir.mkdir(parents=True, exist_ok=True)
    linked = 0
    for beam, sigma_mm, power_kw, b_gs, sc_on in emode_points():
        src = existing_emode_source(beam, sigma_mm, power_kw, b_gs, sc_on)
        if src is None or not src.is_file():
            continue
        dest = dest_dir / emode_csv_name(beam, sigma_mm, power_kw, b_gs, sc_on)
        if dest.exists() or dest.is_symlink():
            continue
        try:
            dest.hardlink_to(src)
        except OSError:
            dest.symlink_to(src.resolve())
        linked += 1
        if verbose:
            print(f"reuse {src.name} -> {dest.name}")
    return linked


def emode_matrix_report(emode_dir: Path | None = None) -> str:
    """Human-readable matrix of the replan with done / to-run counts."""
    dest_dir = emode_dir if emode_dir is not None else (ROOT / "output" / "emode")

    def done(pt: EmodePoint) -> bool:
        beam, sigma_mm, power_kw, b_gs, sc_on = pt
        dest = dest_dir / emode_csv_name(beam, sigma_mm, power_kw, b_gs, sc_on)
        if dest.is_file() and dest.stat().st_size > 0:
            return True
        src = existing_emode_source(beam, sigma_mm, power_kw, b_gs, sc_on)
        return src is not None and src.is_file()

    pts = emode_points()
    lines: list[str] = []
    lines.append(
        f"B grid: {EMODE_BSCAN_GS[0]}–{EMODE_BSCAN_GS[-1]} G step "
        f"{EMODE_BSCAN_GS[1] - EMODE_BSCAN_GS[0]} G ({len(EMODE_BSCAN_GS)} values); "
        f"size-scan fields: {', '.join(str(b) for b in EMODE_SIZE_B_GS)} G; "
        f"powers: {', '.join(str(p) for p in POWERS_KW)} kW; "
        f"sizes: {SIZE_MM[0]}–{SIZE_MM[-1]} mm step 1 mm (σ_y = {ASPECT_YX} σ_x)"
    )
    lines.append("")
    header = f"{'Block / family':<44}{'runs':>6}{'done':>6}{'to run':>8}"
    lines.append(header)
    lines.append("-" * len(header))
    total = total_done = 0

    def row(label: str, subset: list[EmodePoint]) -> None:
        nonlocal total, total_done
        n = len(subset)
        d = sum(done(p) for p in subset)
        total += n
        total_done += d
        lines.append(f"{label:<44}{n:>6}{d:>6}{n - d:>8}")

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
    lines.append("-" * len(header))
    lines.append(f"{'Total':<44}{total:>6}{total_done:>6}{total - total_done:>8}")
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
    args = parser.parse_args(argv)
    if args.emode_matrix:
        print(emode_matrix_report())
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


if __name__ == "__main__":
    main()
