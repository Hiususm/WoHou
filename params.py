# %%[Params]
# Indicator for the timeframe you want to
# compute your ratios.
PERLIST = ["year",
           "week",
           "calendaryear",
           "calendarweek"
           ]
# Categories availabe
CATEGORIES = ["TA",  # Teaching Assistance
              "AD",  # Admin (Proctoring and stuff)
              "RA",  # Research Assistance
              "TS",  # Thesis Supervision
              "PR"   # Protected time
              ]
EXCLUDEDCATEGORIES = ["PR" #!! Will not be included in the working hour computations
                     ]
# Dictionary relating the category to
# the title. (For the information printed
# to the console)
CATEGODICT = {"TA": "Teaching Assistance",
              "AD": "Admin (Proctoring etc.)",
              "RA": "Research Assistance",
              "TS": "Thesis Supervision",
              "PR": "Protected Time"}
# Dictionary indicating which category
# has what time requirement
TOTALTIMEDICT = {"TT": 12.6, #total
                 "TA": 5,
                 "AD": 4.6, #less than
                 "RA": 4.6, #less than
                 "TS": 3,
                 "PR": 12.6
                 }
# List to keep the names of the different columns for export
ALLTIMECOLUMNS = ["date", "start", "end", "activity",
                  "category", "diff", "weeksum", "weeksum_total"]
# Information that shoud be exported to the .csv
INFOLIST = ["date", "started", "ended", "activity",
                  "category", "diff", "weeksum", "weeksum_total"]
# Holiday Correction
## 52 - 4 = 48 weeks of work per year
## 48/52 percent of the weeks a year needs to be worked
## ~10 holidays per year 5/7 probability of falling on a 'good' day
## -> expected day off per year /7 -> weeks => /49
HLDYCRR = (48 - 10 / 49 * 5) / 52
