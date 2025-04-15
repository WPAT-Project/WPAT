from setuptools import setup, find_packages

setup(
    name="wpat",
    version="1.9",
    author="Santitub",
    author_email="tu@email.com",
    description="WPAT (WP Audit Toolkit) es una herramienta de auditoría de seguridad para WordPress que detecta vulnerabilidades comunes y expone riesgos de manera eficiente.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Santitub/WPAT",
    packages=find_packages(include=["wpat", "wpat.*"]),
    install_requires=[
        'colorama',
        'requests',
        'beautifulsoup4',
        'tqdm'
    ],
    entry_points={
        'console_scripts': [
            'wpat=wpat.main:main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Information Technology',
        'Topic :: Security',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.6',
    include_package_data=True,
    zip_safe=False,
    keywords='wordpress security audit toolkit',
    project_urls={
        'Documentation': 'https://github.com/Santitub/wpat/wiki',
        'Source': 'https://github.com/Santitub/wpat',
        'Tracker': 'https://github.com/Santitub/wpat/issues',
    }
)
