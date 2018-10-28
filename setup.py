from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="py4js",
    version="0.1.1",
    keywords=("pip", "py4js"),
    description="a fast and simple micro-framework for small web applications",
    long_description=long_description,
    long_description_content_type='text/markdown',  # This is important!
    license="MIT Licence",

    url="https://github.com/lixk/py4js",
    author="Xiangkui Li",
    author_email="1749498702@qq.com",
    py_modules=['py4js'],
    # packages=find_packages(),
    # include_package_data=True,
    platforms="any",
    install_requires=["bottle"]
)
