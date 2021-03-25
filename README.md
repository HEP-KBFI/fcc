# FCC studies

Run a notebook to study the FCC detector readouts:
```bash
scripts/manivald/jupyter_notebook.sh
```

Get the FCC software and detector descriptions:
```bash
git submodule init
git submodule update
```

Run the simulation:
```bash
source FCCSW/init.sh
fccrun sim/geant_fullsim_fccee_hepevt_CLD.py
```
