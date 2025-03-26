# setup.py for client/setup.py
import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

__version__ = "0.0.0"

# Client setup
CLIENT_REPO_NAME = "XenQ-Client"
CLIENT_SRC_REPO = "xenq_client"


AUTHOR_USER_NAME = "SirajuddinShaik"
AUTHOR_EMAIL = "shaiksirajuddin9949@gmail.com"

# Client setup
setuptools.setup(
    name=CLIENT_SRC_REPO,
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description="XenQ Client: Local AI Assistant for Seamless User Interaction",
    long_description=long_description,
    long_description_content="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{CLIENT_REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{CLIENT_REPO_NAME}/issues",
    },
    package_dir={"": "client/src"},
    packages=setuptools.find_packages(where="client/src")
)