import pkg_resources

from urllib.parse import urlparse
from importlib.metadata import PackageNotFoundError, version

dep = (
    "solax @ git+https://github.com/VadimKraus/solax.git@feature/QVOLTHYBG33P-Inverter"
)


# req = pkg_resources.Requirement.parse(urlparse(dep).fragment)


def is_installed(package: str) -> bool:
    """Check if a package is installed and will be loaded when we import it.
    Returns True when the requirement is met.
    Returns False when the package is not installed or doesn't meet req.
    """
    try:
        pkg_resources.get_distribution(package)
        return True
    except (pkg_resources.ResolutionError, pkg_resources.ExtractionError):
        req = pkg_resources.Requirement.parse(package)
    except ValueError:
        # This is a zip file. We no longer use this in Home Assistant,
        # leaving it in for custom components.
        req = pkg_resources.Requirement.parse(urlparse(package).fragment)

    try:
        installed_version = version(req.project_name)
        # This will happen when an install failed or
        # was aborted while in progress see
        # https://github.com/home-assistant/core/issues/47699
        if installed_version is None:
            _LOGGER.error("Installed version for %s resolved to None", req.project_name)  # type: ignore[unreachable]
            return False
        return installed_version in req
    except PackageNotFoundError:
        return False


if is_installed(dep):
    req = pkg_resources.Requirement.parse(dep)
    installed_version = version(req.project_name)
    print(installed_version)
    if installed_version == "0.2.9":
        try:
            import subprocess
            import sys

            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        except e:
            print("Failed")


def main():
    import solax
    import asyncio

    async def work():
        r = await solax.real_time_api("127.0.0.1")
        return await r.get_data()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(work())
    print(data)