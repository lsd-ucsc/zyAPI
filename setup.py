#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###



from setuptools import setup
from setuptools import find_packages

import zyAPI._Meta


setup(
	name        = zyAPI._Meta.PKG_NAME,
	version     = zyAPI._Meta.__version__,
	packages    = find_packages(where='.', exclude=['setup.py']),
	url         = 'https://github.com/lsd-ucsc/zyAPI',
	license     = zyAPI._Meta.PKG_LICENSE,
	author      = zyAPI._Meta.PKG_AUTHOR,
	description = zyAPI._Meta.PKG_DESCRIPTION,
	entry_points= {
		'console_scripts': [
			'zyAPI=zyAPI.__main__:main',
		]
	},
	install_requires=[
		'requests==2.31.0',
		'pandas==2.2.1',
		'numpy==1.26.4',
	],
)
