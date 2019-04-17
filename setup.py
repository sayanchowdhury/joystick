from setuptools import setup, find_packages

setup(
    name="joystick-py",
    version="0.0.3",
    description="Invoke plume for uploading to cloud",
    license="GPLv3",
    author="Sayan Chowdhury",
    author_email="sayan.chowdhury2012@gmail.com",
    url="https://pagure.io/joystick",
    packages=find_packages(),
    package_data={'': ['LICENSE', 'fedora-messaging.toml.example', 'README.md']},
    data_files=[('config', ['fedora-messaging.toml.example'])],
    include_package_data=True,
    classifiers={
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Systems Administration',
        'Topic :: Software Development :: Libraries :: Python Modules',
    }
)
