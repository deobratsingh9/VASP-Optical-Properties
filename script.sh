#!/bin/bash
#SBATCH -J 2D-elastic
#SBATCH -N 2
#SBATCH --ntasks-per-node=16
#SBATCH -t 012:05:00
#SBATCH -A naiss2025-22-1789

export OMP_NUM_THREADS=2
export OMP_STACKSIZE=512m

module add VASP/6.5.0.16122024-omp-hpc1-intel-2023a-eb

cp KPOINTS.6 KPOINTS

rm WAVECAR* WAVEDER*

cp INCAR.DFT INCAR
mpprun vasp_std
cp OUTCAR OUTCAR.DFT
cp vasprun.xml vasprun.DFT.xml

cp INCAR.DIAG INCAR
mpprun vasp_std
cp OUTCAR OUTCAR.DIAG
cp vasprun.xml vasprun.DIAG.xml
./extract_optics.sh
mv optics.dat optics.DFT.dat

cp INCAR.GW0 INCAR
mpprun vasp_std
cp OUTCAR OUTCAR.GW0
cp vasprun.xml vasprun.GW0.xml

cp INCAR.NONE INCAR
mpprun vasp_std
cp OUTCAR OUTCAR.NONE
cp vasprun.xml vasprun.NONE.xml
./extract_optics.sh
mv optics.dat optics.RPA.dat

cp INCAR.BSE INCAR
mpprun vasp_std
cp OUTCAR OUTCAR.BSE
cp vasprun.xml vasprun.BSE.xml
./extract_optics.sh
mv optics.dat optics.BSE.dat


cp INCAR.BSEwfe INCAR
mpprun vasp_std
cp CHG.1 CHG.1-elect
cp OUTCAR OUTCAR.BSEwfe
cp vasprun.xml vasprun.BSEwfe.xml

cp INCAR.BSEwfh INCAR
mpprun vasp_std
cp CHG.1 CHG.1-hole
cp OUTCAR OUTCAR.BSEwfh
cp vasprun.xml vasprun.BSEwfh.xml
