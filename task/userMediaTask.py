'''
Author: mengzonefire
Date: 2021-09-21 09:19:02
LastEditTime: 2022-03-03 13:31:27
LastEditors: mengzonefire
Description: 推主推文批量爬取任务类
'''
from task.baseTask import Task
from common.logger import write_log
from common.tools import parseData
from common.text import *
from common.const import *


class UserMediaTask(Task):
    userId = ''

    def __init__(self, userName, userId):
        self.userName = userName
        self.userId = userId
        self.savePath = os.path.join(getContext('dl_path'), userName)

    def getDataList(self, cursor=''):
        cursorPar = cursor and '"cursor":"{}",'.format(cursor)
        response = getContext('globalSession').post(
            userMediaApi, params={'variables': userMediaApiPar.format(self.userId, twtCount, cursorPar)}, proxies=getContext(
                'proxy'), headers=getContext('headers'))

        if response.status_code != 200:
            print(http_warning.format('UserMediaTask.getDataList',
                                      response.status_code, issue_page))
            return

        pageContent = response.text
        # debug
        write_log(self.userId, pageContent)
        if 'UserUnavailable' in pageContent:
            print(user_unavailable_warning)
            return

        twtIdList = p_twt_id.findall(pageContent)
        if not twtIdList:
            return
        contentList = pageContent.split('"entryId":"tweet-')
        contentDict = dict(zip(twtIdList, contentList[1:]))
        for twtId in contentDict:
            picList, gifList, vidList, textList = parseData(
                contentDict[twtId].split('extended_entities')[-1], twtId)
            self.dataList['picList'] = dict(
                self.dataList['picList'], **picList)
            self.dataList['gifList'] = dict(
                self.dataList['gifList'], **gifList)
            self.dataList['vidList'] = dict(
                self.dataList['vidList'], **vidList)
            self.dataList['textList'] = dict(
                self.dataList['textList'], **textList)
        cursor = p_cursor.findall(
            pageContent.split('TimelineTimelineCursor')[-1])
        if cursor:
            self.getDataList(cursor[0])
