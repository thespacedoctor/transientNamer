from setuptools import setup
import os

moduleDirectory = os.path.dirname(os.path.realpath(__file__))
exec(open(moduleDirectory + "/transientNamer/__version__.py").read())


def readme():
    with open(moduleDirectory + '/README.md') as f:
        return f.read()


setup(name="transientNamer",
      version=__version__,
      description="A tool to automate the process of add transients to the Transient Name Server",
      long_description=readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Utilities',
      ],
      keywords=[transients],
      url='https://github.com/thespacedoctor/transientNamer',
      download_url='https://github.com/thespacedoctor/transientNamer/archive/v%(__version__)s.zip' % locals(
      ),
      author='David Young',
      author_email='davidrobertyoung@gmail.com',
      license='MIT',
      packages=['transientNamer'],
      install_requires=[
          'pyyaml',
          'fundamentals'
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      # entry_points={
      #     'console_scripts': ['transientNamer=transientNamer.cl_utils:main'],
      # },
      zip_safe=False)
