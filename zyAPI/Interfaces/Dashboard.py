#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from typing import Union
from ..Auth.Auth import Auth
from ..Host import Host
from .Course import Course


class Dashboard(object):

	def __init__(self, host:Host, auth: Auth, uid: int) -> None:
		super(Dashboard, self).__init__()

		self.host = host
		self.auth = auth
		self.uid = uid

	def __str__(self) -> str:
		return f'Dashboard(uid={self.uid})'

	def GetUserInfo(self) -> dict:
		path = f'/v1/user/{self.uid}'
		url = f'https://{self.host.GetHost()}{path}'

		headers = {}

		self.auth.AddAuth(headers)

		response = self.host.session.get(url, headers=headers)

		return response.json()

	def GetCourseList(self) -> dict:
		path = f'/v1/user/{self.uid}/items'
		url = f'https://{self.host.GetHost()}{path}'

		headers = {}

		self.auth.AddAuth(headers)

		response = self.host.session.get(url, headers=headers)

		return response.json()

	def OpenCourse(
		self,
		courseID: Union[int, None]=None,
		courseCode: Union[str, None]=None,
		titleKeyword: Union[str, None]=None,
	) -> Course:
		if (
			courseID is not None and
			courseCode is not None and
			titleKeyword is not None
		):
			raise ValueError(
				'Only one of the search parameters can be specified'
			)

		courseList = self.host.CheckRespJsonSuccess(self.GetCourseList())

		payload = None
		for course in courseList['items']['zybooks']:
			if courseID is not None:
				if course['zybook_id'] == courseID:
					if payload is not None:
						raise ValueError('Course ID not unique')
					payload = course

			elif courseCode is not None:
				if course['zybook_code'] == courseCode:
					if payload is not None:
						raise ValueError('Course code not unique')
					payload = course

			elif titleKeyword is not None:
				if titleKeyword in course['title']:
					if payload is not None:
						raise ValueError('Title keyword not unique')
					payload = course

		if payload is None:
			raise ValueError('Course not found')
		else:
			return Course(
				host=self.host,
				auth=self.auth,
				dashboard=self,
				payload=payload
			)
