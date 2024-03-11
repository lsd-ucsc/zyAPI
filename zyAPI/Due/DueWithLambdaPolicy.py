#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import pandas

from typing import Callable
from .Datetime import Datetime
from .Due import Due


class DueWithLambdaPolicy(Due):

	def __init__(
		self,
		dueDate: Datetime,
		policy: Callable[[float], float] = lambda x: x,
	) -> None:
		super(DueWithLambdaPolicy, self).__init__(dueDate=dueDate)

		self.policy = policy

	def Apply2Pd(
		self,
		df: pandas.DataFrame,
		totalColName: str,
		destColName: str,
	) -> pandas.DataFrame:
		df[destColName] = df[totalColName].apply(self.policy)
		return df

