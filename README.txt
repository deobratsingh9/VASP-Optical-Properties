For optical properties plots

module purge
module load Miniforge/24.7.1-2-hpc1
mamba activate /proj/snic2022-22-1230/users/x_deosi/optics.env

python optical.py


**********************************************************

1. Install prerequisites
On Ubuntu/Debian:

sudo apt update
sudo apt install python3 python3-venv python3-pip

2. Create your environment
python3 -m venv optics.env

3. Activate it
source optics.env/bin/activate

You’ll see (optics.env) in your terminal prompt.

4. Install required packages
pip install --upgrade pip
pip install numpy matplotlib scipy

5. Save dependencies
pip freeze > requirements.txt

6. Run your script
python your_script.py

7. Next time you work

Just activate again:

source optics.env/bin/activate
