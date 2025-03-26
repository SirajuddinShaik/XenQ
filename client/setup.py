# setup.py for client/setup.py
import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

__version__ = "0.0.0"

# Client setup
CLIENT_REPO_NAME = "XenQ-Client"
CLIENT_SRC_REPO = "xenq_client"


REPO_NAME = "XenQ"
AUTHOR_USER_NAME = "SirajuddinShaik"
SRC_REPO = "xenq_client"
AUTHOR_EMAIL = "shaiksirajuddin9949@gmail.com"


setuptools.setup(
    name=SRC_REPO,
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description="XenQ: An Intelligent RAG-Powered AI Assistant for Seamless Data Interaction",
    long_description=long_description,
    long_description_content="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues",
    },
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src")
)