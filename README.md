# p0sX
[![Build Status](https://drone.fap.no/api/badges/nuxis/p0sX-server/status.svg)](https://drone.fap.no/nuxis/p0sX-server)

Point of sale system for LAN parties.

## Contributing

Please read the [guidelines](https://github.com/nuxis/p0sX-server/blob/master/.github/CONTRIBUTING.md) before contributing.

## Development

Install python3, virtualenv, node, npm.

    make env

    make dev

## Example data

To load the example data, create and migrate the database:

    make migrate

Then load the json file:

    ./manage.py loaddata example_data.json

To dump the data, issue:
    ./manage.py dumpdata pos --indent 4 > example_data.json

