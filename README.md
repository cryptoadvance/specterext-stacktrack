![chart_ss](https://user-images.githubusercontent.com/112285082/193432527-3511bdd2-def7-47b4-94ae-0c0f815501a3.png)

# specterext-stacktrack

Specter Desktop plugin to add time series charts for visualizing wallet balances.

To run:

```shell
$ git clone https://github.com/cryptoadvance/specterext-stacktrack.git
$ cd specterext-stacktrack
$ pip3 install virtualenv
$ virtualenv --python=python3 .env
# or do this instead to avoid 3.10, as it isn't yet supported
# $ virtualenv --python=python3.9 .env
$ source .env/bin/activate
$ pip3 install -r requirements.txt
$ pip3 install -e .
$ python3 setup.py install
$ pip3 install cryptoadvance.specter
$ python3 -m cryptoadvance.specter server --config DevelopmentConfig --debug
```

Then point your browser to http://localhost:25441 and choose Services &rarr; StackTrack.

## Development

Running unit tests:

```shell
$ pytest
```
