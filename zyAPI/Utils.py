#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import pandas
import re


class Report(object):

	def __init__(self) -> None:
		super(Report, self).__init__()

	@classmethod
	def MergeEmailCols(
		cls,
		df: pandas.DataFrame,
		preferredEmailFormat: str
	) -> None:
		'''
		Merge primary_email and school_email columns into an email column, by
		checking if the primary_email is preferredEmailFormat,
		if not, check if the school_email is preferredEmailFormat,
		otherwise, keep the primary_email.
		'''

		# iterate through the rows
		for index, row in df.iterrows():
			# check if the index(primary_email) is preferredEmailFormat
			if re.search(preferredEmailFormat, index):
				# if yes, keep index(primary_email) and continue
				df.at[index, 'email'] = index
			# check if the school_email is NaN
			elif pandas.isna(row['school_email']):
				# if school_email is NaN, keep index(primary_email) and continue
				df.at[index, 'email'] = index
			# check if the school_email is preferredEmailFormat
			elif re.search(preferredEmailFormat, row['school_email']):
				# if yes, replace index(primary_email) with school_email
				df.at[index, 'email'] = row['school_email']

		# drop school_email column
		df.drop(columns=['school_email'], inplace=True)

		# drop index(primary_email) column
		df.reset_index(drop=True, inplace=True)

		# make the email column the index
		df.set_index('email', inplace=True)

		# make sure there is no duplicate email
		duplicateEmails = df.index.duplicated()
		if True in duplicateEmails:
			# get the duplicate emails
			duplicateEmails = df.loc[duplicateEmails, 'email']
			# raise an error
			raise ValueError(f'Duplicate email after merging the columns: {duplicateEmails}')

	@classmethod
	def ReplaceEmailsByMap(
		cls,
		df: pandas.DataFrame,
		emailMap: dict,
	) -> None:
		'''
		Replace emails in the dataframe by the emailMap.
		'''

		df.reset_index(drop=False, inplace=True)
		df.replace({'email': emailMap}, inplace=True)
		df.set_index('email', inplace=True)

		# make sure there is no duplicate email
		duplicateEmails = df.index.duplicated()
		if True in duplicateEmails:
			# get the duplicate emails
			duplicateEmails = df.loc[duplicateEmails, 'email']
			raise ValueError(f'Duplicate email after replacing emails by map: {duplicateEmails}')

	@classmethod
	def CheckEmailsFormat(
		cls,
		df: pandas.DataFrame,
		emailFormat: str,
	) -> None:
		'''
		Check if the emails in the dataframe match the emailFormat.
		'''
		invliadEmails = []
		for index, row in df.iterrows():
			if not re.search(emailFormat, index):
				invliadEmails.append({
					'email': index,
					'name': f'{row["first_name"]} {row["last_name"]}'
				})

		if len(invliadEmails) > 0:
			raise ValueError(f'Invalid emails: {invliadEmails}')

