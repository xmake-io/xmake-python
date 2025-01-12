def build_wheel(
    wheel_directory, config_settings=None, metadata_directory=None
):
    return "{name}-{version}-py3-none-any.whl"


def build_sdist(sdist_directory, config_settings=None):
    return "{name}-{version}.tar.gz"


def build_editable(
    wheel_directory, config_settings=None, metadata_directory=None
):
    return "."
