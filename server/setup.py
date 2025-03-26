# setup.py for server/setup.py
# setup.py for setup.py
import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

__version__ = "0.0.0"

# Server setup
SERVER_REPO_NAME = "XenQ-Server"
SERVER_SRC_REPO = "xenq_server"

AUTHOR_USER_NAME = "SirajuddinShaik"
AUTHOR_EMAIL = "shaiksirajuddin9949@gmail.com"


# Server setup
setuptools.setup(
    name=SERVER_SRC_REPO,
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description="XenQ Server: Backend AI Assistant for Processing and Retrieval",
    long_description=long_description,
    long_description_content="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{SERVER_REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{SERVER_REPO_NAME}/issues",
    },
    package_dir={"": "server/src"},
    packages=setuptools.find_packages(where="server/src")
)
