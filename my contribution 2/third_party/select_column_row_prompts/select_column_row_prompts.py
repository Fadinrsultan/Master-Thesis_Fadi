# MIT License
# 
# Copyright (c) 2022 Alibaba Research
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.


select_column_demo = """Use f_col() api to filter out useless columns in the table according to informations in the statement and the table.

/*
{
  "table_caption": "south wales derby",
  "columns": ["competition", "total matches", "cardiff win", "draw", "swansea win"],
  "table_column_priority": [
    ["competition", "league", "fa cup", "league cup"],
    ["total matches", "55", "2", "5"],
    ["cardiff win", "19", "0", "2"],
    ["draw", "16", "27", "0"],
    ["swansea win", "20", "2", "3"]
  ]
}
*/
statement : there are no cardiff wins that have a draw greater than 27.
similar words link to columns :
no cardiff wins -> cardiff win
a draw -> draw
column value link to columns :
27 -> draw
semantic sentence link to columns :
None
The answer is : f_col([cardiff win, draw])

/*
{
  "table_caption": "gambrinus liga",
  "columns": ["season", "champions", "runner - up", "third place", "top goalscorer", "club"],
  "table_column_priority": [
    ["season", "1993 - 94", "1994 - 95", "1995 - 96"],
    ["champions", "sparta prague (1)", "sparta prague (2)", "slavia prague (1)"],
    ["runner - up", "slavia prague", "slavia prague", "sigma olomouc"],
    ["third place", "ban\u00edk ostrava", "fc brno", "baumit jablonec"],
    ["top goalscorer", "horst siegl (20)", "radek drulák (15)", "radek drulák (22)"],
    ["club", "sparta prague", "drnovice", "drnovice"]
  ]
}
*/
statement : the top goal scorer for the season 2010 - 2011 was david lafata.
similar words link to columns :
season 2010 - 2011 -> season
the top goal scorer -> top goalscorer
column value link to columns :
2010 - 2011 -> season
semantic sentence link to columns :
the top goal scorer for ... was david lafata -> top goalscorer
The answer is : f_col([season, top goalscorer])

/*
{
  "table_caption": "head of the river (queensland)",
  "columns": ["crew", "open 1st viii", "senior 2nd viii", "senior 3rd viii", "senior iv", "year 12 single scull", "year 11 single scull"],
  "table_column_priority": [
    ["crew", "2009", "2010", "2011"],
    ["open 1st viii", "stm", "splc", "stm"],
    ["senior 2nd viii", "sta", "som", "stu"],
    ["senior 3rd viii", "sta", "som", "stu"],
    ["senior iv", "som", "sth", "sta"],
    ["year 12 single scull", "stm", "splc", "stm"],
    ["year 11 single scull", "splc", "splc", "splc"]
  ]
}
*/
statement : the crew that had a senior 2nd viii of som and senior iv of stm was that of 2013.
similar words link to columns :
the crew -> crew
a senior 2nd viii of som -> senior 2nd viii
senior iv of stm -> senior iv
column value link to columns :
som -> senior 2nd viii
stm -> senior iv
semantic sentence link to columns :
None
The answer is : f_col([crew, senior 2nd viii, senior iv])

/*
{
  "table_caption": "2007 - 08 boston celtics season",
  "columns": ["game", "date", "team", "score", "high points", "high rebounds", "high assists", "location attendance", "record"],
  "table_column_priority": [
    ["game", "74", "75", "76"],
    ["date", "april 1", "april 2", "april 5"],
    ["team", "chicago", "indiana", "charlotte"],
    ["score", "106 - 92", "92 - 77", "101 - 78"],
    ["high points", "allen (22)", "garnett (20)", "powe (22)"],
    ["high rebounds", "perkins (9)", "garnett (11)", "powe (9)"],
    ["high assists", "rondo (10)", "rondo (6)", "rondo (5)"],
    ["location attendance", "united center 22225", "td banknorth garden 18624", "charlotte bobcats arena 19403"],
    ["record", "59 - 15", "60 - 15", "61 - 15"]
  ]
}
*/
statement : in game 74 against chicago , perkins had the most rebounds (9) and allen had the most points (22).
similar words link to columns :
the most rebounds -> high rebounds
the most points -> high points
in game 74 -> game
column value link to columns :
74 -> game
semantic sentence link to columns :
2007 - 08 boston celtics season in game 74 against chicago -> team
perkins had the most rebounds -> high rebounds
allen had the most points -> high points
The answer is : f_col([game, team, high points, high rebounds])

/*
{
  "table_caption": "dan hardy",
  "columns": ["res", "record", "opponent", "method", "event", "round", "time", "location"],
  "table_column_priority": [
    ["res", "win", "win", "loss"],
    ["record", "25 - 10 (1)", "24 - 10 (1)", "23 - 10 (1)"],
    ["opponent", "amir sadollah", "duane ludwig", "chris lytle"],
    ["method", "decision (unanimous)", "ko (punch and elbows)", "submission (guillotine choke)"],
    ["event", "ufc on fuel tv : struve vs miocic", "ufc 146", "ufc live : hardy vs lytle"],
    ["round", "3", "1", "5"],
    ["time", "5:00", "3:51", "4:16"],
    ["location", "nottingham , england", "las vegas , nevada , united states", "milwaukee , wisconsin , united states"]
  ]
}
*/
statement : the record of the match was a 10 - 3 (1) score , resulting in a win in round 5 with a time of 5:00 minutes.
similar words link to columns :
the record of the match was a 10 - 3 (1) score -> record
the record -> record
in round -> round
a time -> time
column value link to columns :
10 - 3 (1) -> record
5 -> round
5:00 minutes -> time
semantic sentence link to columns :
resulting in a win -> res
The answer is : f_col([res, record, round, time])

/*
{
  "table_caption": "list of largest airlines in central america & the caribbean",
  "columns": ["rank", "airline", "country", "fleet size", "remarks"],
  "table_column_priority": [
    ["rank", "1", "2", "3"],
    ["airline", "caribbean airlines", "liat", "cubana de aviaci\u00e3 cubicn"],
    ["country", "trinidad and tobago", "antigua and barbuda", "cuba"],
    ["fleet size", "22", "17", "14"],
    ["remarks", "largest airline in the caribbean", "second largest airline in the caribbean", "operational since 1929"]
  ]
}
*/
statement : the remark on airline of dutch antilles express with fleet size over 4 is curacao second national carrier.
similar words link to columns :
the remark -> remarks
on airline -> airline
fleet size -> fleet size
column value link to columns :
dutch antilles -> country
4 -> fleet size
curacao second national carrier -> remarks
semantic sentence link to columns :
None
The answer is : f_col([airline, fleet size, remarks])

/*
{
  "table_caption": "cnbc prime 's the profit 200",
  "columns": ["year", "date", "driver", "team", "manufacturer", "laps", "-", "race time", "average speed (mph)"],
  "table_column_priority": [
    ["year", "1990", "1990", "1991"],
    ["date", "july 15", "october 14", "july 14"],
    ["driver", "tommy ellis", "rick mast", "kenny wallace"],
    ["team", "john jackson", "ag dillard motorsports", "rusty wallace racing"],
    ["manufacturer", "buick", "buick", "pontiac"],
    ["laps", "300", "250", "300"],
    ["-", "317.4 (510.805)", "264.5 (425.671)", "317.4 (510.805)"],
    ["race time", "3:41:58", "2:44:37", "2:54:38"],
    ["average speed (mph)", "85.797", "94.405", "109.093"]
  ]
}
*/
statemnet : on june 26th , 2010 kyle busch drove a total of 211.6 miles at an average speed of 110.673 miles per hour.
similar words link to columns :
drove -> driver
column value link to columns :
june 26th , 2010 -> date, year
a total of 211.6 miles -> -
semantic sentence link to columns :
kyle busch drove -> driver
an average speed of 110.673 miles per hour -> average speed (mph)
The answer is : f_col([year, date, driver, -, average speed (mph)])

/*
{
  "table_caption": "2000 ansett australia cup",
  "columns": ["home team", "home team score", "away team", "away team score", "ground", "crowd", "date"],
  "table_column_priority": [
    ["home team", "brisbane lions", "kangaroos", "richmond"],
    ["home team score", "13.6 (84)", "10.16 (76)", "11.16 (82)"],
    ["away team", "sydney", "richmond", "brisbane lions"],
    ["away team score", "17.10 (112)", "9.11 (65)", "15.9 (99)"],
    ["ground", "bundaberg rum stadium", "waverley park", "north hobart oval"],
    ["crowd", "8818", "16512", "4908"],
    ["date", "friday , 28 january", "friday , 28 january", "saturday , 5 february"]
  ]
}
*/
statement : sydney scored the same amount of points in the first game of the 2000 afl ansett australia cup as their opponent did in their second.
similar words link to columns :
scored -> away team score, home team score
column value link to columns :
sydney -> away team, home team
semantic sentence link to columns :
their opponent -> home team, away team
scored the same amount of points -> away team score, home team score
first game -> date
their second -> date
sydney scored -> home team, away team, home team score, away team score
The answer is : f_col([away team, home team, away team score, home team score, date])"""

