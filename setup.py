from setuptools import setup

setup(
    name='lilt_cli',
    version='0.0.5',
    packages=['lilt_cli'],
    scripts=['bin/lilt'],
    description = 'lilt client to help upload, download translations',
    license='lilt cli to manipulate projects',
    author = 'Bruno Agutoli',
    author_email = 'bruno.agutoli@gmail.com',
    url = 'https://github.com/agutoli/lilt-cli',
    download_url = 'https://github.com/agutoli/lilt-cli/archive/master.zip',
    keywords = ['lilt', 'ci', 'codedeploy'],
    install_requires=[
        'requests==2.18.4'
    ],
    long_description=open('README.md').read(),
)
