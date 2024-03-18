#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###



#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import numpy
import re
import pandas

from typing import Callable, List, Tuple
from ..Auth.Auth import Auth
from ..Host import Host
from ..Due import Due
from ..Due import Datetime


class Section(object):

	def __init__(self, payload: dict) -> None:
		super(Section, self).__init__()

		self.payload = payload

		self.id = self.payload['canonical_section_id']
		self.title = self.payload['title']
		self.totalPts = self.payload['total_points']
		self.incPart = self.payload['include_participations']
		self.incChal = self.payload['include_challenges']
		self.incLabs = self.payload['include_labs']

	def __str__(self) -> str:
		return f'Section(id={self.id}, title={self.title}, totalPts={self.totalPts})'

	def CalcTotalPtsByColInfo(self, colInfo: dict) -> float:
		total = 0.0
		if self.incPart:
			total += colInfo['pts']['partTotal']
		if self.incChal:
			total += colInfo['pts']['chalTotal']
		if self.incLabs:
			total += colInfo['pts']['labsTotal']
		return total

	def AssertTotalsPtsWithColInfo(self, colInfo: dict) -> None:
		total = self.CalcTotalPtsByColInfo(colInfo)
		assert float(self.totalPts) == total, 'Total points mismatch'


class Sections(object):

	def __init__(self, payloads: List[dict]) -> None:
		super(Sections, self).__init__()

		self.sections = [Section(payload) for payload in payloads]

	def __str__(self) -> str:
		return f'Sections({self.GetIdList()})'

	def GetIdList(self) -> List[int]:
		return [section.id for section in self.sections]

	def GetTotalPtsBySecId(self, secId: int) -> float:
		for section in self.sections:
			if section.id == secId:
				return section.totalPts
		raise ValueError(f'Section id {secId} not found')


