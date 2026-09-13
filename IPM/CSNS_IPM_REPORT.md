# Space-charge distortion of CSNS RCS IPM measurements

Supervisor note, typeset with the **CERN Yellow Report** class
(`cernrep` / `cernyrep`; [CERN Publishing templates](https://e-publishing.cern.ch/index.php/CYR/templates)).
Prose follows *Phys.\ Rev.\ Accel.\ Beams* / *Nucl.\ Instrum.\ Methods* A
conventions (abstract, numbered sections, numbered equations, numbered
references). Ion-mode guiding \(B\) is not discussed as a mitigation.

- **PDF:** [CSNS_IPM_REPORT.pdf](CSNS_IPM_REPORT.pdf)
- **Source:** [CSNS_IPM_REPORT.tex](CSNS_IPM_REPORT.tex)
- **Class files:** `tex/cern/` (official `cernrep.zip`)

Figs. 4 and 7–11 use the completed 1 kV / 1 mm Virtual-IPM grids
(26 cage voltages; 11 orbit-offset points per curve). `tab:cyc` lists
every voltage. Ion \(\Delta(V)\) on that grid scales as
\(V^{-0.96}\), \(V^{-0.75}\), \(V^{-0.80}\); a 10% \(\mathrm{H}_2^+\)
bias extrapolates to \(\sim 250\,\mathrm{kV}\).

Build (no Virtual-IPM runs):

```bash
cd IPM
TEXINPUTS=./tex/cern: pdflatex CSNS_IPM_REPORT.tex
TEXINPUTS=./tex/cern: pdflatex CSNS_IPM_REPORT.tex
```
