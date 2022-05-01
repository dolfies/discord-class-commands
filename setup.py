from setuptools import setup
import re

with open('requirements.txt') as f:
  requirements = f.read().splitlines()

with open('discord/ext/class_commands/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

with open('README.rst') as f:
    readme = f.read()

setup(name='discord-class-commands',
      author='iDevision',
      url='https://github.com/iDevision/discord-class-commands',
      project_urls={
        'Documentation': 'https://example.com/',
        'Issue tracker': 'https://github.com/iDevision/discord-class-commands/issues',
      },
      version=version,
      packages=['discord.ext.class_commands'],
      license='MIT',
      description='A discord.py extension module to facilitate class-based creation of application commands.',
      long_description=readme,
      long_description_content_type="text/x-rst",
      include_package_data=True,
      install_requires=requirements,
      python_requires='>=3.8.0',
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Typing :: Typed',
      ]
)
