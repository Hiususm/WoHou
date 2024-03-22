# %%[Imports]
from ast import Div
import pandas as pd
import datetime as dt
import numpy as np
import warnings

import params as prms

# %%[Internal Funcs]
def lstdff(cats, excats):
    return list(set(cats).difference(set(excats)))

def cmptdltks(start):
    if isinstance(start, dt.datetime):
        min_week = start.isocalendar().week
    else:
        raise Exception(f"'start' has to be datetime but is {start}")
    return (52 - min_week + 1)

def cntrimport(path, prsdts = 0, skprows =1):
    wh = pd.read_csv(path, parse_dates=[prsdts], skiprows=skprows)
    wh["category"] = wh["category"].map(lambda x: x.strip())
    if not wh["category"].isin(prms.CATEGORIES).all():
        raise Exception("There is a wrong Category\n"
                        f"in line {wh[~wh['category'].isin(prms.CATEGORIES)]}")
    for ind in ["start", "end"]:
        wh[ind] = wh[ind].apply(lambda x: dt.datetime.strptime(x, '%H-%M'))
    wh = ppnddffrncs(wh)
    return wh

def ppndwkhrssm(wh, start):
    wh = wh.assign(week=wh["date"].dt.isocalendar().week)
    wh = wh.assign(year=wh["date"].dt.year)
    grouped = wh.groupby(["week", "year"])
    groupey = wh.groupby("year")
    grouped_ = wh.loc[~wh["category"].isin(prms.EXCLUDEDCATEGORIES),:].groupby(["week", "year"])
    groupey_ = wh.loc[~wh["category"].isin(prms.EXCLUDEDCATEGORIES),:].groupby("year")
    for cat in ([""] + prms.CATEGORIES):
        if cat == "":
            wh.loc[:,"weeksum" + cat] = grouped_["diff" + cat].transform("sum")
            wh.loc[:,"weeksum_total" + cat] = groupey_["diff" + cat].transform("cumsum")
        else:
            wh.loc[:, "weeksum" + cat] = grouped["diff" + cat].transform("sum")
            wh.loc[:, "weeksum_total" + cat] = groupey["diff" + cat].transform("cumsum")
    wh = wh.drop("week", axis=1)
    wh = wh.drop("year", axis=1)
    return wh

def chckclndr(calendar, wh, start):
    if not (isinstance(calendar, str) or
            isinstance(calendar, bool)):
        raise Exception("Calendar has the wrong type.")
    if isinstance(calendar, str):
        if "calendar" in calendar:
            calendar = True
        else:
            calendar = False
    if calendar:
        w = wh.loc[wh["date"].dt.year == start.year, :]
    else:
        cond_ = start <= wh.date
        cond = wh.date <= dt.datetime(start.year + 1,
                                      start.month,
                                      start.day)
        cond = cond & cond_
        w = wh.loc[cond, :]
    return w

def cmptvrgfrwks(wh, start, col="weeksum",
                              format_to_HM=True,
                              per="year"):
    if per not in prms.PERLIST:
        raise Exception(f"'per' has to be one of {prms.PERLIST} but is {per}")
    w = chckclndr(per, wh, start)
    if per == "calendaryear":
        div = cmptdltks(start)
    elif per == "calendarweek":
        div = dt.datetime.now().week + 1
        div -= start.isocalendar().week
    elif per == "year":
        div = 52
    elif per == "week":
        div = dt.datetime.now() - start + dt.timedelta(days=1)
        if div <= dt.timedelta(days=7):
            div = 1
        else:
            div = div.total_seconds() / 604800  # 60^2*24*7
    w = w.assign(week=w["date"].dt.isocalendar().week)
    w = w.assign(year=w["date"].dt.year)
    mean_per_weekyear = w.groupby(["week", "year"])[col].mean()
    sum_per_weeks = mean_per_weekyear.sum()
    aver = sum_per_weeks / (div * prms.HLDYCRR)
    aver = aver.total_seconds()

    if format_to_HM:
        hours = aver // 3600
        aver = aver - (hours * 3600)
        minutes = aver // 60
        seconds = aver - (minutes * 60)
        return hours, minutes, seconds
    else:
        return aver

