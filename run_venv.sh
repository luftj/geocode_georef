source ./venv/bin/activate
alias python=venv/bin/python3
python -c "import sys; print(sys.version)"
# python -m pip install --upgrade pip
python -m pip install -r requirements.txt
./run.sh $1
deactivate