######################################
##################
###
#
select_row_demo = """Using f_row() api to select relevant rows in the given table that support or oppose the statement.
Please use f_row([*]) to select all rows in the table.

/*
table caption : annual and quarterly financial data for nvidia and amd.
col : company | year | period | form | revenue | net income | operating income | assets | liabilities | cash
row 1 : nvidia | 2016 | fy | 10-k | 4130 | 440 | 496 | 7201 | 2783 | 733
row 2 : nvidia | 2016 | q1 | 10-q | 1103 | 137 | 151 | 7201 | 2783 | 1152
row 3 : nvidia | 2016 | q2 | 10-q | 2206 | 265 | 314 | 7201 | 2783 | 1152
row 4 : nvidia | 2016 | q3 | 10-q | 3431 | 437 | 528 | 7201 | 2783 | 1152
row 5 : nvidia | 2017 | fy | 10-k | 4682 | 631 | 759 | 7370 | 2814 | 1152
row 6 : nvidia | 2017 | q1 | 10-q | 1151 | 134 | 176 | 7370 | 2814 | 497
row 7 : nvidia | 2017 | q2 | 10-q | 2304 | 160 | 250 | 7370 | 2814 | 497
row 8 : nvidia | 2017 | q3 | 10-q | 3609 | 406 | 495 | 7370 | 2814 | 497
row 9 : nvidia | 2018 | fy | 10-k | 5010 | 614 | 747 | 9841 | 4048 | 497
row 10 : nvidia | 2018 | q1 | 10-q | 1305 | 208 | 245 | 9841 | 4048 | 596
row 11 : nvidia | 2018 | q2 | 10-q | 2733 | 469 | 561 | 9841 | 4048 | 596
row 12 : nvidia | 2018 | q3 | 10-q | 4737 | 1012 | 1201 | 9841 | 4048 | 596
row 13 : nvidia | 2019 | fy | 10-k | 2847 | 1666 | 1934 | 11241 | 3770 | 596
row 14 : nvidia | 2019 | q1 | 10-q | 1937 | 507 | 554 | 11241 | 3770 | 1766
row 15 : nvidia | 2019 | q2 | 10-q | 4167 | 1091 | 1242 | 11241 | 3770 | 1766
row 16 : nvidia | 2019 | q3 | 10-q | 6803 | 1928 | 2137 | 11241 | 3770 | 1766
row 17 : amd | 2016 | fy | 10-k | 4272 | -497 | -372 | 3321 | 2976 | 1264
row 18 : amd | 2016 | q1 | 10-q | 832 | -109 | -68 | 3321 | 2976 | 716
row 19 : amd | 2016 | q2 | 10-q | 1030 | 69 | -8 | 3321 | 2976 | 957
row 20 : amd | 2016 | q3 | 10-q | 1307 | -406 | -293 | 3321 | 2976 | 1258
row 21 : amd | 2017 | fy | 10-k | 5253 | 43 | 127 | 3540 | 2830 | 1185
row 22 : amd | 2017 | q1 | 10-q | 984 | -73 | -29 | 3540 | 2830 | 943
row 23 : amd | 2017 | q2 | 10-q | 1222 | 16 | 25 | 3540 | 2830 | 844
row 24 : amd | 2017 | q3 | 10-q | 1643 | 71 | 126 | 3540 | 2830 | 879
row 25 : amd | 2018 | fy | 10-k | 5329 | -33 | 127 | 3540 | 2830 | 1185
row 26 : amd | 2018 | q1 | 10-q | 1647 | 81 | 120 | 3540 | 2830 | 1040
row 27 : amd | 2018 | q2 | 10-q | 1756 | 116 | 153 | 3540 | 2830 | 983
row 28 : amd | 2018 | q3 | 10-q | 1653 | 102 | 150 | 3540 | 2830 | 1057
row 29 : amd | 2019 | fy | 10-k | 6475 | 337 | 631 | 6028 | 3201 | 1466
row 30 : amd | 2019 | q1 | 10-q | 1272 | 16 | 38 | 6028 | 3201 | 1207
row 31 : amd | 2019 | q2 | 10-q | 1531 | 35 | 59 | 6028 | 3201 | 1103
row 32 : amd | 2019 | q3 | 10-q | 1801 | 120 | 186 | 6028 | 3201 | 1125
*/


category 1 : simple cell lookup

statement : nvidia revenue in fiscal year 2017 according to the 10-k filing was 4682 million.

explain : the statement asks for one specific value. first, find the row where company is nvidia, year is 2017, period is fy, and form is 10-k. this corresponds to row 5. then select the revenue column.

The answer is : f_row([5])


category 2 : quarterly lookup

statement : nvidia net income in q2 of 2018 was 469 million.

explain : the statement asks for the net income value in a specific quarterly period. find the row where company is nvidia, year is 2018, period is q2, and form is 10-q. this corresponds to row 11. then select the net income column.

The answer is : f_row([11])


category 3 : comparison between two periods

statement : nvidia revenue was higher in q3 of 2018 than in q3 of 2017.

explain : the statement compares revenue from two different periods. we need the nvidia q3 2017 row and the nvidia q3 2018 row. these correspond to rows 8 and 12. compare the revenue values 3609 and 4737.

The answer is : f_row([8, 12])


category 4 : arithmetic difference

statement : the difference in nvidia net income between fiscal year 2016 and fiscal year 2017 was 191 million.

explain : the statement requires subtracting one table value from another. find the nvidia fy 2016 net income in row 1 and the nvidia fy 2017 net income in row 5. calculate 631 minus 440, which equals 191.

The answer is : f_row([1, 5])


category 5 : percentage change

statement : nvidia revenue increased by approximately 21.3 percent from fiscal year 2016 to fiscal year 2018.

explain : the statement requires calculating the percentage change between two annual revenue values. find the nvidia revenue for fiscal year 2016 in row 1 and fiscal year 2018 in row 9. calculate ((5010 - 4130) / 4130) * 100, which is approximately 21.3 percent.

The answer is : f_row([1, 9])


category 6 : aggregation sum

statement : the total annual net income of nvidia from fiscal year 2016 to fiscal year 2018 was 1685 million.

explain : the statement requires adding the annual net income values for 2016, 2017, and 2018. these values are found in rows 1, 5, and 9. calculate 440 + 631 + 614, which equals 1685.

The answer is : f_row([1, 5, 9])


category 7 : maximum value or argmax

statement : among nvidia annual 10-k records from 2016 to 2019, fiscal year 2018 had the highest revenue.

explain : the statement asks for the annual record with the highest revenue. compare the revenue values in all nvidia fy 10-k rows: rows 1, 5, 9, and 13. the values are 4130, 4682, 5010, and 2847. the highest value is 5010 in row 9.

The answer is : f_row([1, 5, 9, 13])


category 8 : threshold filtering

statement : nvidia reported quarterly revenue higher than 4000 million in q3 of 2018, q2 of 2019, and q3 of 2019.

explain : the statement requires checking all nvidia quarterly rows and selecting those where revenue is higher than 4000 million. row 12 has revenue of 4737, row 15 has revenue of 4167, and row 16 has revenue of 6803. these are the matching rows.

The answer is : f_row([12, 15, 16])


category 9 : multi-step reasoning

statement : among nvidia annual records from 2016 to 2019, fiscal year 2019 had the highest net income margin.

explain : the statement requires multiple steps. first, select all nvidia fy 10-k rows. second, calculate net income divided by revenue for each row. third, compare the resulting margins. the required annual rows are 1, 5, 9, and 13.

The answer is : f_row([1, 5, 9, 13])


category 10 : filter and lookup with where condition

statement : the company with revenue of 5329 million in fiscal year 2018 was amd.

explain : the statement asks for the company name where year is 2018, period is fy, form is 10-k, and revenue is 5329 million. apply these conditions to the table. the matching record is row 25. then select the company column.

The answer is : f_row([25])


category 11 : aggregation count

statement : nvidia had two quarterly records with revenue higher than 2000 million in 2018.

explain : the statement asks for the number of nvidia quarterly records in 2018 where revenue is higher than 2000 million. inspect rows 10, 11, and 12. row 10 has revenue of 1305 and does not match. rows 11 and 12 have revenue of 2733 and 4737 and both match. therefore, the count is two.

The answer is : f_row([11, 12])


category 12 : comparison between two companies

statement : amd had higher annual revenue than nvidia in fiscal year 2017.

explain : the statement compares the annual revenue of two companies in the same fiscal year. find the nvidia fy 2017 row and the amd fy 2017 row. these correspond to rows 5 and 21. compare revenues of 4682 and 5253. amd had the higher value.

The answer is : f_row([5, 21])"""

