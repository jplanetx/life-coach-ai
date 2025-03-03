from setuptools import setup, find_packages

setup(
    name="life-coach-ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'langchain>=0.0.350',
        'openai>=1.0.0',
        'python-dotenv>=1.0.0'
    ]
)