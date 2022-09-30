![chart_ss](https://user-images.githubusercontent.com/112285082/189620049-257b8502-a281-4dc9-9712-835cb37513ec.png)

# specterext-stacktrack

Specter Desktop plugin to add time series charts for visualizing wallet balances.

To run:

```shell
git clone https://github.com/wombat6/specterext-stacktrack.git
cd specterext-stacktrack
pip3 install virtualenv
virtualenv --python=python3 .env
# or do this instead to avoid 3.10, is isn't yet supported
# virtualenv --python=python3.9 .env
source .env/bin/activate
pip3 install -r requirements.txt
pip3 install -e .
python3 setup.py install
python3 -m cryptoadvance.specter server --config DevelopmentConfig --debug
```

Then point your browser to http://localhost:25441 and choose Services &rarr; StackTrack.
