## **RC Slab Design (Equivalent Frame Method, EFM)**

- This app is under construction and use ChatGPT generated the code.
- You can see my conversation here: [ChatGPT-EFM](https://chatgpt.com/share/e95fa836-ce07-434b-9d32-a74bea921ebb)


### Instructions

1. Install Python, Git, Anaconda, and VSCode

- [Python](https://www.python.org/downloads/)
- [Git](https://github.com/git-guides/install-git)
- [Anaconda](https://docs.anaconda.com/anaconda/install/index.html)
- [VSCode](https://code.visualstudio.com/download)

2. Go to your project directory

```
cd <your project folder path>
```

3. Clone this repository

```
git clone https://github.com/Suzanoo/slab-efm.git
```

4. Create conda env and activate it

```
 conda create --name <your conda env name> python=3.xxx
 conda activate <your conda env name>
```

5. Install dependency via requirements.txt

```
pip install -r requirements.txt
```

6. Enjoy !!
```

python app/efm_flat.py --t=190 --l2=4500 --lc=2750 --fc1=20 --fc2=35
python app/efm_flat.py --t=240 --l2=3000 --lc=2750 --fc1=35 --fc2=35 --roof=True

python app/efm_drop.py --t=180 --td=775 --l2=6000 --lc=3000  --fc1=25

python app/efm_tb.py --bw=250 --h=500 --t=150 --l2=5000 --lc=3000 --fc1=25 --fc2=35
python app/efm_tb.py --bw=250 --h=500 --t=150 --l2=5000 --lc=3000 --fc1=25 --fc2=35 --type=ext

Look at FLAGS definition for alternative
```

Feedback : highwaynumber12@gmail.com
