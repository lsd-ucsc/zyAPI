#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import pandas

from .Datetime import Datetime


class Due(object):

	def __init__(
		self,
		dueDate: Datetime,
	) -> None:
		super(Due, self).__init__()

		self.dueDate = dueDate

	def Apply2Pd(
		self,
		df: pandas.DataFrame,
		totalColName: str,
	) -> pandas.DataFrame:
		raise NotImplementedError('Apply2Pd not implemented')