class Assignment(object):

	def __init__(
		self,
		host:Host,
		auth: Auth,
		course: 'Course',
		payload: dict,
	) -> None:
		super(Assignment, self).__init__()

		self.host = host
		self.auth = auth
		self.course = course
		self.payload = payload

		self.id = self.payload['assignment_id']
		self.creatorId = self.payload['creator_user_id']
		self.title = self.payload['title']
		self.visible = self.payload['visible'] == 1
		self.sections = Sections(self.payload['sections'])

	def __str__(self) -> str:
		return f'Assignment(id={self.id}, title={self.title}, visible={self.visible})'

	@classmethod
	def ParseReportHeader(cls, headers: List[str]) -> dict:
		'''
		Examples:
		```
		[
			'Total (52)',
			'Participation total (36)',
			'Challenge total (16)',
			'Lab total (0)',
			'1.1 - Participation (21)',
			'1.2 - Participation (15)',
			'1.1 - Challenge (3)',
			'1.2 - Challenge (13)',
			'1.1 - Lab (0)',
			'1.2 - Lab (0)'
		]
		```
		'''
		REGEX_LNAME = r'^\s*[Ll]ast\s+[Nn]ame\s*$'
		REGEX_FNAME = r'^\s*[Ff]irst\s+[Nn]ame\s*$'
		REGEX_PRI_EMAIL = r'^\s*[Pp]rimary\s+[Ee]mail\s*$'
		REGEX_SCH_EMAIL = r'^\s*[Ss]chool\s+[Ee]mail\s*$'
		REGEX_TOTAL = r'^\s*[Tt]otal\s*\((\d+)\)\s*$'
		REGEX_PART_TOTAL = r'^\s*[Pp]articipation\s+[Tt]otal\s*\((\d+)\)\s*$'
		REGEX_CHAL_TOTAL = r'^\s*[Cc]hallenge\s+[Tt]otal\s*\((\d+)\)\s*$'
		REGEX_LABS_TOTAL = r'^\s*[Ll]ab\s+[Tt]otal\s*\((\d+)\)\s*$'
		REGEX_PART = r'^\s*([0-9.]+)\s*-\s*[Pp]articipation\s*\((\d+)\)\s*$'
		REGEX_CHAL = r'^\s*([0-9.]+)\s*-\s*[Cc]hallenge\s*\((\d+)\)\s*$'
		REGEX_LABS = r'^\s*([0-9.]+)\s*-\s*[Ll]ab\s*\((\d+)\)\s*$'

		info = {
			'idx': {
				'part': [],
				'chal': [],
				'labs': [],
			},
			'pts': {
				'part': [],
				'chal': [],
				'labs': [],
			},
		}
		for i in range(len(headers)):
			if match := re.match(REGEX_LNAME, headers[i]):
				if 'lname' in info['idx']:
					raise RuntimeError('Duplicate last name column')
				info['idx']['lname'] = i
			elif match := re.match(REGEX_FNAME, headers[i]):
				if 'fname' in info['idx']:
					raise RuntimeError('Duplicate first name column')
				info['idx']['fname'] = i
			elif match := re.match(REGEX_SCH_EMAIL, headers[i]):
				if 'schEmail' in info['idx']:
					raise RuntimeError('Duplicate school email column')
				info['idx']['schEmail'] = i
			elif match := re.match(REGEX_PRI_EMAIL, headers[i]):
				if 'priEmail' in info['idx']:
					raise RuntimeError('Duplicate primary email column')
				info['idx']['priEmail'] = i

			elif match := re.match(REGEX_TOTAL, headers[i]):
				if 'total' in info['idx']:
					raise RuntimeError('Duplicate total column')
				info['idx']['total'] = i
				info['pts']['total'] = float(match.group(1))

			elif match := re.match(REGEX_PART_TOTAL, headers[i]):
				if 'partTotal' in info['idx']:
					raise RuntimeError('Duplicate participation total column')
				info['idx']['partTotal'] = i
				info['pts']['partTotal'] = float(match.group(1))
			elif match := re.match(REGEX_CHAL_TOTAL, headers[i]):
				if 'chalTotal' in info['idx']:
					raise RuntimeError('Duplicate challenge total column')
				info['idx']['chalTotal'] = i
				info['pts']['chalTotal'] = float(match.group(1))
			elif match := re.match(REGEX_LABS_TOTAL, headers[i]):
				if 'labsTotal' in info['idx']:
					raise RuntimeError('Duplicate lab total column')
				info['idx']['labsTotal'] = i
				info['pts']['labsTotal'] = float(match.group(1))

			elif match := re.match(REGEX_PART, headers[i]):
				info['idx']['part'].append(i)
				info['pts']['part'].append(float(match.group(2)))
			elif match := re.match(REGEX_CHAL, headers[i]):
				info['idx']['chal'].append(i)
				info['pts']['chal'].append(float(match.group(2)))
			elif match := re.match(REGEX_LABS, headers[i]):
				info['idx']['labs'].append(i)
				info['pts']['labs'].append(float(match.group(2)))

		# print(info)

		# validate
		if 'lname' not in info['idx']:
			raise RuntimeError('Missing last name column')
		if 'fname' not in info['idx']:
			raise RuntimeError('Missing first name column')
		if 'priEmail' not in info['idx']:
			raise RuntimeError('Missing primary email column')
		if 'schEmail' not in info['idx']:
			raise RuntimeError('Missing school email column')

		if 'total' not in info['idx']:
			raise RuntimeError('Missing total column')
		if 'partTotal' not in info['idx']:
			raise RuntimeError('Missing participation total column')
		if 'chalTotal' not in info['idx']:
			raise RuntimeError('Missing challenge total column')
		if 'labsTotal' not in info['idx']:
			raise RuntimeError('Missing lab total column')

		if (
			(
				info['pts']['partTotal'] +
				info['pts']['chalTotal'] +
				info['pts']['labsTotal']
			) !=
			info['pts']['total']
		):
			raise RuntimeError('Total mismatch')

		if sum(info['pts']['part']) != info['pts']['partTotal']:
			raise RuntimeError('Participation total mismatch')
		if sum(info['pts']['chal']) != info['pts']['chalTotal']:
			raise RuntimeError('Challenge total mismatch')
		if sum(info['pts']['labs']) != info['pts']['labsTotal']:
			raise RuntimeError('Lab total mismatch')

		return info

	def _CourseExportReportByDate(
		self,
		date: Datetime.Datetime,
		secIds: List[int],
		includeTimeSpent: bool=False,
	) -> Tuple[str, pandas.DataFrame]:
		return self.course.ExportReportByDate(
			date=date,
			secIds=secIds,
			includeTimeSpent=includeTimeSpent,
		)

	def ExportReportByDate(
		self,
		date: Datetime.Datetime,
		includeTimeSpent: bool=False,
	) -> Tuple[str, pandas.DataFrame]:
		dfs = {}
		for sec in self.sections.sections:
			secId = sec.id

			filename, df = self._CourseExportReportByDate(
				date=date,
				secIds=[secId],
				includeTimeSpent=includeTimeSpent,
			)

			# rename columns and drop unwanted columns
			unwantedCols = []
			colInfo = self.ParseReportHeader(list(df.columns))
			for i in range(len(df.columns)):
				# names, emails
				if i == colInfo['idx']['lname']:
					df.columns.values[i] = 'last_name'
				elif i == colInfo['idx']['fname']:
					df.columns.values[i] = 'first_name'
				elif i == colInfo['idx']['priEmail']:
					df.columns.values[i] = 'primary_email'
				elif i == colInfo['idx']['schEmail']:
					df.columns.values[i] = 'school_email'

				# total points
				elif i == colInfo['idx']['total']:
					df.columns.values[i] = f'{secId}'
				elif (i == colInfo['idx']['partTotal']) and sec.incPart:
					df.columns.values[i] = f'{secId}.part'
				elif (i == colInfo['idx']['chalTotal']) and sec.incChal:
					df.columns.values[i] = f'{secId}.chal'
				elif (i == colInfo['idx']['labsTotal']) and sec.incLabs:
					df.columns.values[i] = f'{secId}.labs'
				else:
					# give unwanted columns a unique name
					df.columns.values[i] = f'unwanted_{i}'
					unwantedCols.append(i)

			df.drop(columns=df.columns[unwantedCols], inplace=True)

			# fillna with 0.0
			df[f'{secId}'] = df[f'{secId}'].fillna(0.0)
			if sec.incPart:
				df[f'{secId}.part'] = df[f'{secId}.part'].fillna(0.0)
			if sec.incChal:
				df[f'{secId}.chal'] = df[f'{secId}.chal'].fillna(0.0)
			if sec.incLabs:
				df[f'{secId}.labs'] = df[f'{secId}.labs'].fillna(0.0)

			# make primary_email as the key column
			df.set_index('primary_email', inplace=True)

			# validate the total points
			sec.AssertTotalsPtsWithColInfo(colInfo)

			# calculate points by col_values(i.e., percent) x total points
			df[f'{secId}'] = 0.0
			if sec.incPart:
				df[f'{secId}.part'] *= colInfo['pts']['partTotal']
				df[f'{secId}.part'] /= 100
				# add to total
				df[f'{secId}'] += df[f'{secId}.part']
			if sec.incChal:
				df[f'{secId}.chal'] *= colInfo['pts']['chalTotal']
				df[f'{secId}.chal'] /= 100
				# add to total
				df[f'{secId}'] += df[f'{secId}.chal']
			if sec.incLabs:
				df[f'{secId}.labs'] *= colInfo['pts']['labsTotal']
				df[f'{secId}.labs'] /= 100
				# add to total
				df[f'{secId}'] += df[f'{secId}.labs']

			# save the dataframe
			dfs[secId] = df

		# merge the dataframes
		if len(dfs) == 0:
			raise RuntimeError('No dataframes')

		dfsecIds = list(dfs.keys())
		df = dfs[dfsecIds[0]]
		dfRowCnt = len(df)

		for i in range(1, len(dfsecIds)):
			df = pandas.merge(
				df, dfs[dfsecIds[i]],
				how='inner',
				on='primary_email',
				suffixes=('', f'_{dfsecIds[i]}'),
			)

			# make sure merged dataframe doesn't lost any rows
			if len(df) < dfRowCnt:
				raise RuntimeError('Merged dataframe lost rows')
			dfRowCnt = len(df)

			# remove duplicate columns
			df.drop(columns=[f'last_name_{dfsecIds[i]}'], inplace=True)
			df.drop(columns=[f'first_name_{dfsecIds[i]}'], inplace=True)
			df.drop(columns=[f'school_email_{dfsecIds[i]}'], inplace=True)

		# create total column
		df['total'] = 0.0
		df['total_percent'] = 0.0
		asgTotal = 0.0
		for secId in dfsecIds:
			df['total'] += df[f'{secId}']
			asgTotal += self.sections.GetTotalPtsBySecId(secId)

		df['total_percent'] += (df['total'] * 100) / asgTotal

		return filename, df

	def ExportReportWithDue(
		self,
		due: Due.Due,
		includeTimeSpent: bool=False,
	) -> Tuple[str, pandas.DataFrame]:
		filename, df = self.ExportReportByDate(
			date=due.dueDate,
			includeTimeSpent=includeTimeSpent
		)

		due.Apply2Pd(
			df=df,
			totalColName='total',
			destColName='total_due',
		)

		due.Apply2Pd(
			df=df,
			totalColName='total_percent',
			destColName='total_percent_due',
		)

		return filename, df

	def ExportReportWithDues(
		self,
		dues: List[Due.Due],
		includeTimeSpent: bool=False,
		mergeOps: Callable = numpy.maximum,
	) -> Tuple[str, pandas.DataFrame]:
		if len(dues) == 0:
			raise ValueError('No dues specified')

		filename, df = self.ExportReportWithDue(
			due=dues[0],
			includeTimeSpent=includeTimeSpent,
		)

		for dIdx in range(1, len(dues)):
			_, dfNext = self.ExportReportWithDue(
				due=dues[dIdx],
				includeTimeSpent=includeTimeSpent,
			)
			for i in range(len(df.columns)):
				colName = df.columns.values[i]
				for sec in self.sections.sections:
					if f'{sec.id}' in colName:
						df[colName] = mergeOps(df[colName], dfNext[colName])

				if 'total' in colName:
					df[colName] = mergeOps(df[colName], dfNext[colName])
					#print(df[colName].keys())

		return filename, df

