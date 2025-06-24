import tomllib

def get_competitors():
    with open("../../config.toml", "rb") as f:
        config = tomllib.load(f)

    competitors = config['competitors']
    return competitors
