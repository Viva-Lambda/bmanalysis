# bmanalysis
Scripts for analysing British Museum Collections

# Data

The data is collected from the online collection of [British Museum](https://www.britishmuseum.org/collection).

The search criteria is the following:

- Place: Egypt
- Production date: 700 BC - 330 BC

It yielded 15.104 items. Some of those items are determined to be duplicated by `pd.DataFrame`.
The elimination gave us the csv file, dully named as `EgyptBritishMuseum-2021-03-05CSVUnique.csv`.
The date 2021-03-05 is the date of retrieval of the data. 
You'll notice that some items have very vague production dates (5th C to 5 AD, etc), or completely
off the chart, like 980BC-780BC etc, I have no idea why.

I have added a very simple script that scrapes images from the given links in csv file as well.
You just need to create a `images` folder under the `data`. Beware that the ssl verification is set to `False` in `requests`. 
Feel free to correct it if you are really concerned about it.

# Dependencies

- pandas
- requests
- opencv
- scikit-learn
