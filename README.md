# Interpolation backend

## Running the script

In order to upload the heatmaps to the server, the script
should be run after setting the API Key as specified in the [backend
description](https://github.com/base-camp-luftdaten/data#installation--setup) (look for `apiKey`) as an environment variable.

For example:

```sh
API_KEY=my-api-key python3 interpolation.py
```

Otherwise, the server is not going to accept the heatmaps.
