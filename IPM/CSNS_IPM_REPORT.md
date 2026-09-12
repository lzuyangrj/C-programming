# Space-charge distortion of CSNS RCS IPM measurements

Supervisor note, typeset with the **CERN Yellow Report** class
(`cernrep` / `cernyrep`; [CERN Publishing templates](https://e-publishing.cern.ch/index.php/CYR/templates)).
Prose follows *Phys.\ Rev.\ Accel.\ Beams* / *Nucl.\ Instrum.\ Methods* A
conventions (abstract, numbered sections, numbered equations, numbered
references). Ion-mode guiding \(B\) is not discussed as a mitigation.

- **PDF:** [CSNS_IPM_REPORT.pdf](CSNS_IPM_REPORT.pdf)
- **Source:** [CSNS_IPM_REPORT.tex](CSNS_IPM_REPORT.tex)
- **Class files:** `tex/cern/` (official `cernrep.zip`)

Build (no Virtual-IPM runs):

```bash
cd IPM
TEXINPUTS=./tex/cern: pdflatex CSNS_IPM_REPORT.tex
TEXINPUTS=./tex/cern: pdflatex CSNS_IPM_REPORT.tex
```
