#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import datetime

try:
	import zoneinfo
except ImportError:
	from backports import zoneinfo


class Datetime(object):

	def __init__(self, datetime: datetime.datetime) -> None:
		super(Datetime, self).__init__()

		self.datetime = datetime

	def GetTimestampStr(self) -> str:
		# format: '2024-03-08T07:59:59.999Z'
		return self.datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

	def GetUtcTimestampStr(self) -> str:
		utcDatetime = self.datetime.astimezone(zoneinfo.ZoneInfo('UTC'))
		return utcDatetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

	def GetTimezoneAbbr(self) -> str:
		return self.datetime.strftime('%Z')

	def GetTimezoneOffsetMin(self) -> int:
		return int(self.datetime.utcoffset().total_seconds()) // 60

	def GetZyTimezoneOffsetMin(self) -> int:
		return -1 * self.GetTimezoneOffsetMin()

	def GetReportNameSuffix(self) -> str:
		# report_2024-01-20_0759_PST
		return self.datetime.strftime('%Y-%m-%d_%H%M_%Z')

	def __str__(self) -> str:
		return (
			f'{self.__class__.__name__}' +
			f'(ts={self.GetTimestampStr()}, ' +
			f'tz={self.GetTimezoneAbbr()}, ' +
			f'offset={self.GetTimezoneOffsetMin()})'
		)

	@classmethod
	def FromComponents(
		cls,
		year: int,
		month: int,
		day: int,
		hour: int,
		minute: int,
		second: int,
		tz: str,
	) -> 'Datetime':
		tzInfo = zoneinfo.ZoneInfo(tz)

		return cls(
			datetime=datetime.datetime(
				year=year,
				month=month,
				day=day,
				hour=hour,
				minute=minute,
				second=second,
				tzinfo=tzInfo
			)
		)

