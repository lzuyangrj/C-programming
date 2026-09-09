#!/usr/bin/env python3
"""Write Virtual-IPM XML configs for the CSNS RCS IPM space-charge study."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "configs" / "csns_rcs_ipm"
BSCAN_OUT = OUT / "bscan"

# Parameters from NIMA 1092 (2026) 171809 and the cited CSNS RCS IPM papers.
# See configs/csns_rcs_ipm/PARAMETERS.md.
GAP_M = 231e-3
V_CAGE = 25e3
E_Y = V_CAGE / GAP_M  # ~108 kV/m; paper quotes ~110 kV/m
B_Y_DESIGN = 0.1  # PAC’09 cage design, 1000 G
N_PER_BUNCH_100KW = 1.56e13 / 2.0
GS_TO_T = 1.0e-4  # 1 G = 1e-4 T
B_SCAN_GS = (0, 50, 100, 200)

PROTON = "%(proton mass energy equivalent in MeV)"
H2_REST_ENERGY = f"2 * {PROTON}"

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
) -> Path:
    stem = _stem(name, sc_on, b_tag)
    csv = f"{csv_dir}/csns_{stem}.csv"
    beam = beam_xml(
        energy=energy,
        energy_unit=energy_unit,
        sigma_t_ns=sigma_t_ns,
        sigma_xy_um=sigma_xy_um,
        n_bunch=N_PER_BUNCH_100KW,
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
) -> Path:
    spec = BEAMS[beam_key]
    stem = _stem(slug, sc_on, b_tag)
    csv = f"{csv_dir}/csns_{stem}.csv"
    # Generation-only bunch (fields off) so ions are created from a single passage.
    gen = beam_xml(
        energy=spec["energy"],
        energy_unit=spec["energy_unit"],
        sigma_t_ns=spec["sigma_t_ns"],
        sigma_xy_um=spec["sigma_xy_um"],
        n_bunch=N_PER_BUNCH_100KW,
        e_off=True,
        b_off=True,
        train=single_bunch_train(),
    )
    # Tracking bunch train: ions see several subsequent bunches.
    track = beam_xml(
        energy=spec["energy"],
        energy_unit=spec["energy_unit"],
        sigma_t_ns=spec["sigma_t_ns"],
        sigma_xy_um=spec["sigma_xy_um"],
        n_bunch=N_PER_BUNCH_100KW,
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


def main() -> None:
    write_design_b_configs()
    write_bscan_configs()


if __name__ == "__main__":
    main()