def chckdffs(wh):
    if any(wh["diff"] < pd.to_timedelta(0)):
        raise Exception("There is an Error in the reported time.\n"
                        " Negative time difference "
                        f"at line: {wh.index[wh['diff'] < pd.to_timedelta(0)][0]}")

    test = wh[["diff", "date"]].copy()
    test["diff"] = pd.to_timedelta(test["diff"], unit="min")
    test = wh.groupby(test["date"].dt.date)["diff"].sum()

    if any(test > pd.to_timedelta(24, unit="h")):
        raise Exception("There is an Error in the reported time.\n"
                        " Day with more than 24h "
                        f"at: {wh.loc[wh['date'] == str(test.index[test > pd.to_timedelta(24,unit='H')][0]),:].index}")
    return None

def ppnddffrncs(wh):
    wh = wh.assign(diff=wh["end"] - wh["start"])
    chckdffs(wh)
    for cat in prms.CATEGORIES:
        wh["diff" + cat] = wh.loc[wh["category"] == cat,
        "end"] - wh.loc[wh["category"] == cat,
        "start"]
    return wh

def prntvrg(wh, start, col, calendar):
    ret = cmptvrgfrwks(wh, start,
                       col=col,
                       format_to_HM=True,
                       per="calendaryear" if calendar else "year")
    ret_str = '{:02}:{:02}:{:02}'.format(int(ret[0]),
                                         int(ret[1]),
                                         int(ret[2]))
    ret_1 = cmptvrgfrwks(wh, start,
                         col=col,
                         format_to_HM=True,
                         per="calendarweek" if calendar else "week")
    ret_1str = '{:02}:{:02}:{:02}'.format(int(ret_1[0]),
                                          int(ret_1[1]),
                                          int(ret_1[2]))
    if col == "weeksum":
        print(f"Average time worked per {'calendar ' if calendar else 'contract '}week in the running ",
              f"year is: {ret_str} of {prms.TOTALTIMEDICT['TT']}h in total.\n",
              f"Time worked per {'calendar ' if calendar else 'contract '}week is on average {ret_1str}.\n\n",
              sep="")
        if (ret[0] + ret[1] / 60) >= prms.TOTALTIMEDICT["TT"]:
            warnings.warn("Total time requirement fulfilled for this year.")
    elif col[7:] in lstdff(prms.CATEGORIES, prms.EXCLUDEDCATEGORIES):
        if (ret[0] + ret[1] / 60) >= prms.TOTALTIMEDICT[col[7:]]:
            warnings.warn(f"'{prms.CATEGODICT[col[7:]]}' time requirement fulfilled for this year.")
        print(f"Average worked for {prms.CATEGODICT[col[7:]]} per {'calendar ' if calendar else 'contract '}week ",
              f"in the running {'calendar ' if calendar else 'contract '}year is: "
              f"{ret_str} of <{prms.TOTALTIMEDICT[col[7:]]}h in total.\n",
              f"Time worked per {'calendar ' if calendar else 'contract '}week for {prms.CATEGODICT[col[7:]]}",
              f" is on average {ret_1str}.\n\n",
              sep="")
    elif col[7:] in prms.EXCLUDEDCATEGORIES:
        print(f"Average {prms.CATEGODICT[col[7:]]} used per {'calendar ' if calendar else 'contract '}week ",
              f"in the running {'calendar ' if calendar else 'contract '}year is: "
              f"{ret_str} of >{prms.TOTALTIMEDICT[col[7:]]}h in total.\n",
              f"{prms.CATEGODICT[col[7:]]} used per {'calendar ' if calendar else 'contract '}week ",
              f"is on average {ret_1str}.\n\n",
              sep="")
    else:
        raise Exception("There is a category which is not classified correctly.")
    return None

