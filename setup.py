import setuptools

def read_requirements(path='./requirements.txt'):
    with open(path, encoding='utf-8', errors='ignore') as file:
        install_requires = file.read()

    return install_requires

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pornhub_cli",
    version="1.0.8",
    author="Amirhossein Douzandeh",
    author_email="amirzenoozi72@gmail.com",
    description="A Simple CLI To Get Videos From Pornhub And Split By Their Action Frames and Collect Dataset",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rango-tools/pornhub-crawler-cli",
    packages=setuptools.find_packages(),
    install_requires=[
        "async-generator==1.10",
        "attrs==22.1.0",
        "certifi==2022.9.24",
        "cffi==1.15.1",
        "charset-normalizer==2.1.1",
        "docopt==0.6.2",
        "exceptiongroup==1.0.0rc9",
        "h11==0.14.0",
        "idna==3.4",
        "outcome==1.2.0",
        "pycparser==2.21",
        "PySocks==1.7.1",
        "python-dotenv==0.21.0",
        "requests==2.28.1",
        "selenium==4.5.0",
        "sniffio==1.3.0",
        "sortedcontainers==2.4.0",
        "trio==0.22.0",
        "trio-websocket==0.9.2",
        "urllib3==1.26.12",
        "wsproto==1.2.0",
        "youtube-dl==2021.12.17",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    entry_points ={
            'console_scripts': [
                'pornhub = pornhub_cli.pornhub_cli:main'
            ]
        },
    keywords ='pornhub crawler selenium python package image photo dataset cli search tools web',
)