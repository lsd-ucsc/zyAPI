#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import io
import json
import logging
import pandas
import os

from typing import List, Tuple, Union
from ..Auth.Auth import Auth
from ..Due import Datetime
from ..Host import Host
from .Assignment import Assignment

class Course(object):

	def __init__(
		self,
		host:Host,
		auth: Auth,
		dashboard: 'Dashboard',
		payload: dict
	) -> None:
		super(Course, self).__init__()

		self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

		self.host = host
		self.auth = auth
		self.dashboard = dashboard
		self.payload = payload

		self.id = self.payload['zybook_id']
		self.code = self.payload['zybook_code']
		self.title = self.payload['title']

	def __str__(self) -> str:
		return f'Course(id={self.id}, code={self.code}, title={self.title})'

	def GetRoster(
		self,
		roles: List[str]=['Instructor','TA','Student','Temporary','Dropped']
	) -> dict:
		path = f'/v1/zybook/{self.code}/roster'
		url = f'https://{self.host.GetHost()}{path}'

		params = {
			'zybook_roles': json.dumps(roles,separators=(',', ':')),
		}
		headers = {}

		self.auth.AddAuth(headers)

		response = self.host.session.get(url, headers=headers, params=params)

		return self.host.CheckRespJsonSuccess(response.json())

	def GetAssignments(self) -> dict:
		path = f'/v1/zybook/{self.code}/assignments'
		url = f'https://{self.host.GetHost()}{path}'

		headers = {}

		self.auth.AddAuth(headers)

		response = self.host.session.get(url, headers=headers)

		return self.host.CheckRespJsonSuccess(response.json())

	def OpenAssignment(
		self,
		assignmentID: Union[int, None]=None,
		titleKeyword: Union[str, None]=None,
	) -> Assignment:
		if (
			assignmentID is not None and
			titleKeyword is not None
		):
			raise ValueError(
				'Only one of the search parameters can be specified'
			)

		assignmentList = self.GetAssignments()

		payload = None
		for assignment in assignmentList['assignments']:
			if assignmentID is not None:
				if assignment['assignment_id'] == assignmentID:
					if payload is not None:
						raise ValueError('Assignment ID not unique')
					payload = assignment

			elif titleKeyword is not None:
				if titleKeyword in assignment['title']:
					if payload is not None:
						raise ValueError('Title keyword not unique')
					payload = assignment

		if payload is None:
			raise ValueError('Assignment not found')
		else:
			return Assignment(
				host=self.host,
				auth=self.auth,
				course=self,
				payload=payload
			)

	def ExportReportByDate(
		self,
		date: Datetime.Datetime,
		secIds: List[int],
		includeTimeSpent: bool=False,
	) -> Tuple[str, pandas.DataFrame]:
		path = f'/v1/zybook/{self.code}/activities/export'
		url = f'https://{self.host.GetHost()}{path}'

		headers = {}
		self.auth.AddAuth(headers)

		# pull the report
		params = {
			'time_zone_abbreviation': date.GetTimezoneAbbr(),
			'time_zone_offset': date.GetZyTimezoneOffsetMin(),
			'end_date': date.GetUtcTimestampStr(),
			'sections': json.dumps(secIds,separators=(',', ':')),
			'include_time_spent': includeTimeSpent,
			'combine_activities': False,
			'assignment_id': '',
		}
		resp = self.host.session.get(url, params=params, headers=headers)
		respJson = self.host.CheckRespJsonSuccess(resp.json())

		# wait for the report to be ready
		csvUrl = self.host.ExportWait(auth=self.auth, exportDict=respJson)

		# download the report
		csvResp = self.host.session.get(csvUrl, headers=headers)

		csvStr = csvResp.text
		filename = os.path.basename(csvUrl)

		self.logger.debug(f'Exported report: {filename}')
		expectedTimeSuffix = date.GetReportNameSuffix()
		if expectedTimeSuffix not in filename:
			raise ValueError(f'Expected time suffix not found in filename: {expectedTimeSuffix}')

		df = pandas.read_csv(io.StringIO(csvStr))

		return filename, df

