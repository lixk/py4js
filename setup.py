from setuptools import setup

setup(
    name="py4js",
    version="0.0.1",
    keywords=("pip", "py4js"),
    description="a fast and simple micro-framework for small web applications",
#     long_description="""py4js is a fast and simple micro-framework for small web applications. Its goal is to enable you to develop
# web applications in a simple and understandable way.
#
# With it, you don't need to know the HTTP protocol, or how Python communicates with JavaScript. You can use Python functions in JavaScript just like native JavaScript functions.
# """,
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
