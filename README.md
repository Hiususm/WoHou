# WoHou

Includes two main functions.

1) read_and_parse: reads a formatted csv. Conducts some basic checks and prints information to the console. Returns information on the time worked per week, up to now and over the course of the (contract) year.

2) export_stats: Exports the desired details to a CSV file.

## Notes

### Adjustments
Note that all parameter definitions are contained in the params file. Adjustments of categories can be made there.

### Holiday Correction
The work time is adjusted for holidays in the following way: 4 weeks of holidays mean that in total there are 48 weeks to work. From these weeks ~10 days are holidays, which land with a probability of 5/7 on a 'good' day. Computed time worked is thus multiplied by the factor: (48-10/49*5)/52. There might be better ways...

### Protected Time
The computations exclude the entries in the category 'PR' (Protected Time). This information is excluded in the exported file if the 'exclude' flag is set to true.

### Warnings
read_and_parse will print a warning if you've worked too much already.



```python
import datetime as dt # To set the starting date of the contract
import wohou as wo
```


```python
start = dt.datetime(2023, 9, 1) # Contract started
month = "ALL" # Should one month be computed
which = None # Any special occupation ? e.g. "TA"
import_path = r"Working hours test.csv"
export_path = r"worktime_test.csv"
```


```python
#Prepares the data and prints to console
wh = wo.read_and_parse(import_path, 
                       start = start, 
                       print_info = True, # Print to console ? 
                       calendar = False) # Calendar year or contract year ?
```

    
    - Start of the contract: 2023-09-01 00:00:00
    
    - All averages are corrected for holidays.
    - Average time worked per contract week in the running year is the 
      total worked. I.e., if > 12.6h there is nothing to do anymore
    - Time worked per contract week on average shows the hours worked 
      in the current contract year. I.e., if all stays as is, at the end 
      of the contract year the average time worked for [category] will be equal to this.
    
    Average time worked per contract week in the running year is: 01:03:43 of 12.6h in total.
    Time worked per contract week is on average 01:53:22.
    
    
    Average worked for Teaching Assistance per contract week in the running contract year is: 00:26:49 of <5h in total.
    Time worked per contract week for Teaching Assistance is on average 00:47:42.
    
    
    Average worked for Admin (Proctoring etc.) per contract week in the running contract year is: 00:14:20 of <4.6h in total.
    Time worked per contract week for Admin (Proctoring etc.) is on average 00:25:31.
    
    
    Average worked for Research Assistance per contract week in the running contract year is: 00:02:37 of <4.6h in total.
    Time worked per contract week for Research Assistance is on average 00:04:39.
    
    
    Average worked for Thesis Supervision per contract week in the running contract year is: 00:19:56 of <3h in total.
    Time worked per contract week for Thesis Supervision is on average 00:35:28.
    
    
    Average Protected Time used per contract week in the running contract year is: 00:19:56 of >12.6h in total.
    Protected Time used per contract week is on average 00:35:28.
    
    
    


```python
#Exports
wo.export_stats(wh = wh,
                path = export_path,
                which = which,
                month = month,
                start = start,
                exclude = False)
```
