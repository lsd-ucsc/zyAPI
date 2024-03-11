#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import json
import logging
import time
import requests

from .Auth.Auth import Auth

class Host(object):

	LOGGER = logging.getLogger(f'{__name__}')

	def __init__(self, host: str) -> None:
		super(Host, self).__init__()

		self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

		self.host = host
		self.session = requests.Session()
		self.exportSession = requests.Session()

	def __str__(self) -> str:
		return f'Host(host={self.host})'

	def GetHost(self) -> str:
		return self.host

	@classmethod
	def CheckRespJsonSuccess(cls, resp: dict) -> dict:
		if not resp['success']:
			err = resp['error']
			errStr = json.dumps(err, indent='\t')
			raise RuntimeError(f'API call failed: {errStr}')

		return resp

	def ExportWait(
		self,
		auth: Auth,
		exportDict: dict,
		pollInterval: float=1.0,
		pollTimes: int=50
	) -> str:
		if not exportDict['success']:
			raise RuntimeError('Export failed')

		loc = exportDict['location']

		headers = {}
		auth.AddAuth(headers)

		for _ in range(pollTimes):
			resp = self.exportSession.get(loc, headers=headers)
			statusDict = resp.json()

			if not statusDict['success']:
				statusDictStr = json.dumps(statusDict, indent='\t')
				self.logger.error(f'Export status failed:\n{statusDictStr}')
				raise RuntimeError('Export status failed')

			if statusDict['state'] == 'PENDING':
				self.logger.debug('Export pending')
				time.sleep(pollInterval)
			elif statusDict['state'] == 'SUCCESS':
				self.logger.debug('Export success')
				url = statusDict['url']
				return url
			else:
				state = statusDict['state']
				raise RuntimeError(f'Export failed with state: {state}')

		raise RuntimeError('Status polling exceeded maximum attempts')

