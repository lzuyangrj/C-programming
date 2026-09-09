#!/usr/bin/env python3
"""Write Virtual-IPM XML configs for the CSNS RCS IPM space-charge study."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "configs" / "csns_rcs_ipm"

# Parameters from NIMA 1092 (2026) 171809 and the cited CSNS RCS IPM papers.
# See configs/csns_rcs_ipm/PARAMETERS.md.
GAP_M = 231e-3
V_CAGE = 25e3
E_Y = V_CAGE / GAP_M  # ~108 kV/m; paper quotes ~110 kV/m
B_Y = 0.1
N_PER_BUNCH_100KW = 1.56e13 / 2.0


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
                <MagneticField unit="T">[ 0, {b_y}, 0 ]</MagneticField>
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


def write(name: str, xml: str) -> None:
    path = OUT / name
    path.write_text(xml)
    print(f"wrote {path}")


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
    n_particles: int = 1200,
) -> None:
    tag = "sc_on" if sc_on else "sc_off"
    csv = f"output/csns_{name}_{tag}.csv"
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
        + device_and_fields(e_y=E_Y, b_y=B_Y)
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
    write(f"{name}_{tag}.xml", xml)


def ion_injection_case(*, sc_on: bool, n_particles: int = 800) -> None:
    tag = "sc_on" if sc_on else "sc_off"
    csv = f"output/csns_injection_ions_{tag}.csv"
    # Generation-only bunch (fields off) so ions are created from a single passage.
    gen = beam_xml(
        energy="80",
        energy_unit="MeV",
        sigma_t_ns=120.0,
        sigma_xy_um="[ 25000, 20000 ]",
        n_bunch=N_PER_BUNCH_100KW,
        e_off=True,
        b_off=True,
        train=single_bunch_train(),
    )
    # Tracking bunch train: ions see several subsequent bunches.
    track = beam_xml(
        energy="80",
        energy_unit="MeV",
        sigma_t_ns=120.0,
        sigma_xy_um="[ 25000, 20000 ]",
        n_bunch=N_PER_BUNCH_100KW,
        e_off=not sc_on,
        b_off=not sc_on,
        train=circular_train(3, 980.0, -480.0),
    )
    xml = wrap(
        "    <Beams>\n"
        + gen
        + "\n"
        + track
        + "\n    </Beams>\n"
        # Ions are collected at the lower y-boundary, so E_y is reversed vs electron mode.
        + device_and_fields(e_y=-E_Y, b_y=B_Y)
        + "\n"
        + ion_generation()
        + "\n"
        + simulation(
            n_particles=n_particles,
            sim_time="12",
            sim_unit="us",
            n_steps=8000,
            charge=1,
            rest_energy="2 * %(proton mass energy equivalent in MeV)",
            filename=csv,
        )
    )
    write(f"injection_ions_{tag}.xml", xml)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # Injection: 80 MeV, σ_t = 120 ns, painted beam.
    electron_case(
        "injection_electrons",
        energy="80",
        energy_unit="MeV",
        sigma_t_ns=120.0,
        sigma_xy_um="[ 25000, 20000 ]",
        sim_time="1100",
        sim_unit="ns",
        n_steps=8000,
        sc_on=True,
    )
    electron_case(
        "injection_electrons",
        energy="80",
        energy_unit="MeV",
        sigma_t_ns=120.0,
        sigma_xy_um="[ 25000, 20000 ]",
        sim_time="1100",
        sim_unit="ns",
        n_steps=8000,
        sc_on=False,
    )
    # Extraction: 1.6 GeV, σ_t = 20 ns, adiabatically damped beam.
    electron_case(
        "extraction_electrons",
        energy="1.6",
        energy_unit="GeV",
        sigma_t_ns=20.0,
        sigma_xy_um="[ 10000, 8000 ]",
        sim_time="220",
        sim_unit="ns",
        n_steps=8000,
        sc_on=True,
    )
    electron_case(
        "extraction_electrons",
        energy="1.6",
        energy_unit="GeV",
        sigma_t_ns=20.0,
        sigma_xy_um="[ 10000, 8000 ]",
        sim_time="220",
        sim_unit="ns",
        n_steps=8000,
        sc_on=False,
    )
    ion_injection_case(sc_on=True)
    ion_injection_case(sc_on=False)


if __name__ == "__main__":
    main()
