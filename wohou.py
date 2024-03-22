import utils as ut
import params as prms

def read_and_parse(path, start, print_info=True, calendar = False):
    if not isinstance(calendar,bool):
        raise Exception(f"'calendar' needs to be bolean. It is {calendar}.")
    wh = ut.cntrimport(path)
    if print_info:
        print("",
              f"- Start of the contract: {start}",
              "",
              "- All averages are corrected for holidays.",
              f"- Average time worked per {'calendar ' if calendar else 'contract '}week in the running year is the ",
              f"  total worked. I.e., if > {prms.TOTALTIMEDICT['TT']}h there is nothing to do anymore",
              f"- Time worked per {'calendar ' if calendar else 'contract '}week on average shows the hours worked ",
              f"  in the current {'calendar ' if calendar else 'contract '}year. I.e., if all stays as is, at the end ",
              f"  of the {'calendar ' if calendar else 'contract '}year the average time worked for [category] will be equal to this.",
              sep="\n", end="\n\n")
    wh = ut.ppndwkhrssm(wh, start)
    if print_info:
        ut.prntvrg(wh, start, col="weeksum",
                calendar = calendar)
        for cat in prms.CATEGORIES:
            col = "weeksum" + cat
            ut.prntvrg(wh, start, col,
                    calendar = calendar)
    return (wh, calendar)

def export_stats(wh, path, which, month, start, exclude = False):
    wh = ut.chckclndr(wh[1], wh[0], start)
    if which is not None:
        if which not in prms.CATEGORIES:
            raise Exception(f"'which' needs to be one of: {prms.CATEGORIES} or 'None'.")
        print(f"Export only for '{which}'")
        cols = ["date", "start", "end", "activity"] + [i for i in list(wh.columns) if which in i]
        w = wh.loc[wh["category"] == which]
        w = w[cols]
        if isinstance(month, int):
            print(f"Export for month:{month}")
            w = w.loc[wh["date"].apply(lambda x: x.month) == month, :]
            if which is not None:
                w.loc[:, "monthly_sum_" + which] = w["diff" + which].cumsum()
            else:
                w.loc[:, "monthly_sum"] = w.loc[:, "diff"].cumsum()
        elif month == "ALL":
            print("The total time is exported.")
        else:
            raise Exception("'month' needs to be either an int or 'ALL'."
                            f"\nIt is '{month}'")
        for ind in ["start", "end"]:
            w.loc[:, ind] = w.loc[:, ind].dt.time

    else:
        w = wh[prms.ALLTIMECOLUMNS]
        w = w.assign(started = w.loc[:, "start"].dt.time)
        w = w.assign(ended = w.loc[:, "end"].dt.time)
        w = w[prms.INFOLIST]

    if exclude:
        w = w.loc[~w["category"].isin(prms.EXCLUDEDCATEGORIES),:]
        w.to_csv(path, index=False)
    else:
        w.to_csv(path, index=False)
    return None