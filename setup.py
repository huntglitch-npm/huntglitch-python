from setuptools import setup, find_packages
import pathlib

# Read the README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='huntglitch-python',
    version='1.0.1',
    description='Send Python exceptions and logs to HuntGlitch Lighthouse API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/huntglitch-npm/huntglitch-python',
    author='IT Path Solutions',
    author_email='support@itpathsolutions.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Logging',
        'Topic :: System :: Monitoring',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='logging, error tracking, monitoring, debugging, huntglitch',
    packages=find_packages(exclude=['tests*']),
    python_requires='>=3.7',
    install_requires=[
        'requests>=2.25.0,<3.0.0',
    ],
    extras_require={
        'env': ['python-dotenv>=0.19.0,<2.0.0'],
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.0.0',
            'black>=21.0.0',
            'flake8>=3.8.0',
            'mypy>=0.910',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/huntglitch-npm/huntglitch-python/issues',
        'Source': 'https://github.com/huntglitch-npm/huntglitch-python',
        'Documentation': 'https://github.com/huntglitch-npm/huntglitch-python#readme',
    },
    include_package_data=True,
    zip_safe=False,
)
